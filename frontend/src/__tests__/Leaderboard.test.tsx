import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Leaderboard from '../pages/Leaderboard';
import * as client from '../api/client';

jest.mock('../api/client');

const mockClient = client as jest.Mocked<typeof client>;

beforeEach(() => {
  mockClient.getLeaderboard.mockResolvedValue({ data: { rankings: [] } } as any);
  mockClient.getModels.mockResolvedValue({ data: { models: [] } } as any);
  mockClient.getAgents.mockResolvedValue({ data: { agents: [] } } as any);
  mockClient.getDatasets.mockResolvedValue({ data: { datasets: [] } } as any);
});

test('renders leaderboard heading', async () => {
  render(<MemoryRouter><Leaderboard /></MemoryRouter>);
  await waitFor(() => expect(screen.getByText('排行榜')).toBeInTheDocument());
});

test('shows empty state when no data', async () => {
  render(<MemoryRouter><Leaderboard /></MemoryRouter>);
  await waitFor(() => expect(screen.getByText(/暂无评测数据/)).toBeInTheDocument());
});

test('renders ranking rows', async () => {
  mockClient.getLeaderboard.mockResolvedValue({
    data: {
      rankings: [{
        rank: 1, model_name: 'GLM-5.2', agent_name: 'Claude Code',
        dataset_name: 'Multi-SWE-Bench-Java', resolved_rate: 43.75,
        total_tasks: 80, resolved_tasks: 35, task_id: 'uuid-1',
      }],
    },
  } as any);
  render(<MemoryRouter><Leaderboard /></MemoryRouter>);
  await waitFor(() => expect(screen.getByText('GLM-5.2')).toBeInTheDocument());
  expect(screen.getByText('Claude Code')).toBeInTheDocument();
});
