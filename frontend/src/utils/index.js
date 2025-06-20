/**
 * Common utility functions for the D&D Character Creator frontend
 */

// Utility functions for character data
export const characterUtils = {
  // Calculate ability modifier from ability score
  getAbilityModifier: (score) => {
    return Math.floor((score - 10) / 2);
  },

  // Format ability modifier for display
  formatModifier: (modifier) => {
    return modifier >= 0 ? `+${modifier}` : `${modifier}`;
  },

  // Calculate proficiency bonus based on level
  getProficiencyBonus: (level) => {
    return Math.ceil(level / 4) + 1;
  },

  // Get character level (sum of all class levels)
  getTotalLevel: (character) => {
    if (!character.character_classes) return 1;
    return Object.values(character.character_classes).reduce((sum, level) => sum + level, 0) || 1;
  }
};

// Utility functions for API responses
export const apiUtils = {
  // Handle API errors gracefully
  handleError: (error, fallbackMessage = 'An error occurred') => {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return fallbackMessage;
  },

  // Format API response data
  formatResponse: (response) => {
    return response.data || response;
  }
};

// Utility functions for UI
export const uiUtils = {
  // Capitalize first letter
  capitalize: (str) => {
    return str.charAt(0).toUpperCase() + str.slice(1);
  },

  // Format enum values for display
  formatEnumValue: (value) => {
    return value.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  },

  // Generate random ID
  generateId: () => {
    return Math.random().toString(36).substr(2, 9);
  }
};

// D&D specific utilities
export const dndUtils = {
  // Common D&D 5e species
  SPECIES: [
    'Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 
    'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling'
  ],

  // Common D&D 5e classes
  CLASSES: [
    'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter',
    'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer',
    'Warlock', 'Wizard'
  ],

  // Ability scores
  ABILITIES: ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'],

  // Alignments
  ALIGNMENTS: [
    'Lawful Good', 'Neutral Good', 'Chaotic Good',
    'Lawful Neutral', 'True Neutral', 'Chaotic Neutral',
    'Lawful Evil', 'Neutral Evil', 'Chaotic Evil'
  ]
};

export default {
  characterUtils,
  apiUtils,
  uiUtils,
  dndUtils
};
