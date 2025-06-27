/**
 * API Service for D&D Character Creator
 * Handles all communication with the FastAPI backend
 */

import axios from 'axios';

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Character API endpoints
export const characterAPI = {
  // Get all characters
  getAll: (playerName = null) => {
    const params = playerName ? { player_name: playerName } : {};
    return api.get('/api/v1/characters', { params });
  },

  // Get character by ID
  getById: (id) => api.get(`/api/v1/characters/${id}`),

  // Create new character
  create: (characterData) => api.post('/api/v1/characters', characterData),

  // Update character
  update: (id, characterData) => api.put(`/api/v1/characters/${id}`, characterData),

  // Delete character
  delete: (id) => api.delete(`/api/v1/characters/${id}`),

  // Update character state (for gameplay)
  updateState: (id, stateData) => api.put(`/api/v1/characters/${id}/state`, stateData),

  // Apply combat effects
  applyCombat: (id, combatData) => api.post(`/api/v1/characters/${id}/combat`, combatData),

  // Apply rest effects
  applyRest: (id, restData) => api.post(`/api/v1/characters/${id}/rest`, restData),

  // Get character sheet with all calculated stats
  getSheet: (id) => api.get(`/api/v1/characters/${id}/sheet`),

  // Get character state
  getState: (id) => api.get(`/api/v1/characters/${id}/state`),

  // Validate character
  validate: (id) => api.get(`/api/v1/characters/${id}/validate`),
};

// Content Generation API endpoints
export const generationAPI = {
  // Generate character backstory
  generateBackstory: (characterData) => api.post('/api/v1/generate/backstory', characterData),

  // Generate equipment suggestions
  generateEquipment: (characterData) => api.post('/api/v1/generate/equipment', characterData),

  // Generate full character (AI-driven creation)
  generateCharacter: (generationData) => api.post('/api/v1/characters/generate', generationData),

  // Generator endpoints
  generateBackstory: (characterData) => api.post('/api/v1/generate/backstory', { character_data: characterData }),
  generateEquipment: (characterData) => api.post('/api/v1/generate/equipment', { character_data: characterData }),
};

// Item Creation API endpoints
export const itemAPI = {
  // Create custom item
  create: (itemData) => api.post('/api/v1/items/create', itemData),

  // Get item templates (if available)
  getTemplates: () => api.get('/api/v1/items/templates'),
};

// NPC Creation API endpoints
export const npcAPI = {
  // Create custom NPC
  create: (npcData) => api.post('/api/v1/npcs/create', npcData),

  // Get NPC templates (if available)
  getTemplates: () => api.get('/api/v1/npcs/templates'),
};

// Creature Creation API endpoints
export const creatureAPI = {
  // Create custom creature
  create: (creatureData) => api.post('/api/v1/creatures/create', creatureData),

  // Get creature templates (if available)
  getTemplates: () => api.get('/api/v1/creatures/templates'),
};

// Character Versioning API endpoints (Git-like system)
export const versioningAPI = {
  // Create character repository
  createRepository: (repositoryData) => api.post('/api/v1/character-repositories', repositoryData),

  // Get repository info
  getRepository: (repositoryId) => api.get(`/api/v1/character-repositories/${repositoryId}`),

  // Get character timeline
  getTimeline: (repositoryId) => api.get(`/api/v1/character-repositories/${repositoryId}/timeline`),

  // Get character visualization data
  getVisualization: (repositoryId) => api.get(`/api/v1/character-repositories/${repositoryId}/visualization`),

  // Create branch
  createBranch: (repositoryId, branchData) => api.post(`/api/v1/character-repositories/${repositoryId}/branches`, branchData),

  // Get branches
  getBranches: (repositoryId) => api.get(`/api/v1/character-repositories/${repositoryId}/branches`),

  // Create commit
  createCommit: (repositoryId, commitData) => api.post(`/api/v1/character-repositories/${repositoryId}/commits`, commitData),

  // Get commits
  getCommits: (repositoryId) => api.get(`/api/v1/character-repositories/${repositoryId}/commits`),

  // Get character at specific commit
  getCharacterAtCommit: (commitHash) => api.get(`/api/v1/character-commits/${commitHash}/character`),

  // Level up character
  levelUp: (repositoryId, levelUpData) => api.post(`/api/v1/character-repositories/${repositoryId}/level-up`, levelUpData),

  // Tag milestone
  tagMilestone: (repositoryId, tagData) => api.post(`/api/v1/character-repositories/${repositoryId}/tags`, tagData),
};

// Validation API endpoints
export const validationAPI = {
  // Validate character data
  validateCharacter: (characterData) => api.post('/api/v1/validate/character', characterData),
};

// Utility functions
export const apiUtils = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Test connection to backend
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
