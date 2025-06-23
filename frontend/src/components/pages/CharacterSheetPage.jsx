import React, { useState, useEffect } from 'react';

const CharacterSheetPage = () => {
  const [character, setCharacter] = useState(null);
  const [isDM, setIsDM] = useState(false); // TODO: Replace with real auth/role check

  useEffect(() => {
    // TODO: Fetch character data from backend
    // setCharacter(response.data);
  }, []);

  const handleApproveEvolution = () => {
    // TODO: Call backend to approve character evolution
    alert('Character evolution approved!');
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Character Sheet</h1>
      {/* Character sheet UI and controls for in-game state */}
      {character ? (
        <div>
          <h2 className="text-xl font-semibold">{character.name}</h2>
          {/* ...other character details... */}
          {isDM && (
            <button className="bg-green-600 px-4 py-2 rounded text-white mt-4" onClick={handleApproveEvolution}>
              Approve Evolution
            </button>
          )}
        </div>
      ) : (
        <p>Loading character sheet...</p>
      )}
    </div>
  );
};

export default CharacterSheetPage;
