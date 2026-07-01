import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Descriptions, Tag, Typography, Spin, Button, message, Timeline, Card } from 'antd';
import ReactDiffViewer from 'react-diff-viewer-continued';
import { getSubtaskDetail } from '../api/client';

const { Title, Paragraph } = Typography;

const resultColor: Record<string, string> = {
  通过: 'green', 失败: 'red', 超时: 'orange', 未执行: 'default',
};

export default function SubTaskDetail() {
  const { taskId, subtaskId } = useParams<{ taskId: string; subtaskId: string }>();
  const navigate = useNavigate();
  const [subtask, setSubtask] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!taskId || !subtaskId) return;
    loadSubtask();
  }, [taskId, subtaskId]);

  async function loadSubtask() {
    setLoading(true);
    try {
      const resp = await getSubtaskDetail(taskId!, subtaskId!);
      setSubtask(resp.data);
    } catch {
      message.error('加载子任务详情失败');
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <Spin style={{ margin: 48 }} />;
  if (!subtask) return null;

  const trajectorySteps: any[] = subtask.trajectory?.steps ?? [];

  return (
    <div style={{ padding: 24 }}>
      <Button onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>返回</Button>
      <Title level={3}>子任务详情：{subtask.dataset_task_id}</Title>
      <Descriptions bordered column={2} style={{ marginBottom: 24 }}>
        <Descriptions.Item label="结果">
          <Tag color={resultColor[subtask.result]}>{subtask.result}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="执行耗时">
          {subtask.execution_time != null ? `${subtask.execution_time.toFixed(1)}s` : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="Token消耗">
          {subtask.token_usage != null ? subtask.token_usage.toLocaleString() : '-'}
        </Descriptions.Item>
      </Descriptions>

      {trajectorySteps.length > 0 && (
        <Card title="执行轨迹" style={{ marginBottom: 24 }}>
          <Timeline
            items={trajectorySteps.map((step: any, idx: number) => ({
              children: (
                <div key={idx}>
                  <strong>{step.action ?? `步骤 ${idx + 1}`}</strong>
                  {step.content && <Paragraph style={{ marginTop: 4 }}>{step.content}</Paragraph>}
                </div>
              ),
            }))}
          />
        </Card>
      )}

      {subtask.code_diff && (
        <Card title="代码变更 Diff" style={{ marginBottom: 24 }}>
          <ReactDiffViewer
            oldValue=""
            newValue={subtask.code_diff}
            splitView={false}
            useDarkTheme={false}
          />
        </Card>
      )}

      {subtask.error_log && (
        <Card title="错误日志">
          <Paragraph code>{subtask.error_log}</Paragraph>
        </Card>
      )}
    </div>
  );
}
