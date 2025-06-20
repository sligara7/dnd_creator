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
};

// Content Generation API endpoints
export const generationAPI = {
  // Generate character backstory
  generateBackstory: (characterData) => api.post('/api/v1/generate/backstory', characterData),

  // Generate equipment suggestions
  generateEquipment: (characterData) => api.post('/api/v1/generate/equipment', characterData),

  // Generate full character (AI-driven creation)
  generateCharacter: (prompt) => api.post('/api/v1/generate/character', { prompt }),
};

// Item Creation API endpoints
export const itemAPI = {
  // Create custom item
  create: (itemData) => api.post('/api/v1/items', itemData),

  // Get item templates
  getTemplates: () => api.get('/api/v1/items/templates'),
};

// NPC Creation API endpoints
export const npcAPI = {
  // Create custom NPC
  create: (npcData) => api.post('/api/v1/npcs', npcData),

  // Get NPC templates
  getTemplates: () => api.get('/api/v1/npcs/templates'),
};

// Creature Creation API endpoints
export const creatureAPI = {
  // Create custom creature
  create: (creatureData) => api.post('/api/v1/creatures', creatureData),

  // Get creature templates
  getTemplates: () => api.get('/api/v1/creatures/templates'),
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
