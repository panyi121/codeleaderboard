import React, { useEffect, useState } from 'react';
import { Table, Button, Form, Input, Select, Modal, Tag, Typography, message, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { getModels, registerModel } from '../api/client';

const { Title } = Typography;

export default function Models() {
  const [models, setModels] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => { loadModels(); }, []);

  async function loadModels() {
    setLoading(true);
    try {
      const resp = await getModels();
      setModels(resp.data.models);
    } catch {
      message.error('加载模型列表失败');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(values: any) {
    setSubmitting(true);
    try {
      await registerModel(values);
      message.success('模型注册成功');
      setModalOpen(false);
      form.resetFields();
      loadModels();
    } catch (err: any) {
      const detail = err.response?.data?.detail ?? '注册失败';
      message.error(detail);
    } finally {
      setSubmitting(false);
    }
  }

  const columns = [
    { title: '名称', dataIndex: 'name' },
    { title: '类型', dataIndex: 'model_type' },
    { title: 'API端点', dataIndex: 'api_endpoint', ellipsis: true },
    { title: '模型标识', dataIndex: 'model_identifier' },
    {
      title: '状态',
      dataIndex: 'status',
      render: (v: string) => <Tag color={v === '可用' ? 'green' : 'red'}>{v}</Tag>,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Space style={{ marginBottom: 16 }}>
        <Title level={2} style={{ margin: 0 }}>模型管理</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          注册模型
        </Button>
      </Space>
      <Table rowKey="id" dataSource={models} columns={columns} loading={loading} />
      <Modal
        title="注册新模型"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="name" label="模型名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="model_type" label="类型" rules={[{ required: true }]}>
            <Select options={[{ label: '开源', value: '开源' }, { label: '闭源', value: '闭源' }]} />
          </Form.Item>
          <Form.Item name="api_endpoint" label="API端点" rules={[{ required: true }]}>
            <Input placeholder="https://api.example.com/v1" />
          </Form.Item>
          <Form.Item name="model_identifier" label="模型标识" rules={[{ required: true }]}>
            <Input placeholder="glm-5.2" />
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
