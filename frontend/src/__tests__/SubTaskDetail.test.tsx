import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import SubTaskDetail from '../pages/SubTaskDetail';
import * as client from '../api/client';

jest.mock('../api/client');
const mockClient = client as jest.Mocked<typeof client>;

test('renders subtask detail with trajectory and diff', async () => {
  mockClient.getSubtaskDetail.mockResolvedValue({
    data: {
      dataset_task_id: 'task-001',
      result: '通过',
      trajectory: { steps: [{ action: 'read_file', content: 'Test.java' }] },
      code_diff: 'diff --git a/Test.java b/Test.java\n+fix',
      execution_time: 90.0,
      token_usage: 8000,
      error_log: null,
    },
  } as any);

  render(
    <MemoryRouter initialEntries={['/evaluations/t1/subtasks/s1']}>
      <Routes>
        <Route path="/evaluations/:taskId/subtasks/:subtaskId" element={<SubTaskDetail />} />
      </Routes>
    </MemoryRouter>
  );
  await waitFor(() => expect(screen.getByText(/task-001/)).toBeInTheDocument());
  expect(screen.getByText('通过')).toBeInTheDocument();
});
