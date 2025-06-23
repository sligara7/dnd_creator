import React, { useEffect, useState } from 'react';
import DMCharacterApproval from '../DM/DMCharacterApproval';

const DMDashboard = ({ isBackendConnected }) => {
  const [pendingCharacters, setPendingCharacters] = useState([]);

  useEffect(() => {
    if (isBackendConnected) {
      // TODO: Fetch pending character creations from backend
      // setPendingCharacters(response.data);
    }
  }, [isBackendConnected]);

  const handleApprove = (characterId) => {
    // TODO: Call backend to approve character
    setPendingCharacters(pendingCharacters.filter(c => c.id !== characterId));
  };

  const handleReject = (characterId) => {
    // TODO: Call backend to reject character
    setPendingCharacters(pendingCharacters.filter(c => c.id !== characterId));
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">DM Dashboard</h1>
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Pending Character Approvals</h2>
        {pendingCharacters.length === 0 ? (
          <p>No characters pending approval.</p>
        ) : (
          pendingCharacters.map(character => (
            <DMCharacterApproval
              key={character.id}
              character={character}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          ))
        )}
      </section>
      <section>
        <h2 className="text-xl font-semibold mb-2">Content Creation</h2>
        <ul className="list-disc ml-6">
          <li><a href="/create-spell" className="text-blue-400 hover:underline">Create Spell</a></li>
          <li><a href="/create-item" className="text-blue-400 hover:underline">Create Weapon/Armor</a></li>
          <li><a href="/create-npc" className="text-blue-400 hover:underline">Create NPC</a></li>
          <li><a href="/create-creature" className="text-blue-400 hover:underline">Create Creature</a></li>
        </ul>
      </section>
    </div>
  );
};

export default DMDashboard;
