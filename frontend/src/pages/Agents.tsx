import React, { useEffect, useState } from 'react';
import { Table, Button, Form, Input, Modal, Tag, Typography, message, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { getAgents, registerAgent } from '../api/client';

const { Title } = Typography;

export default function Agents() {
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => { loadAgents(); }, []);

  async function loadAgents() {
    setLoading(true);
    try {
      const resp = await getAgents();
      setAgents(resp.data.agents);
    } catch {
      message.error('加载 Agent 列表失败');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(values: any) {
    setSubmitting(true);
    try {
      await registerAgent(values);
      message.success('Agent 注册成功');
      setModalOpen(false);
      form.resetFields();
      loadAgents();
    } catch (err: any) {
      const detail = err.response?.data?.detail ?? '注册失败';
      message.error(detail);
    } finally {
      setSubmitting(false);
    }
  }

  const columns = [
    { title: '名称', dataIndex: 'name' },
    { title: '类型', dataIndex: 'agent_type' },
    { title: 'Docker 镜像', dataIndex: 'docker_image', ellipsis: true },
    {
      title: '状态',
      dataIndex: 'status',
      render: (v: string) => <Tag color={v === '可用' ? 'green' : 'red'}>{v}</Tag>,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Space style={{ marginBottom: 16 }}>
        <Title level={2} style={{ margin: 0 }}>Agent 管理</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          注册 Agent
        </Button>
      </Space>
      <Table rowKey="id" dataSource={agents} columns={columns} loading={loading} />
      <Modal
        title="注册新 Agent"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="name" label="Agent 名称" rules={[{ required: true }]}>
            <Input placeholder="Claude Code" />
          </Form.Item>
          <Form.Item name="agent_type" label="类型标识" rules={[{ required: true }]}>
            <Input placeholder="claude-code" />
          </Form.Item>
          <Form.Item name="docker_image" label="Docker 镜像" rules={[{ required: true }]}>
            <Input placeholder="claude-code:latest" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={submitting} block>
              注册
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
