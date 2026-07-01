import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import EvaluationTask, SubTaskResult
from ..config import settings
from .result_parser import get_parser

logger = logging.getLogger(__name__)


class EvaluationRunner:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(self, task: EvaluationTask) -> None:
        task.status = "执行中"
        await self.db.commit()

        try:
            dataset = task.dataset
            agent = task.agent
            model = task.model

            tasks = self._load_dataset_tasks(dataset.config_path)
            task.total_tasks = len(tasks)
            await self.db.commit()

            for dataset_task in tasks:
                subtask_id = dataset_task.get("task_id", str(dataset_task))
                await self._run_subtask(task, agent, model, dataset_task, subtask_id)

            resolved = sum(1 for sr in task.subtask_results if sr.result == "通过")
            task.resolved_tasks = resolved
            task.resolved_rate = (resolved / task.total_tasks * 100) if task.total_tasks > 0 else 0.0
            task.status = "已完成"
            task.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await self.db.commit()

        except Exception as exc:
            logger.exception("Evaluation task %s failed", task.id)
            task.status = "失败"
            task.error_message = str(exc)
            await self.db.commit()

    def _load_dataset_tasks(self, config_path: str) -> list:
        if not os.path.isabs(config_path):
            config_path = os.path.join(settings.datasets_config_path, config_path)
        if not os.path.exists(config_path):
            logger.warning("Dataset config not found: %s", config_path)
            return []
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("tasks", [])

    async def _run_subtask(self, task: EvaluationTask, agent, model, dataset_task: dict, subtask_id: str):
        result_enum = "失败"
        trajectory = None
        code_diff = None
        execution_time = None
        token_usage = None
        error_log = None

        with tempfile.TemporaryDirectory() as result_dir:
            try:
                exit_code = await asyncio.wait_for(
                    self._run_docker(agent, model, dataset_task, result_dir),
                    timeout=settings.task_timeout_seconds,
                )
                parser = get_parser(agent.agent_type)
                summary = parser.parse_summary(result_dir)
                trajectory = parser.parse_trajectory(result_dir)
                code_diff = parser.parse_diff(result_dir)
                result_enum = summary.get("result", "失败")
                execution_time = summary.get("execution_time")
                token_usage = summary.get("token_usage")
                error_log = summary.get("error_log")
            except asyncio.TimeoutError:
                result_enum = "超时"
                error_log = "任务执行超时"
            except Exception as exc:
                result_enum = "失败"
                error_log = str(exc)

        subtask = SubTaskResult(
            task_id=task.id,
            dataset_task_id=subtask_id,
            result=result_enum,
            trajectory=trajectory,
            code_diff=code_diff,
            execution_time=execution_time,
            token_usage=token_usage,
            error_log=error_log,
        )
        self.db.add(subtask)
        await self.db.commit()

    async def _run_docker(self, agent, model, dataset_task: dict, result_dir: str) -> int:
        env = {
            "MODEL_API_ENDPOINT": model.api_endpoint,
            "MODEL_IDENTIFIER": model.model_identifier,
            "TASK_ID": dataset_task.get("task_id", ""),
            "RESULT_DIR": "/results",
        }
        env_args = []
        for k, v in env.items():
            env_args += ["-e", f"{k}={v}"]

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{result_dir}:/results",
            *env_args,
            agent.docker_image,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _stdout, _stderr = await proc.communicate()
        return proc.returncode
