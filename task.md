# Code Leaderboard SWE-Bench 实现计划

> 任务标题使用复选框（`### [ ]`）语法来跟踪进度，步骤使用（`-`）语法记录详细操作。

**目标：** 构建一个评测平台，支持调度多种 Agent+模型组合在 Multi-SWE-Bench Java 上执行代码修复评测，收集结果并展示排行榜和轨迹分析。

---

## 1. 职责边界
- 禁止为了完成本次需求进行无关重构。
- 禁止修改未列入计划的核心文件；如必须修改，先在任务回传中说明原因。
- 遵循现有代码风格、错误码风格、日志风格和测试组织方式。
- 如果发现更合适的文件归属，必须说明依据，不得直接大规模迁移。

---

## 2. 文件职责清单

| 文件路径 | 职责 |
|----------|------|
| `backend/app/main.py` | FastAPI 应用入口，路由注册 |
| `backend/app/models.py` | SQLAlchemy ORM 模型定义 |
| `backend/app/schemas.py` | Pydantic 请求/响应 Schema |
| `backend/app/database.py` | 数据库连接和会话管理 |
| `backend/app/api/leaderboard.py` | 排行榜查询 API |
| `backend/app/api/evaluations.py` | 评测任务 CRUD API |
| `backend/app/api/models.py` | 模型管理 API |
| `backend/app/api/agents.py` | Agent 管理 API |
| `backend/app/api/datasets.py` | 数据集管理 API |
| `backend/app/api/auth.py` | 认证 API |
| `backend/app/services/evaluator.py` | 评测任务调度和执行逻辑 |
| `backend/app/services/result_parser.py` | Agent 结果解析器基类和实现 |
| `backend/app/workers.py` | Celery Worker 入口和任务定义 |
| `backend/app/config.py` | 应用配置 |
| `backend/alembic/` | 数据库迁移 |
| `backend/tests/` | 后端测试 |
| `frontend/src/pages/Leaderboard.tsx` | 排行榜页面 |
| `frontend/src/pages/EvaluationDetail.tsx` | 评测详情页 |
| `frontend/src/pages/SubTaskDetail.tsx` | 子任务轨迹详情页 |
| `frontend/src/pages/Models.tsx` | 模型管理页 |
| `frontend/src/pages/Agents.tsx` | Agent 管理页 |
| `frontend/src/pages/Datasets.tsx` | 数据集页 |
| `frontend/src/api/client.ts` | API 客户端 |
| `docker-compose.yml` | 开发环境编排 |
| `Dockerfile.backend` | 后端 Docker 镜像 |
| `Dockerfile.frontend` | 前端 Docker 镜像 |

---

### [x] 任务 1：项目脚手架与数据模型

**任务目标：** 搭建后端项目结构，定义数据库模型和 Schema，完成数据库迁移，确保所有数据结构可创建和查询。

**依据：**
- 规格：`spec.md` 2.1-2.5 数据约束变更
- 设计：`design.md` 3.1 新增数据结构

**涉及文件：**
| 文件名 | 操作 | 说明 |
|--------|------|------|
| `backend/app/main.py` | 创建 | FastAPI 应用入口 |
| `backend/app/models.py` | 创建 | ORM 模型定义 |
| `backend/app/schemas.py` | 创建 | Pydantic Schema |
| `backend/app/database.py` | 创建 | 数据库连接管理 |
| `backend/app/config.py` | 创建 | 应用配置 |
| `backend/requirements.txt` | 创建 | Python 依赖 |
| `backend/alembic/` | 创建 | 数据库迁移 |
| `backend/tests/test_models.py` | 创建 | 模型测试 |

**修改入口：**
- `backend/app/models.py` 中所有 ORM 类

**执行步骤：**
- **步骤 1：读取上下文**
   - 读取 spec.md 2.1-2.5 数据约束、design.md 3.1 数据结构定义

- **步骤 2：编写失败的测试**：`backend/tests/test_models.py`
   - 测试 Model、Agent、Dataset、EvaluationTask、SubTaskResult 的创建和查询
   - 测试枚举约束（status、result 字段仅接受合法值）
   - 测试唯一约束（模型名称、Agent名称、数据集名称不可重复）

- **步骤 3：运行测试验证失败**：`cd backend && python -m pytest tests/test_models.py -v`
   - 预期：FAIL，原因为 `模块不存在`

- **步骤 4：按实现约束完成最小实现**
   - 创建 `backend/` 目录结构
<<<<<<< HEAD
   - 创建 `requirements.txt`（fastapi, uvicorn, sqlalchemy, alembic, psycopg2-binary, pydantic, celery, redis）
=======
   - 创建 `requirements.txt`（fastapi, uvicorn, sqlalchemy, alembic, pydantic, celery, redis）
>>>>>>> 83479ff8 (feat: add full-stack code leaderboard platform)
   - 创建 `backend/app/config.py`：从环境变量读取数据库URL、Redis URL、最大并发数等配置
   - 创建 `backend/app/database.py`：SQLAlchemy async engine、sessionmaker、Base
   - 创建 `backend/app/models.py`：定义 Model、Agent、Dataset、EvaluationTask、SubTaskResult 五个 ORM 模型，字段类型和约束与 design.md 3.1 一致
   - 创建 `backend/app/schemas.py`：为每个模型定义 Pydantic Schema（Create/Response）
   - 创建 `backend/app/main.py`：FastAPI app 实例，注册路由占位
   - 初始化 alembic 并生成初始迁移

- **步骤 5：运行测试验证通过**：`cd backend && python -m pytest tests/test_models.py -v`
   - 预期：PASS

- **步骤 6：Commit**
   ```bash
   git add backend/
   git commit -m "feat: scaffold backend project with data models and schemas"
   ```

---

### [x] 任务 2：模型/Agent/数据集管理 API

**任务目标：** 实现模型、Agent、数据集的 CRUD API，支持注册、列表查询，为后续评测任务提供基础数据。

**依据：**
- 规格：`spec.md` 1.3 模型与Agent管理、1.4 数据集管理
- 设计：`design.md` 4.1 GET/POST /api/models, /api/agents, /api/datasets, GET /api/datasets/{id}/tasks

**涉及文件：**
| 文件名 | 操作 | 说明 |
|--------|------|------|
| `backend/app/api/models.py` | 创建 | 模型管理 API |
| `backend/app/api/agents.py` | 创建 | Agent 管理 API |
| `backend/app/api/datasets.py` | 创建 | 数据集管理 API |
| `backend/app/api/auth.py` | 创建 | 简易 Token 认证 |
| `backend/app/main.py` | 修改 | 注册新路由 |
| `backend/tests/test_api_models.py` | 创建 | 模型 API 测试 |
| `backend/tests/test_api_agents.py` | 创建 | Agent API 测试 |
| `backend/tests/test_api_datasets.py` | 创建 | 数据集 API 测试 |

**修改入口：**
- `backend/app/api/models.py` 中 `register_model`, `list_models`
- `backend/app/api/agents.py` 中 `register_agent`, `list_agents`
- `backend/app/api/datasets.py` 中 `list_datasets`, `list_dataset_tasks`
- `backend/app/api/auth.py` 中 `verify_token`

**执行步骤：**
- **步骤 1：读取上下文**
   - 读取 spec.md 1.3-1.4、design.md 4.1 中模型/Agent/数据集相关接口定义

- **步骤 2：编写失败的测试**：`backend/tests/test_api_models.py`, `test_api_agents.py`, `test_api_datasets.py`
   - 测试 POST /api/models 注册模型，返回201和模型详情
   - 测试 POST /api/models 重复名称返回409
   - 测试 GET /api/models 返回模型列表
   - 测试 POST /api/agents 注册Agent，返回201
   - 测试 GET /api/agents 返回Agent列表
   - 测试 GET /api/datasets 返回数据集列表
   - 测试 GET /api/datasets/{id}/tasks 返回任务列表
   - 测试未认证用户POST操作返回401

- **步骤 3：运行测试验证失败**：`cd backend && python -m pytest tests/test_api_models.py tests/test_api_agents.py tests/test_api_datasets.py -v`
   - 预期：FAIL，原因为 `API端点不存在`

- **步骤 4：按实现约束完成最小实现**
   - 创建 `backend/app/api/auth.py`：实现基于 API Token 的简易认证中间件，从配置读取允许的 Token 列表
   - 创建 `backend/app/api/models.py`：POST /api/models（需认证）、GET /api/models（公开）
   - 创建 `backend/app/api/agents.py`：POST /api/agents（需认证）、GET /api/agents（公开）
   - 创建 `backend/app/api/datasets.py`：GET /api/datasets（公开）、GET /api/datasets/{id}/tasks（公开）
   - 修改 `backend/app/main.py`：注册以上路由

- **步骤 5：运行测试验证通过**：`cd backend && python -m pytest tests/test_api_models.py tests/test_api_agents.py tests/test_api_datasets.py -v`
   - 预期：PASS

- **步骤 6：Commit**
   ```bash
   git add backend/app/api/ backend/app/main.py backend/tests/
   git commit -m "feat: add model/agent/dataset management APIs with auth"
   ```

---

### [x] 任务 3：评测任务调度与执行

**任务目标：** 实现评测任务的创建、Celery 异步调度、Docker 沙箱执行、结果收集和解析的完整流程。

**依据：**
- 规格：`spec.md` 1.2 评测任务调度
- 设计：`design.md` 2.1-2.3 设计决策、5.1 评测任务执行流程

**涉及文件：**
| 文件名 | 操作 | 说明 |
|--------|------|------|
| `backend/app/api/evaluations.py` | 创建 | 评测任务 API |
| `backend/app/services/evaluator.py` | 创建 | 评测调度和执行逻辑 |
| `backend/app/services/result_parser.py` | 创建 | Agent 结果解析器 |
| `backend/app/workers.py` | 创建 | Celery Worker 定义 |
| `backend/app/main.py` | 修改 | 注册新路由 |
| `backend/tests/test_evaluations.py` | 创建 | 评测 API 和流程测试 |

**修改入口：**
- `backend/app/api/evaluations.py` 中 `create_evaluation`, `get_evaluation`, `get_subtask_detail`
- `backend/app/workers.py` 中 `run_evaluation` Celery task
- `backend/app/services/evaluator.py` 中 `EvaluationRunner`
- `backend/app/services/result_parser.py` 中 `BaseResultParser`, `ClaudeCodeResultParser`

**执行步骤：**
- **步骤 1：读取上下文**
   - 读取 spec.md 1.2 全部场景、design.md 5.1 执行流程

- **步骤 2：编写失败的测试**：`backend/tests/test_evaluations.py`
   - 测试 POST /api/evaluations 创建评测任务，返回 task_id 和 status="排队中"
   - 测试 GET /api/evaluations/{task_id} 返回任务详情和进度
   - 测试 GET /api/evaluations/{task_id}/subtasks/{subtask_id} 返回轨迹详情
   - 测试评测任务完成后解决率计算正确
   - 测试评测任务失败时状态更新为"失败"
   - 测试未认证用户创建评测返回401

- **步骤 3：运行测试验证失败**：`cd backend && python -m pytest tests/test_evaluations.py -v`
   - 预期：FAIL，原因为 `API端点不存在`

- **步骤 4：按实现约束完成最小实现**
   - 创建 `backend/app/services/result_parser.py`：定义 `BaseResultParser` 抽象基类（parse_trajectory, parse_diff, parse_summary 方法），实现 `ClaudeCodeResultParser` 解析 .traj.json 格式
   - 创建 `backend/app/services/evaluator.py`：`EvaluationRunner` 类，实现 run 方法——遍历数据集子任务，启动 Docker 容器执行 Agent，收集 Volume 中的结果文件，调用对应 ResultParser 解析，创建 SubTaskResult 记录，计算解决率
   - 创建 `backend/app/workers.py`：定义 Celery app（broker=Redis），定义 `run_evaluation` task 调用 EvaluationRunner
   - 创建 `backend/app/api/evaluations.py`：POST /api/evaluations（需认证，创建任务并发送 Celery task）、GET /api/evaluations/{task_id}（公开）、GET /api/evaluations/{task_id}/subtasks/{subtask_id}（公开）
   - 修改 `backend/app/main.py`：注册评测路由

- **步骤 5：运行测试验证通过**：`cd backend && python -m pytest tests/test_evaluations.py -v`
   - 预期：PASS

- **步骤 6：Commit**
   ```bash
   git add backend/app/api/evaluations.py backend/app/services/ backend/app/workers.py backend/app/main.py backend/tests/test_evaluations.py
   git commit -m "feat: add evaluation task scheduling with Celery and Docker sandbox"
   ```

---

### [x] 任务 4：排行榜 API

**任务目标：** 实现排行榜查询 API，支持按模型/Agent/数据集筛选，返回按解决率降序排列的排名数据。

**依据：**
- 规格：`spec.md` 1.1 排行榜展示
- 设计：`design.md` 4.1 GET /api/leaderboard、5.2 排行榜查询流程

**涉及文件：**
| 文件名 | 操作 | 说明 |
|--------|------|------|
| `backend/app/api/leaderboard.py` | 创建 | 排行榜查询 API |
| `backend/app/main.py` | 修改 | 注册新路由 |
| `backend/tests/test_leaderboard.py` | 创建 | 排行榜 API 测试 |

**修改入口：**
- `backend/app/api/leaderboard.py` 中 `get_leaderboard`

**执行步骤：**
- **步骤 1：读取上下文**
   - 读取 spec.md 1.1 全部场景、design.md 4.1 leaderboard 接口

- **步骤 2：编写失败的测试**：`backend/tests/test_leaderboard.py`
   - 测试 GET /api/leaderboard 返回按解决率降序排列的排名
   - 测试 GET /api/leaderboard?model=GLM-5.2 按模型筛选
   - 测试 GET /api/leaderboard?agent=Claude Code 按Agent筛选
   - 测试 GET /api/leaderboard?dataset=Multi-SWE-Bench-Java 按数据集筛选
   - 测试无评测数据时返回空列表

- **步骤 3：运行测试验证失败**：`cd backend && python -m pytest tests/test_leaderboard.py -v`
   - 预期：FAIL，原因为 `API端点不存在`

- **步骤 4：按实现约束完成最小实现**
   - 创建 `backend/app/api/leaderboard.py`：GET /api/leaderboard，查询 EvaluationTask 中 status="已完成" 的记录，按 model_id + agent_id + dataset_id 分组取最新，计算排名，支持 query 参数筛选
   - 修改 `backend/app/main.py`：注册排行榜路由

- **步骤 5：运行测试验证通过**：`cd backend && python -m pytest tests/test_leaderboard.py -v`
   - 预期：PASS

- **步骤 6：Commit**
   ```bash
   git add backend/app/api/leaderboard.py backend/app/main.py backend/tests/test_leaderboard.py
   git commit -m "feat: add leaderboard API with filtering support"
   ```

---

### [x] 任务 5：前端页面开发

**任务目标：** 实现前端所有页面——排行榜、评测详情、子任务轨迹、模型/Agent/数据集管理，与后端 API 对接。

**依据：**
- 规格：`spec.md` 1.1-1.4 全部场景
- 设计：`design.md` 4.1 全部接口、5.2-5.3 查询流程

**涉及文件：**
| 文件名 | 操作 | 说明 |
|--------|------|------|
| `frontend/` | 创建 | 整个前端项目 |
| `frontend/src/pages/Leaderboard.tsx` | 创建 | 排行榜页面 |
| `frontend/src/pages/EvaluationDetail.tsx` | 创建 | 评测详情页 |
| `frontend/src/pages/SubTaskDetail.tsx` | 创建 | 子任务轨迹详情页 |
| `frontend/src/pages/Models.tsx` | 创建 | 模型管理页 |
| `frontend/src/pages/Agents.tsx` | 创建 | Agent 管理页 |
| `frontend/src/pages/Datasets.tsx` | 创建 | 数据集页 |
| `frontend/src/api/client.ts` | 创建 | API 客户端 |
| `frontend/src/App.tsx` | 创建 | 路由配置 |

**修改入口：**
- `frontend/src/App.tsx` 路由定义

**执行步骤：**
- **步骤 1：读取上下文**
   - 读取 spec.md 1.1-1.4、design.md 4.1 全部接口定义

- **步骤 2：编写失败的测试**：`frontend/src/__tests__/` 目录下各页面组件测试
   - 测试 Leaderboard 组件渲染排名表格
   - 测试 EvaluationDetail 组件渲染子任务列表
   - 测试 SubTaskDetail 组件渲染轨迹和 diff
   - 测试 Models/Agents/Datasets 组件渲染管理表单

- **步骤 3：运行测试验证失败**：`cd frontend && npm test`
   - 预期：FAIL，原因为 `组件不存在`

- **步骤 4：按实现约束完成最小实现**
   - 使用 `create-react-app --template typescript` 初始化前端项目
   - 安装依赖：antd, react-router-dom, axios, react-diff-viewer-continued
   - 创建 `frontend/src/api/client.ts`：封装 axios 实例，定义所有 API 调用函数
   - 创建 `frontend/src/pages/Leaderboard.tsx`：表格展示排名，支持筛选（模型/Agent/数据集下拉），点击行跳转评测详情
   - 创建 `frontend/src/pages/EvaluationDetail.tsx`：展示评测任务概览（状态、进度、解决率）和子任务结果列表，点击子任务跳转轨迹详情
   - 创建 `frontend/src/pages/SubTaskDetail.tsx`：展示 Agent 执行轨迹（步骤时间线）、代码 diff（react-diff-viewer）、执行耗时和 token 消耗
   - 创建 `frontend/src/pages/Models.tsx`：模型列表 + 注册表单（需认证）
   - 创建 `frontend/src/pages/Agents.tsx`：Agent 列表 + 注册表单（需认证）
   - 创建 `frontend/src/pages/Datasets.tsx`：数据集列表 + 任务列表
   - 创建 `frontend/src/App.tsx`：React Router 配置，导航栏

- **步骤 5：运行测试验证通过**：`cd frontend && npm test`
   - 预期：PASS

- **步骤 6：Commit**
   ```bash
   git add frontend/
   git commit -m "feat: add frontend pages for leaderboard, evaluation details, and management"
   ```

---

### [x] 任务 6：Docker 编排与集成验证

<<<<<<< HEAD
**任务目标：** 创建 Docker Compose 编排文件，将前后端、Redis、PostgreSQL 打包为可一键启动的开发环境，执行端到端集成验证。
=======
**任务目标：** 创建 Docker Compose 编排文件，将前后端、Redis 打包为可一键启动的开发环境（数据库使用 SQLite 文件，无需独立服务），执行端到端集成验证。
>>>>>>> 83479ff8 (feat: add full-stack code leaderboard platform)

**依据：**
- 设计：`design.md` 2.1-2.2 设计决策

**涉及文件：**
| 文件名 | 操作 | 说明 |
|--------|------|------|
| `docker-compose.yml` | 创建 | 开发环境编排 |
| `Dockerfile.backend` | 创建 | 后端镜像 |
| `Dockerfile.frontend` | 创建 | 前端镜像 |
| `backend/tests/test_integration.py` | 创建 | 集成测试 |

**修改入口：**
- `docker-compose.yml` 服务定义

**执行步骤：**
- **步骤 1：读取上下文**
   - 读取 design.md 2.1-2.2 中 Docker 和 Celery 相关决策

- **步骤 2：编写失败的测试**：`backend/tests/test_integration.py`
   - 测试完整的评测流程：创建模型 → 创建Agent → 创建数据集 → 创建评测任务 → 查看排行榜
   - 测试排行榜筛选功能
   - 测试轨迹查看功能

- **步骤 3：运行测试验证失败**：`cd backend && python -m pytest tests/test_integration.py -v`
   - 预期：FAIL，原因为 `服务未启动`

- **步骤 4：按实现约束完成最小实现**
   - 创建 `Dockerfile.backend`：基于 python:3.11，安装依赖，启动 FastAPI + Celery worker
   - 创建 `Dockerfile.frontend`：基于 node:20，构建并使用 nginx 服务静态文件
<<<<<<< HEAD
   - 创建 `docker-compose.yml`：定义 postgres、redis、backend-api、backend-worker、frontend 五个服务
=======
   - 创建 `docker-compose.yml`：定义 redis、backend-api、backend-worker、frontend 四个服务（SQLite 数据库以文件形式挂载，无需独立容器）
>>>>>>> 83479ff8 (feat: add full-stack code leaderboard platform)
   - 配置 Volume 挂载用于 Agent 执行结果收集
   - 配置环境变量传递数据库URL、Redis URL、认证Token等

- **步骤 5：运行测试验证通过**：`docker-compose up -d && cd backend && python -m pytest tests/test_integration.py -v`
   - 预期：PASS

- **步骤 6：Commit**
   ```bash
   git add docker-compose.yml Dockerfile.backend Dockerfile.frontend backend/tests/test_integration.py
   git commit -m "feat: add Docker Compose orchestration and integration tests"
   ```
