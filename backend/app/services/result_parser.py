import json
import os
from abc import ABC, abstractmethod
from typing import Optional


class BaseResultParser(ABC):
    @abstractmethod
    def parse_trajectory(self, result_dir: str) -> Optional[dict]:
        ...

    @abstractmethod
    def parse_diff(self, result_dir: str) -> Optional[str]:
        ...

    @abstractmethod
    def parse_summary(self, result_dir: str) -> dict:
        """Return dict with: result, execution_time, token_usage, error_log"""
        ...


class ClaudeCodeResultParser(BaseResultParser):
    def parse_trajectory(self, result_dir: str) -> Optional[dict]:
        traj_file = os.path.join(result_dir, "trajectory.json")
        if not os.path.exists(traj_file):
            # Try .traj.json extension
            for f in os.listdir(result_dir) if os.path.isdir(result_dir) else []:
                if f.endswith(".traj.json"):
                    traj_file = os.path.join(result_dir, f)
                    break
        if not os.path.exists(traj_file):
            return None
        try:
            with open(traj_file, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except Exception:
            return None

    def parse_diff(self, result_dir: str) -> Optional[str]:
        diff_file = os.path.join(result_dir, "patch.diff")
        if not os.path.exists(diff_file):
            diff_file = os.path.join(result_dir, "result.diff")
        if not os.path.exists(diff_file):
            return None
        try:
            with open(diff_file, "r", encoding="utf-8") as fp:
                return fp.read()
        except Exception:
            return None

    def parse_summary(self, result_dir: str) -> dict:
        summary = {
            "result": "失败",
            "execution_time": None,
            "token_usage": None,
            "error_log": None,
        }
        summary_file = os.path.join(result_dir, "summary.json")
        if os.path.exists(summary_file):
            try:
                with open(summary_file, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                summary["result"] = data.get("result", "失败")
                summary["execution_time"] = data.get("execution_time")
                summary["token_usage"] = data.get("token_usage")
                summary["error_log"] = data.get("error_log")
            except Exception:
                pass
        error_file = os.path.join(result_dir, "error.log")
        if os.path.exists(error_file):
            try:
                with open(error_file, "r", encoding="utf-8") as fp:
                    summary["error_log"] = fp.read()
            except Exception:
                pass
        return summary


RESULT_PARSERS = {
    "claude-code": ClaudeCodeResultParser(),
    "default": ClaudeCodeResultParser(),
}


def get_parser(agent_type: str) -> BaseResultParser:
    return RESULT_PARSERS.get(agent_type, RESULT_PARSERS["default"])
