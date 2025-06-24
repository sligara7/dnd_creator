import React, { useState, useEffect } from 'react';
import { characterAPI } from '../../services/api';

const CharacterList = () => {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCharacters();
  }, []);

  const fetchCharacters = async () => {
    try {
      setLoading(true);
      const response = await characterAPI.getAll();
      setCharacters(response.data);
    } catch (e) {
      setError(`Failed to load characters: ${e.response?.data?.detail || e.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-4">Loading characters...</div>;
  }

  if (error) {
    return <div className="p-4 bg-red-200 text-red-800 rounded">{error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Your Characters</h1>
      {characters.length === 0 ? (
        <p>No characters found. Create your first character!</p>
      ) : (
        <div className="grid gap-4">
          {characters.map((character) => (
            <div key={character.id} className="bg-gray-800 p-4 rounded">
              <h3 className="text-lg font-semibold">{character.core?.name || 'Unnamed Character'}</h3>
              <p>{character.core?.species} {Object.keys(character.core?.character_classes || {}).join(', ')}</p>
              <p>Level {character.core?.level || 1}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CharacterList;
