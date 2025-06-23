import React from 'react';

const DMCharacterApproval = ({ character, onApprove, onReject }) => (
  <div className="bg-gray-800 p-4 rounded mb-4">
    <h2 className="text-xl font-bold mb-2">{character.name}</h2>
    <p>Class: {character.class}</p>
    <p>Level: {character.level}</p>
    {/* Add more character details as needed */}
    <div className="mt-2 flex gap-2">
      <button className="bg-green-600 px-3 py-1 rounded text-white" onClick={() => onApprove(character.id)}>Approve</button>
      <button className="bg-red-600 px-3 py-1 rounded text-white" onClick={() => onReject(character.id)}>Reject</button>
    </div>
  </div>
);

export default DMCharacterApproval;
