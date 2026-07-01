import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Descriptions, Table, Tag, Typography, Spin, Button, message } from 'antd';
import { getEvaluation } from '../api/client';

interface SubTaskBrief {
  id: string;
  dataset_task_id: string;
  result: string;
  execution_time: number | null;
  token_usage: number | null;
}

const { Title } = Typography;

const resultColor: Record<string, string> = {
  通过: 'green', 失败: 'red', 超时: 'orange', 未执行: 'default',
};

export default function EvaluationDetail() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [task, setTask] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!taskId) return;
    loadTask();
  }, [taskId]);

  async function loadTask() {
    setLoading(true);
    try {
      const resp = await getEvaluation(taskId!);
      setTask(resp.data);
    } catch {
      message.error('加载评测详情失败');
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <Spin style={{ margin: 48 }} />;
  if (!task) return null;

  const columns = [
    { title: '任务ID', dataIndex: 'dataset_task_id' },
    {
      title: '结果',
      dataIndex: 'result',
      render: (v: string) => <Tag color={resultColor[v]}>{v}</Tag>,
    },
    {
      title: '执行耗时(s)',
      dataIndex: 'execution_time',
      render: (v: number | null) => v != null ? v.toFixed(1) : '-',
    },
    {
      title: 'Token消耗',
      dataIndex: 'token_usage',
      render: (v: number | null) => v != null ? v.toLocaleString() : '-',
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Button onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>返回</Button>
      <Title level={3}>评测详情</Title>
      <Descriptions bordered column={2} style={{ marginBottom: 24 }}>
        <Descriptions.Item label="模型">{task.model_name}</Descriptions.Item>
        <Descriptions.Item label="Agent">{task.agent_name}</Descriptions.Item>
        <Descriptions.Item label="数据集">{task.dataset_name}</Descriptions.Item>
        <Descriptions.Item label="状态">
          <Tag color={task.status === '已完成' ? 'green' : task.status === '失败' ? 'red' : 'blue'}>
            {task.status}
          </Tag>
        </Descriptions.Item>
        <Descriptions.Item label="进度">{task.progress}</Descriptions.Item>
        <Descriptions.Item label="解决率">
          {task.resolved_rate != null ? `${task.resolved_rate.toFixed(2)}%` : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="创建时间">{task.created_at}</Descriptions.Item>
        <Descriptions.Item label="完成时间">{task.completed_at || '-'}</Descriptions.Item>
      </Descriptions>
      <Title level={4}>子任务结果</Title>
      <Table<SubTaskBrief>
        rowKey="id"
        dataSource={task.subtask_results as SubTaskBrief[]}
        columns={columns}
        onRow={record => ({
          onClick: () => navigate(`/evaluations/${taskId}/subtasks/${record.id}`),
          style: { cursor: 'pointer' },
        })}
      />
    </div>
  );
}
