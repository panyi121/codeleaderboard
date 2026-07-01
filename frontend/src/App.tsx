import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Layout, Menu, Input, Button, Space, Typography } from 'antd';
import { TrophyOutlined, ExperimentOutlined, RobotOutlined, DatabaseOutlined, KeyOutlined } from '@ant-design/icons';
import Leaderboard from './pages/Leaderboard';
import EvaluationDetail from './pages/EvaluationDetail';
import SubTaskDetail from './pages/SubTaskDetail';
import Models from './pages/Models';
import Agents from './pages/Agents';
import Datasets from './pages/Datasets';
import { setAuthToken, clearAuthToken } from './api/client';

const { Header, Content, Sider } = Layout;
const { Text } = Typography;

function NavMenu() {
  const location = useLocation();
  const selectedKey = location.pathname.split('/')[1] || 'leaderboard';

  const items = [
    { key: 'leaderboard', icon: <TrophyOutlined />, label: <Link to="/">排行榜</Link> },
    { key: 'models', icon: <ExperimentOutlined />, label: <Link to="/models">模型管理</Link> },
    { key: 'agents', icon: <RobotOutlined />, label: <Link to="/agents">Agent 管理</Link> },
    { key: 'datasets', icon: <DatabaseOutlined />, label: <Link to="/datasets">数据集</Link> },
  ];

  return <Menu mode="inline" selectedKeys={[selectedKey]} items={items} />;
}

function AuthBar() {
  const [token, setToken] = useState('');
  const [authed, setAuthed] = useState(false);

  function login() {
    if (token.trim()) {
      setAuthToken(token.trim());
      setAuthed(true);
    }
  }

  function logout() {
    clearAuthToken();
    setAuthed(false);
    setToken('');
  }

  return (
    <Space>
      {authed ? (
        <>
          <Text style={{ color: '#fff' }}>已登录</Text>
          <Button size="small" onClick={logout}>退出</Button>
        </>
      ) : (
        <>
          <Input.Password
            size="small"
            placeholder="输入 API Token"
            value={token}
            onChange={e => setToken(e.target.value)}
            style={{ width: 180 }}
            prefix={<KeyOutlined />}
          />
          <Button size="small" type="primary" onClick={login}>登录</Button>
        </>
      )}
    </Space>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ color: '#fff', fontSize: 18, fontWeight: 600 }}>Code Leaderboard</span>
          <AuthBar />
        </Header>
        <Layout>
          <Sider width={200} style={{ background: '#fff' }}>
            <NavMenu />
          </Sider>
          <Content style={{ background: '#f5f5f5', minHeight: 280 }}>
            <Routes>
              <Route path="/" element={<Leaderboard />} />
              <Route path="/models" element={<Models />} />
              <Route path="/agents" element={<Agents />} />
              <Route path="/datasets" element={<Datasets />} />
              <Route path="/evaluations/:taskId" element={<EvaluationDetail />} />
              <Route path="/evaluations/:taskId/subtasks/:subtaskId" element={<SubTaskDetail />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </BrowserRouter>
  );
}
