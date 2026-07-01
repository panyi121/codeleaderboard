import React, { useEffect, useState } from 'react';
import { Table, Typography, message, Drawer, Tag } from 'antd';
import { getDatasets, getDatasetTasks } from '../api/client';

const { Title } = Typography;

export default function Datasets() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [tasks, setTasks] = useState<any[]>([]);
  const [tasksLoading, setTasksLoading] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState<string>('');

  useEffect(() => { loadDatasets(); }, []);

  async function loadDatasets() {
    setLoading(true);
    try {
      const resp = await getDatasets();
      setDatasets(resp.data.datasets);
    } catch {
      message.error('加载数据集失败');
    } finally {
      setLoading(false);
    }
  }

  async function openTasks(dataset: any) {
    setSelectedDataset(dataset.name);
    setDrawerOpen(true);
    setTasksLoading(true);
    try {
      const resp = await getDatasetTasks(dataset.id);
      setTasks(resp.data.tasks);
    } catch {
      message.error('加载任务列表失败');
    } finally {
      setTasksLoading(false);
    }
  }

  const datasetColumns = [
    { title: '名称', dataIndex: 'name' },
    { title: '语言', dataIndex: 'language' },
    { title: '任务总数', dataIndex: 'task_count' },
    { title: '描述', dataIndex: 'description', ellipsis: true },
  ];

  const taskColumns = [
    { title: '任务ID', dataIndex: 'task_id' },
    { title: '仓库', dataIndex: 'repository' },
    { title: 'Issue标题', dataIndex: 'issue_title', ellipsis: true },
    {
      title: '难度',
      dataIndex: 'difficulty',
      render: (v: string) => {
        const color = v === 'hard' ? 'red' : v === 'medium' ? 'orange' : 'green';
        return <Tag color={color}>{v}</Tag>;
      },
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>数据集</Title>
      <Table
        rowKey="id"
        dataSource={datasets}
        columns={datasetColumns}
        loading={loading}
        onRow={record => ({ onClick: () => openTasks(record), style: { cursor: 'pointer' } })}
      />
      <Drawer
        title={`${selectedDataset} - 任务列表`}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={700}
      >
        <Table
          rowKey="task_id"
          dataSource={tasks}
          columns={taskColumns}
          loading={tasksLoading}
          size="small"
        />
      </Drawer>
    </div>
  );
}
