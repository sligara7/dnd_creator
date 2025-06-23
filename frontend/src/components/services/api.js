// D&D Character Creator API Service
// Handles all communication with the FastAPI backend (podman container)

import axios from 'axios';

// Determine API base URL from environment (for podman networking)
const API_BASE_URL =
  process.env.REACT_APP_API_URL ||
  import.meta.env.VITE_API_URL ||
  'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// --- CHARACTER ENDPOINTS ---
export const characterAPI = {
  getAll: (params = {}) => api.get('/api/v1/characters', { params }),
  getById: (id) => api.get(`/api/v1/characters/${id}`),
  create: (characterData) => api.post('/api/v1/characters', characterData),
  update: (id, characterData) => api.put(`/api/v1/characters/${id}`, characterData),
  delete: (id) => api.delete(`/api/v1/characters/${id}`),
  updateState: (id, stateData) => api.put(`/api/v1/characters/${id}/state`, stateData),
};

// --- CHARACTER REPOSITORY (GIT-LIKE) ENDPOINTS ---
export const repoAPI = {
  create: (repoData) => api.post('/api/v1/character-repositories', repoData),
  get: (id) => api.get(`/api/v1/character-repositories/${id}`),
  timeline: (id) => api.get(`/api/v1/character-repositories/${id}/timeline`),
  visualization: (id) => api.get(`/api/v1/character-repositories/${id}/visualization`),
  createBranch: (id, branchData) => api.post(`/api/v1/character-repositories/${id}/branches`, branchData),
  createCommit: (id, commitData) => api.post(`/api/v1/character-repositories/${id}/commits`, commitData),
  createTag: (id, tagData) => api.post(`/api/v1/character-repositories/${id}/tags`, tagData),
};

// --- CONTENT GENERATION (LLM) ENDPOINTS ---
export const generationAPI = {
  generateBackstory: (characterData) => api.post('/api/v1/generate/backstory', characterData),
  generateEquipment: (characterData) => api.post('/api/v1/generate/equipment', characterData),
  generateCharacter: (prompt) => api.post('/api/v1/generate/character', { prompt }),
};

// --- ITEM, NPC, CREATURE ENDPOINTS ---
export const itemAPI = {
  create: (itemData) => api.post('/api/v1/items', itemData),
  getTemplates: () => api.get('/api/v1/items/templates'),
};
export const npcAPI = {
  create: (npcData) => api.post('/api/v1/npcs', npcData),
  getTemplates: () => api.get('/api/v1/npcs/templates'),
};
export const creatureAPI = {
  create: (creatureData) => api.post('/api/v1/creatures', creatureData),
  getTemplates: () => api.get('/api/v1/creatures/templates'),
};

// --- UTILITY ENDPOINTS ---
export const apiUtils = {
  healthCheck: () => api.get('/health'),
  testConnection: async () => {
    try {
      await api.get('/health');
      return { connected: true, message: 'Backend connection successful' };
    } catch (error) {
      return { connected: false, message: error.message };
    }
  },
};

export default api;
