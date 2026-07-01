import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Agents from '../pages/Agents';
import * as client from '../api/client';

jest.mock('../api/client');
const mockClient = client as jest.Mocked<typeof client>;

beforeEach(() => {
  mockClient.getAgents.mockResolvedValue({
    data: { agents: [{ id: '1', name: 'Claude Code', agent_type: 'claude-code', docker_image: 'claude-code:latest', status: '可用', created_at: '' }] },
  } as any);
});

test('renders agent management page', async () => {
  render(<MemoryRouter><Agents /></MemoryRouter>);
  await waitFor(() => expect(screen.getByText('Agent 管理')).toBeInTheDocument());
  expect(screen.getByText('Claude Code')).toBeInTheDocument();
});
