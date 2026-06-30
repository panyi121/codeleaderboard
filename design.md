## 1. 设计背景

### 1.1 设计目标

构建一个 Code Leaderboard 评测平台，支持调度多种 Agent（Claude Code、OpenCode、CodeX 等）配合多种开源模型（GLM-5.2、MiniMax、DeepSeek 等）在 Multi-SWE-Bench Java 数据集上执行代码修复评测，收集结果并展示排行榜和详细轨迹分析。

### 1.2 设计约束

1. 部署在华为内部服务器，Agent 执行环境为 Docker 沙箱
2. 技术栈：React 前端 + FastAPI 后端 + Celery 任务队列 + SQLite 数据库
3. MVP 阶段优先核心流程，后续迭代扩展功能
4. 查看排行榜无需登录，触发评测和写操作需要鉴权
5. Agent 执行需要调用模型 API，需支持不同模型的 API 格式差异

### 1.3 非目标

- 不支持实时流式展示 Agent 执行过程（MVP 阶段仅支持执行完成后查看结果）
- 不支持自定义评测数据集上传（MVP 阶段数据集通过配置文件管理）
- 不支持多语言数据集（MVP 仅 Multi-SWE-Bench Java，架构预留扩展）
- 不支持评测结果的人工复核流程

---

## 2. 设计决策

### 2.1 Agent 执行沙箱方案

**决策**：使用 Docker 容器作为 Agent 执行沙箱，每个评测子任务启动独立容器

**背景**：Agent 执行需要隔离环境，防止对宿主系统的副作用，同时需要可重复性

**方案对比**：

| 方案 | 优点 | 缺点 |
|------|------|------|
| Docker容器（采纳） | 隔离性好、可重复、镜像标准化 | 启动开销、需要Docker守护进程 |
| 子进程隔离 | 启动快、无额外依赖 | 隔离性差、安全风险 |
| K8s Pod | 编排能力强、适合大规模 | 架构复杂、MVP过度设计 |

**理由**：
- Docker 是 Agent 评测的事实标准（ais_bench、SWE-agent 均使用 Docker）
- 镜像可预构建，包含 Agent 运行所需的所有依赖
- 容器销毁后环境完全清理，保证评测隔离性

### 2.2 任务调度方案

**决策**：使用 Celery + Redis 作为任务队列

**背景**：评测任务是长时间运行的异步任务，需要排队、并发控制、失败重试

**方案对比**：

| 方案 | 优点 | 缺点 |
|------|------|------|
| Celery + Redis（采纳） | 成熟稳定、支持优先级/重试/限流 | 引入Redis依赖 |
| ARQ + Redis | 轻量、原生asyncio | 社区较小、功能较少 |
| Python asyncio.Queue | 无额外依赖 | 不支持持久化、进程重启丢任务 |

**理由**：
- Celery 是 Python 生态最成熟的任务队列，社区支持好
- 支持任务优先级、失败重试、并发限制（worker concurrency）
- Redis 同时作为 Celery broker 和结果后端，部署简单

### 2.3 评测结果收集方案

**决策**：Agent 执行完成后，通过挂载卷（Docker Volume）收集结果文件，后端解析入库

**背景**：Agent 执行会产生轨迹文件（.traj.json）、代码 diff、日志等，需要统一收集和解析

**理由**：
- Docker Volume 是容器与宿主机共享文件的标准方式
- Agent 执行完成后，后端从 Volume 读取结果文件并解析
- 不同 Agent 的输出格式不同，需要为每种 Agent 实现结果解析器

### 2.4 前端方案

**决策**：React + Ant Design 组件库

**背景**：需要展示排行榜表格、轨迹详情、代码 diff 等复杂 UI

**理由**：
- React 生态成熟，组件丰富
- Ant Design 提供开箱即用的表格、表单、代码展示组件
- 代码 diff 展示可使用 react-diff-viewer 等成熟组件

---

## 3. 模块/数据变更

### 3.1 新增数据结构

#### Model（模型）

| 字段/属性 | 类型 | 约束 | 说明 |
|------------|------|------|------|
| id | UUID | PK, 自动生成 | 主键 |
| name | VARCHAR(128) | UNIQUE, NOT NULL | 模型名称 |
| model_type | ENUM | NOT NULL | 开源/闭源 |
| api_endpoint | VARCHAR(512) | NOT NULL | API端点URL |
| model_identifier | VARCHAR(128) | NOT NULL | API调用标识符 |
| status | ENUM | NOT NULL, DEFAULT='可用' | 可用/不可用 |
| created_at | TIMESTAMP | NOT NULL, 自动生成 | 创建时间 |

#### Agent（评测Agent）

| 字段/属性 | 类型 | 约束 | 说明 |
|------------|------|------|------|
| id | UUID | PK, 自动生成 | 主键 |
| name | VARCHAR(128) | UNIQUE, NOT NULL | Agent名称 |
| agent_type | VARCHAR(64) | NOT NULL | Agent类型标识 |
| docker_image | VARCHAR(512) | NOT NULL | Docker镜像地址 |
| status | ENUM | NOT NULL, DEFAULT='可用' | 可用/不可用 |
| created_at | TIMESTAMP | NOT NULL, 自动生成 | 创建时间 |

#### Dataset（数据集）

| 字段/属性 | 类型 | 约束 | 说明 |
|------------|------|------|------|
| id | UUID | PK, 自动生成 | 主键 |
| name | VARCHAR(128) | UNIQUE, NOT NULL | 数据集名称 |
| language | VARCHAR(32) | NOT NULL | 编程语言（含"多语言"） |
| task_count | INTEGER | NOT NULL, DEFAULT=0 | 任务总数（导入前为0） |
| source_type | ENUM | NOT NULL, DEFAULT='本地' | 内置/huggingface/本地 |
| hf_repo_id | VARCHAR(256) | NULL | HuggingFace repo ID，如 `princeton-nlp/SWE-bench` |
| import_status | ENUM | NOT NULL, DEFAULT='就绪' | 就绪/导入中/解析失败 |
| config_path | VARCHAR(512) | NULL | 本地配置文件路径（非HF来源时使用） |
| description | TEXT | | 描述 |
| created_at | TIMESTAMP | NOT NULL, 自动生成 | 创建时间 |

#### EvaluationTask（评测任务）

| 字段/属性 | 类型 | 约束 | 说明 |
|------------|------|------|------|
| id | UUID | PK, 自动生成 | 主键 |
| model_id | UUID | FK -> Model, NOT NULL | 关联模型 |
| agent_id | UUID | FK -> Agent, NOT NULL | 关联Agent |
| dataset_id | UUID | FK -> Dataset, NOT NULL | 关联数据集 |
| status | ENUM | NOT NULL, DEFAULT='排队中' | 排队中/执行中/已完成/失败 |
| resolved_rate | FLOAT | NULL | 解决率(0-100) |
| total_tasks | INTEGER | NOT NULL | 总子任务数 |
| resolved_tasks | INTEGER | DEFAULT=0 | 已解决子任务数 |
| error_message | TEXT | NULL | 失败原因 |
| created_at | TIMESTAMP | NOT NULL, 自动生成 | 创建时间 |
| completed_at | TIMESTAMP | NULL | 完成时间 |
| created_by | VARCHAR(128) | NOT NULL | 创建者 |

#### SubTaskResult（子任务结果）

| 字段/属性 | 类型 | 约束 | 说明 |
|------------|------|------|------|
| id | UUID | PK, 自动生成 | 主键 |
| task_id | UUID | FK -> EvaluationTask, NOT NULL | 所属评测任务 |
| dataset_task_id | VARCHAR(128) | NOT NULL | 数据集中的任务标识 |
| result | ENUM | NOT NULL | 通过/失败/超时/未执行 |
| trajectory | JSON | NULL | Agent执行轨迹 |
| code_diff | TEXT | NULL | 代码变更差异 |
| execution_time | FLOAT | NULL | 执行耗时(秒) |
| token_usage | INTEGER | NULL | Token消耗量 |
| error_log | TEXT | NULL | 错误日志 |

---

## 4. 接口变更

### 4.1 新增接口

#### GET /api/leaderboard

**输入**：

```
Query参数:
  model: string (可选) - 按模型名称筛选
  agent: string (可选) - 按Agent名称筛选
  dataset: string (可选) - 按数据集名称筛选
```

**输出**：

```
{
  "rankings": [
    {
      "rank": 1,
      "model_name": "GLM-5.2",
      "agent_name": "Claude Code",
      "dataset_name": "Multi-SWE-Bench-Java",
      "resolved_rate": 43.75,
      "total_tasks": 80,
      "resolved_tasks": 35,
      "task_id": "uuid"
    }
  ]
}
```

#### POST /api/evaluations

**输入**：

```
{
  "model_id": "uuid",
  "agent_id": "uuid",
  "dataset_id": "uuid"
}
```

**输出**：

```
{
  "task_id": "uuid",
  "status": "排队中",
  "message": "评测任务已创建"
}
```

**错误处理**：

| 错误场景 | 错误码/状态 | 说明 |
|----------|------------|------|
| 模型/Agent/数据集不存在 | 404 | 指定的资源不存在 |
| 模型或Agent不可用 | 400 | 模型或Agent状态为不可用 |
| 未认证 | 401 | 需要登录 |

#### GET /api/evaluations/{task_id}

**输入**：

```
Path参数: task_id (UUID)
```

**输出**：

```
{
  "task_id": "uuid",
  "model_name": "GLM-5.2",
  "agent_name": "Claude Code",
  "dataset_name": "Multi-SWE-Bench-Java",
  "status": "执行中",
  "progress": "15/80",
  "resolved_rate": null,
  "subtask_results": [
    {
      "dataset_task_id": "task-001",
      "result": "通过",
      "execution_time": 120.5,
      "token_usage": 15000
    }
  ],
  "created_at": "2026-06-27T10:00:00Z",
  "completed_at": null
}
```

#### GET /api/evaluations/{task_id}/subtasks/{subtask_id}

**输入**：

```
Path参数: task_id (UUID), subtask_id (UUID)
```

**输出**：

```
{
  "dataset_task_id": "task-001",
  "result": "通过",
  "trajectory": { ... },
  "code_diff": "diff --git a/...",
  "execution_time": 120.5,
  "token_usage": 15000,
  "error_log": null
}
```

#### GET /api/models

**输出**：

```
{
  "models": [
    {
      "id": "uuid",
      "name": "GLM-5.2",
      "model_type": "开源",
      "api_endpoint": "https://...",
      "model_identifier": "glm-5.2",
      "status": "可用"
    }
  ]
}
```

#### POST /api/models

**输入**：

```
{
  "name": "GLM-5.2",
  "model_type": "开源",
  "api_endpoint": "https://...",
  "model_identifier": "glm-5.2"
}
```

**错误处理**：

| 错误场景 | 错误码/状态 | 说明 |
|----------|------------|------|
| 名称重复 | 409 | 模型名称已存在 |
| 未认证 | 401 | 需要登录 |

#### GET /api/agents

**输出**：

```
{
  "agents": [
    {
      "id": "uuid",
      "name": "Claude Code",
      "agent_type": "claude-code",
      "docker_image": "claude-code:latest",
      "status": "可用"
    }
  ]
}
```

#### POST /api/agents

**输入**：

```
{
  "name": "Claude Code",
  "agent_type": "claude-code",
  "docker_image": "claude-code:latest"
}
```

#### GET /api/datasets

**输出**：

```
{
  "datasets": [
    {
      "id": "uuid",
      "name": "Multi-SWE-Bench-Java",
      "language": "Java",
      "task_count": 80,
      "description": "..."
    }
  ]
}
```

#### POST /api/datasets/import

**说明**：通过 HuggingFace 链接异步导入数据集（需认证）

**输入**：

```
{
  "hf_url": "https://huggingface.co/datasets/princeton-nlp/SWE-bench",
  "name": "SWE-bench",          // 可选，默认从 repo ID 推断
  "language": "Python",         // 可选，默认从数据集元信息推断
  "description": "..."          // 可选
}
```

**输出**：

```
{
  "dataset_id": "uuid",
  "name": "SWE-bench",
  "import_status": "导入中",
  "message": "数据集导入任务已创建，请稍后刷新查看"
}
```

**错误处理**：

| 错误场景 | 状态码 | 说明 |
|----------|--------|------|
| URL 格式非法 | 422 | 非 HuggingFace 域名或缺少 repo 路径 |
| 数据集名称重复 | 409 | 同名数据集已存在 |
| 未认证 | 401 | 需要登录 |

#### POST /api/datasets/sync-builtin

**说明**：一键同步所有内置主流数据集（需认证），已存在的跳过

**输出**：

```
{
  "synced": ["SWE-bench", "SWE-bench_Lite", "Multi-SWE-Bench-Java"],
  "skipped": ["multi-swe-bench"],
  "message": "同步完成"
}
```

#### GET /api/datasets/{dataset_id}/tasks

**输出**：

```
{
  "tasks": [
    {
      "task_id": "task-001",
      "repository": "apache/commons-lang",
      "issue_title": "Fix NPE in StringUtils",
      "difficulty": "medium"
    }
  ]
}
```

---

## 5. 流程设计

### 5.1 评测任务执行流程

1. 已认证用户通过 POST /api/evaluations 创建评测任务，指定模型、Agent、数据集
2. 后端验证参数，创建 EvaluationTask 记录（状态=排队中），发送 Celery 任务
3. Celery Worker 取出任务，更新状态为"执行中"
4. Worker 遍历数据集中的子任务，对每个子任务：
   a. 启动 Docker 容器（挂载 Volume），传入模型 API 配置和任务信息
   b. Agent 在容器内执行评测，结果写入 Volume
   c. 超时监控：若超过配置阈值，终止容器，标记子任务为"超时"
   d. Worker 从 Volume 读取结果文件，调用对应 Agent 的结果解析器
   e. 创建 SubTaskResult 记录
5. 所有子任务完成后，计算解决率，更新 EvaluationTask 状态为"已完成"
6. 任何步骤发生不可恢复错误，标记任务为"失败"，记录错误信息

### 5.2 排行榜查询流程

1. 用户访问排行榜页面
2. 前端调用 GET /api/leaderboard（可带筛选参数）
3. 后端查询每个模型+Agent+数据集组合的最新评测任务结果
4. 按解决率降序排列返回

### 5.3 轨迹查看流程

1. 用户在排行榜点击某条记录，进入评测详情页
2. 前端调用 GET /api/evaluations/{task_id} 获取子任务列表
3. 用户点击某子任务，前端调用 GET /api/evaluations/{task_id}/subtasks/{subtask_id}
4. 后端返回轨迹 JSON、代码 diff 等，前端渲染展示

---

## 6. 风险 / 权衡

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Docker 容器启动开销影响评测效率 | 单次评测耗时较长 | 预热容器池、批量执行子任务复用容器 |
| 不同 Agent 的输出格式差异大 | 结果解析复杂度高 | 为每种 Agent 实现独立的 ResultParser，定义统一内部格式 |
| 模型 API 不稳定导致评测中断 | 评测任务失败率高 | 实现子任务级别重试，记录失败点支持断点续跑 |
| 并发评测资源竞争 | 服务器资源不足 | Celery worker 并发限制 + 配置最大并发评测数 |
| 评测结果文件较大（轨迹JSON） | 数据库存储压力大 | 轨迹数据使用 JSONB 存储，考虑大文件存对象存储 |
| MVP 阶段仅支持单一数据集 | 扩展时需改动 | 数据集通过配置文件管理，代码层面抽象 Dataset 接口 |
