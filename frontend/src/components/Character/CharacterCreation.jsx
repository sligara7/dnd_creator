import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';

const CharacterCreation = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [aiSuggestions, setAiSuggestions] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [character, setCharacter] = useState({
    name: '',
    species: '',
    character_class: '',
    alignment: '',
    ability_scores: {
      strength: 10,
      dexterity: 10,
      constitution: 10,
      intelligence: 10,
      wisdom: 10,
      charisma: 10
    },
    backstory: '',
    appearance: '',
    skills: [],
    feats: [],
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setCharacter({
        ...character,
        [parent]: {
          ...character[parent],
          [child]: value
        }
      });
    } else {
      setCharacter({ ...character, [name]: value });
    }
  };

  const getAiSuggestion = async (prompt) => {
    setIsLoading(true);
    try {
      const response = await api.post('/api/ai/character-guidance', { 
        prompt, 
        character_data: character 
      });
      setAiSuggestions(response.data.suggestion);
    } catch (error) {
      console.error('Error getting AI suggestion:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplySuggestion = () => {
    // This would parse the AI suggestions and apply them to the character state
    // In a real implementation, this would be more sophisticated
    setAiSuggestions('');
  };

  const nextStep = () => {
    setStep(step + 1);
  };

  const prevStep = () => {
    setStep(step - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      // Add user ID from authentication (would be implemented in a real app)
      const characterData = {
        ...character,
        user_id: 'current-user-id'
      };
      
      const response = await api.post('/api/character/create', characterData);
      navigate(`/character/${response.data.id}`);
    } catch (error) {
      console.error('Error creating character:', error);
      // Show error message
    } finally {
      setIsLoading(false);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-bold">Basic Information</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700">Character Name</label>
              <input
                type="text"
                name="name"
                value={character.name}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Species</label>
              <select
                name="species"
                value={character.species}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="">Select Species</option>
                <option value="human">Human</option>
                <option value="elf">Elf</option>
                <option value="dwarf">Dwarf</option>
                {/* More options would be here */}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Class</label>
              <select
                name="character_class"
                value={character.character_class}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="">Select Class</option>
                <option value="fighter">Fighter</option>
                <option value="wizard">Wizard</option>
                <option value="rogue">Rogue</option>
                {/* More options would be here */}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Alignment</label>
              <select
                name="alignment"
                value={character.alignment}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="">Select Alignment</option>
                <option value="lawful_good">Lawful Good</option>
                <option value="neutral_good">Neutral Good</option>
                <option value="chaotic_good">Chaotic Good</option>
                {/* More options would be here */}
              </select>
            </div>
            <div className="pt-4">
              <button
                type="button"
                onClick={() => getAiSuggestion("Help me create a character concept")}
                className="mr-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                disabled={isLoading}
              >
                {isLoading ? 'Getting suggestions...' : 'Get AI Suggestions'}
              </button>
            </div>
          </div>
        );
      // Additional steps would be implemented here
      default:
        return <div>Unknown step</div>;
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Create Your Character</h1>
      <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6">
        {/* Step progress indicator */}
        <div className="mb-6">
          <div className="flex items-center">
            {[1, 2, 3, 4, 5].map((stepNumber) => (
              <React.Fragment key={stepNumber}>
                <div
                  className={`rounded-full h-8 w-8 flex items-center justify-center ${
                    stepNumber <= step ? 'bg-indigo-600 text-white' : 'bg-gray-300'
                  }`}
                >
                  {stepNumber}
                </div>
                {stepNumber < 5 && (
                  <div
                    className={`h-1 w-10 ${
                      stepNumber < step ? 'bg-indigo-600' : 'bg-gray-300'
                    }`}
                  />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {renderStep()}
          
          {/* AI Suggestions Panel */}
          {aiSuggestions && (
            <div className="mt-6 p-4 bg-blue-50 rounded-md">
              <h3 className="font-medium text-blue-800">AI Suggestions</h3>
              <p className="mt-2 text-sm text-blue-700 whitespace-pre-wrap">{aiSuggestions}</p>
              <button
                type="button"
                onClick={handleApplySuggestion}
                className="mt-2 inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Apply Suggestion
              </button>
            </div>
          )}
          
          {/* Navigation buttons */}
          <div className="mt-8 flex justify-between">
            {step > 1 && (
              <button
                type="button"
                onClick={prevStep}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Previous
              </button>
            )}
            <div>
              {step < 5 ? (
                <button
                  type="button"
                  onClick={nextStep}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Next
                </button>
              ) : (
                <button
                  type="submit"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  disabled={isLoading}
                >
                  {isLoading ? 'Creating...' : 'Create Character'}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CharacterCreation;