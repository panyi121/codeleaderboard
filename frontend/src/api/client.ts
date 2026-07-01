import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export function setAuthToken(token: string) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

export function clearAuthToken() {
  delete api.defaults.headers.common['Authorization'];
}

// Leaderboard
export const getLeaderboard = (params?: { model?: string; agent?: string; dataset?: string }) =>
  api.get('/api/leaderboard', { params });

// Models
export const getModels = () => api.get('/api/models');
export const registerModel = (data: {
  name: string; model_type: string; api_endpoint: string; model_identifier: string;
}) => api.post('/api/models', data);

// Agents
export const getAgents = () => api.get('/api/agents');
export const registerAgent = (data: {
  name: string; agent_type: string; docker_image: string;
}) => api.post('/api/agents', data);

// Datasets
export const getDatasets = () => api.get('/api/datasets');
export const getDatasetTasks = (datasetId: string) => api.get(`/api/datasets/${datasetId}/tasks`);

// Evaluations
export const createEvaluation = (data: {
  model_id: string; agent_id: string; dataset_id: string;
}) => api.post('/api/evaluations', data);
export const getEvaluation = (taskId: string) => api.get(`/api/evaluations/${taskId}`);
export const getSubtaskDetail = (taskId: string, subtaskId: string) =>
  api.get(`/api/evaluations/${taskId}/subtasks/${subtaskId}`);
