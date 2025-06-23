import React, { useState } from 'react';
// import { createCharacter, updateCharacter, commitCharacter } from '../../services/api'; // Example API functions

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

  // Step 1: User inputs
  const handleCreate = async () => {
    setIsLoading(true);
    setError('');
    try {
      // Replace with real API call
      // const result = await createCharacter({ description, level, generateBackstory, includeCustomContent, addInitialJournal });
      const result = { success: true, data: { core: { name: 'Example', species: 'Human', character_classes: { Fighter: 1 } }, sheet: {}, backstory: 'A mysterious past...', custom_content: {}, journal: { entries: [], summary: '' }, managers: {} } };
      if (result.success) {
        setCharacter(result.data);
        setStep(2);
        setIteration(iteration + 1);
      } else {
        setError(result.error || 'Character creation failed.');
      }
    } catch (e) {
      setError('Error creating character.');
    }
    setIsLoading(false);
  };

  // Step 2: User tweaks and iterates
  const handleIterate = async () => {
    setIsLoading(true);
    setError('');
    try {
      // Replace with real API call for update/tweak
      // const result = await updateCharacter(character);
      const result = { success: true, data: { ...character, core: { ...character.core, name: character.core.name + ' (Tweaked)' } } };
      if (result.success) {
        setCharacter(result.data);
        setIteration(iteration + 1);
      } else {
        setError(result.error || 'Character update failed.');
      }
    } catch (e) {
      setError('Error updating character.');
    }
    setIsLoading(false);
  };

  // Step 3: Commit character
  const handleCommit = async () => {
    setIsLoading(true);
    setError('');
    try {
      // Replace with real API call for commit
      // const result = await commitCharacter(character);
      const result = { success: true };
      if (result.success) {
        setCommitted(true);
      } else {
        setError(result.error || 'Commit failed.');
      }
    } catch (e) {
      setError('Error committing character.');
    }
    setIsLoading(false);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Create a New Character</h1>
      {error && <div className="bg-red-200 text-red-800 p-2 mb-4 rounded">{error}</div>}
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <label className="block font-semibold">Character Description</label>
            <textarea className="w-full p-2 rounded bg-gray-800 text-white" value={description} onChange={e => setDescription(e.target.value)} rows={3} />
          </div>
          <div>
            <label className="block font-semibold">Level</label>
            <input type="number" min={1} max={20} className="w-24 p-2 rounded bg-gray-800 text-white" value={level} onChange={e => setLevel(Number(e.target.value))} />
          </div>
          <div className="flex gap-4">
            <label><input type="checkbox" checked={generateBackstory} onChange={e => setGenerateBackstory(e.target.checked)} /> Generate Backstory</label>
            <label><input type="checkbox" checked={includeCustomContent} onChange={e => setIncludeCustomContent(e.target.checked)} /> Include Custom Content</label>
            <label><input type="checkbox" checked={addInitialJournal} onChange={e => setAddInitialJournal(e.target.checked)} /> Add Initial Journal</label>
          </div>
          <button className="bg-blue-600 px-4 py-2 rounded text-white" onClick={handleCreate} disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Create Character'}
          </button>
        </div>
      )}
      {step === 2 && character && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Review & Tweak Character (Iteration {iteration})</h2>
          <div className="bg-gray-800 p-4 rounded">
            <p><strong>Name:</strong> {character.core.name}</p>
            <p><strong>Species:</strong> {character.core.species}</p>
            <p><strong>Classes:</strong> {Object.entries(character.core.character_classes).map(([cls, lvl]) => `${cls} (Level ${lvl})`).join(', ')}</p>
            <p><strong>Backstory:</strong> {character.backstory}</p>
            {/* Add more fields and allow user to tweak as needed */}
          </div>
          <button className="bg-yellow-600 px-4 py-2 rounded text-white mr-2" onClick={handleIterate} disabled={isLoading}>
            {isLoading ? 'Updating...' : 'Tweak & Iterate'}
          </button>
          <button className="bg-green-600 px-4 py-2 rounded text-white" onClick={handleCommit} disabled={isLoading}>
            {isLoading ? 'Committing...' : 'Commit Character'}
          </button>
        </div>
      )}
      {committed && (
        <div className="bg-green-200 text-green-900 p-4 mt-4 rounded">
          Character committed to the database! You can now view it in your character list.
        </div>
      )}
    </div>
  );
};

export default CharacterCreator;
