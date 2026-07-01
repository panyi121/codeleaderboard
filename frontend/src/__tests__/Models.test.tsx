import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Models from '../pages/Models';
import * as client from '../api/client';

jest.mock('../api/client');
const mockClient = client as jest.Mocked<typeof client>;

beforeEach(() => {
  mockClient.getModels.mockResolvedValue({
    data: { models: [{ id: '1', name: 'GLM-5.2', model_type: '开源', api_endpoint: 'http://x.com', model_identifier: 'glm', status: '可用', created_at: '' }] },
  } as any);
});

test('renders model management page', async () => {
  render(<MemoryRouter><Models /></MemoryRouter>);
  await waitFor(() => expect(screen.getByText('模型管理')).toBeInTheDocument());
  expect(screen.getByText('GLM-5.2')).toBeInTheDocument();
});

test('shows register button', async () => {
  render(<MemoryRouter><Models /></MemoryRouter>);
  await waitFor(() => expect(screen.getByText('注册模型')).toBeInTheDocument());
});
