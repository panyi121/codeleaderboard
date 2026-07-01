import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Datasets from '../pages/Datasets';
import * as client from '../api/client';

jest.mock('../api/client');
const mockClient = client as jest.Mocked<typeof client>;

beforeEach(() => {
  mockClient.getDatasets.mockResolvedValue({
    data: { datasets: [{ id: '1', name: 'Multi-SWE-Bench-Java', language: 'Java', task_count: 80, description: 'Java benchmark', created_at: '' }] },
  } as any);
});

test('renders datasets page', async () => {
  render(<MemoryRouter><Datasets /></MemoryRouter>);
  await waitFor(() => expect(screen.getByText('数据集')).toBeInTheDocument());
  expect(screen.getByText('Multi-SWE-Bench-Java')).toBeInTheDocument();
});
