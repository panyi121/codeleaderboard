import React, { useEffect, useState } from 'react';
import { Table, Select, Space, Typography, Empty, Button, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { getLeaderboard, getModels, getAgents, getDatasets } from '../api/client';

const { Title } = Typography;

interface LeaderboardEntry {
  rank: number;
  model_name: string;
  agent_name: string;
  dataset_name: string;
  resolved_rate: number;
  total_tasks: number;
  resolved_tasks: number;
  task_id: string;
}

export default function Leaderboard() {
  const navigate = useNavigate();
  const [rankings, setRankings] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<string[]>([]);
  const [agents, setAgents] = useState<string[]>([]);
  const [datasets, setDatasets] = useState<string[]>([]);
  const [filterModel, setFilterModel] = useState<string | undefined>();
  const [filterAgent, setFilterAgent] = useState<string | undefined>();
  const [filterDataset, setFilterDataset] = useState<string | undefined>();

  useEffect(() => {
    loadFilterOptions();
  }, []);

  useEffect(() => {
    loadLeaderboard();
  }, [filterModel, filterAgent, filterDataset]);

  async function loadFilterOptions() {
    try {
      const [mRes, aRes, dRes] = await Promise.all([getModels(), getAgents(), getDatasets()]);
      setModels(mRes.data.models.map((m: any) => m.name));
      setAgents(aRes.data.agents.map((a: any) => a.name));
      setDatasets(dRes.data.datasets.map((d: any) => d.name));
    } catch {}
  }

  async function loadLeaderboard() {
    setLoading(true);
    try {
      const resp = await getLeaderboard({
        model: filterModel,
        agent: filterAgent,
        dataset: filterDataset,
      });
      setRankings(resp.data.rankings);
    } catch {
      message.error('加载排行榜失败');
    } finally {
      setLoading(false);
    }
  }

  const columns = [
    { title: '排名', dataIndex: 'rank', width: 80 },
    { title: '模型', dataIndex: 'model_name' },
    { title: 'Agent', dataIndex: 'agent_name' },
    { title: '数据集', dataIndex: 'dataset_name' },
    {
      title: '解决率',
      dataIndex: 'resolved_rate',
      render: (v: number) => `${v.toFixed(2)}%`,
      sorter: (a: LeaderboardEntry, b: LeaderboardEntry) => a.resolved_rate - b.resolved_rate,
    },
    {
      title: '已解决/总任务',
      render: (_: any, r: LeaderboardEntry) => `${r.resolved_tasks}/${r.total_tasks}`,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>排行榜</Title>
      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          placeholder="筛选模型"
          allowClear
          style={{ width: 180 }}
          options={models.map(m => ({ label: m, value: m }))}
          onChange={setFilterModel}
        />
        <Select
          placeholder="筛选 Agent"
          allowClear
          style={{ width: 180 }}
          options={agents.map(a => ({ label: a, value: a }))}
          onChange={setFilterAgent}
        />
        <Select
          placeholder="筛选数据集"
          allowClear
          style={{ width: 220 }}
          options={datasets.map(d => ({ label: d, value: d }))}
          onChange={setFilterDataset}
        />
        <Button onClick={loadLeaderboard}>刷新</Button>
      </Space>
      <Table
        rowKey="task_id"
        dataSource={rankings}
        columns={columns}
        loading={loading}
        locale={{ emptyText: <Empty description="暂无评测数据，请先触发评测" /> }}
        onRow={record => ({ onClick: () => navigate(`/evaluations/${record.task_id}`) })}
        style={{ cursor: 'pointer' }}
      />
    </div>
  );
}
