import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import EvaluationDetail from '../pages/EvaluationDetail';
import * as client from '../api/client';

jest.mock('../api/client');
const mockClient = client as jest.Mocked<typeof client>;

test('renders evaluation detail', async () => {
  mockClient.getEvaluation.mockResolvedValue({
    data: {
      task_id: 'uuid-1', model_name: 'GLM-5.2', agent_name: 'Claude Code',
      dataset_name: 'Multi-SWE-Bench-Java', status: '已完成',
      progress: '80/80', resolved_rate: 43.75, subtask_results: [],
      created_at: '2026-07-01T00:00:00Z', completed_at: '2026-07-01T01:00:00Z',
    },
  } as any);

  render(
    <MemoryRouter initialEntries={['/evaluations/uuid-1']}>
      <Routes>
        <Route path="/evaluations/:taskId" element={<EvaluationDetail />} />
      </Routes>
    </MemoryRouter>
  );
  await waitFor(() => expect(screen.getByText('GLM-5.2')).toBeInTheDocument());
  expect(screen.getByText('Claude Code')).toBeInTheDocument();
  expect(screen.getByText('43.75%')).toBeInTheDocument();
});
