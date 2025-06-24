import React, { useState, useEffect } from 'react';
import { generationAPI, characterAPI, apiUtils, versioningAPI } from '../../services/api';

const CharacterCreator = () => {
  const [step, setStep] = useState(1);
  const [description, setDescription] = useState('');
  const [level, setLevel] = useState(1);
  const [generateBackstory, setGenerateBackstory] = useState(true);
  const [includeCustomContent, setIncludeCustomContent] = useState(false);
  const [addInitialJournal, setAddInitialJournal] = useState(true);
  const [character, setCharacter] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [iteration, setIteration] = useState(0);
  const [committed, setCommitted] = useState(false);
  const [backendConnected, setBackendConnected] = useState(false);
  const [repository, setRepository] = useState(null);

  // Check backend connection on component mount
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      const result = await apiUtils.testConnection();
      setBackendConnected(result.connected);
      if (!result.connected) {
        setError(`Backend connection failed: ${result.message}`);
      }
    } catch (e) {
      setBackendConnected(false);
      setError('Failed to connect to backend. Please ensure the backend server is running.');
    }
  };

  // Step 1: Generate character using backend API
  const handleCreate = async () => {
    if (!backendConnected) {
      setError('Backend not connected. Please check the server.');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      console.log('🎲 Creating character with parameters:', {
        description, level, generateBackstory, includeCustomContent, addInitialJournal
      });

      // Use the character generation API
      const response = await generationAPI.generateCharacter({
        description: description,
        level: level,
        generate_backstory: generateBackstory,
        include_custom_content: includeCustomContent,
        add_initial_journal: addInitialJournal
      });

      console.log('✅ Character generation response:', response.data);
      
      if (response.data) {
        setCharacter(response.data);
        setStep(2);
        setIteration(iteration + 1);
      } else {
        setError('Character generation failed - no data returned.');
      }
    } catch (e) {
      console.error('❌ Character creation error:', e);
      setError(`Error creating character: ${e.response?.data?.detail || e.message}`);
    }
    setIsLoading(false);
  };

  // Step 2: Update character (iterate and improve)
  const handleIterate = async () => {
    if (!character || !character.id) {
      setError('No character loaded for iteration.');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      console.log('🔄 Updating character:', character.id);

      // Generate new backstory as an example of iteration
      const backstoryResponse = await generationAPI.generateBackstory({
        character_data: character,
        user_description: `${description} (iteration ${iteration + 1})`
      });

      console.log('✅ New backstory generated:', backstoryResponse.data);

      // Update the character with new backstory
      const updatedCharacter = {
        ...character,
        backstory: backstoryResponse.data.backstory || character.backstory,
        // Add iteration marker
        name: character.core?.name ? `${character.core.name} (v${iteration + 1})` : `Character v${iteration + 1}`
      };

      // Update in backend
      const updateResponse = await characterAPI.update(character.id, updatedCharacter);
      
      setCharacter(updateResponse.data);
      setIteration(iteration + 1);
      
      console.log('✅ Character updated successfully');
    } catch (e) {
      console.error('❌ Character update error:', e);
      setError(`Error updating character: ${e.response?.data?.detail || e.message}`);
    }
    setIsLoading(false);
  };

  // Step 3: Commit character to versioning system
  const handleCommit = async () => {
    if (!character || !character.id) {
      setError('No character loaded for commit.');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      console.log('💾 Committing character to versioning system:', character.id);

      // First, create a repository if we don't have one
      if (!repository) {
        const repoResponse = await versioningAPI.createRepository({
          character_id: character.id,
          name: character.core?.name || 'Unnamed Character',
          description: `Character repository for ${character.core?.name || 'character'}`
        });
        
        console.log('✅ Repository created:', repoResponse.data);
        setRepository(repoResponse.data);
      }

      // Commit the character state
      const commitResponse = await versioningAPI.createCommit(
        repository?.id || character.id, 
        {
          message: `Character creation - Iteration ${iteration}`,
          character_data: character
        }
      );

      console.log('✅ Character committed:', commitResponse.data);
      setCommitted(true);
      
    } catch (e) {
      console.error('❌ Character commit error:', e);
      setError(`Error committing character: ${e.response?.data?.detail || e.message}`);
    }
    setIsLoading(false);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Create a New Character</h1>
      
      {/* Backend Connection Status */}
      <div className={`p-2 mb-4 rounded ${backendConnected ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>
        Backend Status: {backendConnected ? '✅ Connected' : '❌ Disconnected'}
        {!backendConnected && (
          <button 
            onClick={checkBackendConnection} 
            className="ml-2 px-2 py-1 bg-blue-600 text-white rounded text-sm"
          >
            Retry Connection
          </button>
        )}
      </div>

      {error && <div className="bg-red-200 text-red-800 p-2 mb-4 rounded">{error}</div>}
      
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <label className="block font-semibold">Character Description</label>
            <textarea 
              className="w-full p-2 rounded bg-gray-800 text-white" 
              value={description} 
              onChange={e => setDescription(e.target.value)} 
              rows={3}
              placeholder="Describe your character concept (e.g., 'A brave warrior from the northern mountains' or 'A cunning rogue with a mysterious past')"
            />
          </div>
          <div>
            <label className="block font-semibold">Level</label>
            <input 
              type="number" 
              min={1} 
              max={20} 
              className="w-24 p-2 rounded bg-gray-800 text-white" 
              value={level} 
              onChange={e => setLevel(Number(e.target.value))} 
            />
          </div>
          <div className="flex gap-4">
            <label>
              <input 
                type="checkbox" 
                checked={generateBackstory} 
                onChange={e => setGenerateBackstory(e.target.checked)} 
              /> Generate AI Backstory
            </label>
            <label>
              <input 
                type="checkbox" 
                checked={includeCustomContent} 
                onChange={e => setIncludeCustomContent(e.target.checked)} 
              /> Include Custom Content
            </label>
            <label>
              <input 
                type="checkbox" 
                checked={addInitialJournal} 
                onChange={e => setAddInitialJournal(e.target.checked)} 
              /> Add Initial Journal
            </label>
          </div>
          <button 
            className={`px-4 py-2 rounded text-white ${
              backendConnected && description.trim() 
                ? 'bg-blue-600 hover:bg-blue-700' 
                : 'bg-gray-400 cursor-not-allowed'
            }`}
            onClick={handleCreate} 
            disabled={isLoading || !backendConnected || !description.trim()}
          >
            {isLoading ? '🎲 Creating Character...' : '🎲 Create Character'}
          </button>
        </div>
      )}
      
      {step === 2 && character && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Review & Refine Character (Iteration {iteration})</h2>
          <div className="bg-gray-800 p-4 rounded">
            <p><strong>Name:</strong> {character.core?.name || character.name || 'Unnamed Character'}</p>
            <p><strong>Species:</strong> {character.core?.species || 'Unknown'}</p>
            <p><strong>Classes:</strong> {
              character.core?.character_classes 
                ? Object.entries(character.core.character_classes).map(([cls, lvl]) => `${cls} (Level ${lvl})`).join(', ')
                : 'No classes defined'
            }</p>
            <p><strong>Level:</strong> {character.core?.level || level}</p>
            <p><strong>Backstory:</strong> {character.backstory || 'No backstory generated'}</p>
            
            {/* Display API response structure for debugging */}
            <details className="mt-4">
              <summary className="cursor-pointer text-blue-400">🔍 View API Response (Debug)</summary>
              <pre className="text-xs bg-gray-900 p-2 mt-2 rounded overflow-auto max-h-40">
                {JSON.stringify(character, null, 2)}
              </pre>
            </details>
          </div>
          
          <div className="flex gap-2">
            <button 
              className="bg-yellow-600 hover:bg-yellow-700 px-4 py-2 rounded text-white" 
              onClick={handleIterate} 
              disabled={isLoading}
            >
              {isLoading ? '🔄 Refining...' : '🔄 Refine Character'}
            </button>
            <button 
              className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-white" 
              onClick={handleCommit} 
              disabled={isLoading}
            >
              {isLoading ? '💾 Committing...' : '💾 Commit to Repository'}
            </button>
          </div>
        </div>
      )}
      
      {committed && (
        <div className="bg-green-200 text-green-900 p-4 mt-4 rounded">
          🎉 Character committed to the versioning system! You can now view it in your character list or explore its development timeline.
        </div>
      )}
    </div>
  );
};

export default CharacterCreator;
