import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, RefreshCw } from 'lucide-react';

const BackendStatus = () => {
  const [isConnected, setIsConnected] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const [lastCheck, setLastCheck] = useState(null);

  const checkBackendHealth = async () => {
    setIsChecking(true);
    try {
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        timeout: 5000
      });
      setIsConnected(response.ok);
      setLastCheck(new Date().toLocaleTimeString());
    } catch (error) {
      console.warn('Backend health check failed:', error);
      setIsConnected(false);
      setLastCheck(new Date().toLocaleTimeString());
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkBackendHealth();
    // Check every 30 seconds
    const interval = setInterval(checkBackendHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    if (isConnected === null) return 'text-gray-500';
    return isConnected ? 'text-green-600' : 'text-red-600';
  };

  const getStatusIcon = () => {
    if (isChecking) return <RefreshCw className="w-4 h-4 animate-spin" />;
    if (isConnected === null) return <RefreshCw className="w-4 h-4" />;
    return isConnected ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />;
  };

  const getStatusText = () => {
    if (isChecking) return 'Checking...';
    if (isConnected === null) return 'Unknown';
    return isConnected ? 'Connected' : 'Disconnected';
  };

  return (
    <div className="flex items-center space-x-2 text-sm">
      <span className="text-gray-600">Backend:</span>
      <div className={`flex items-center space-x-1 ${getStatusColor()}`}>
        {getStatusIcon()}
        <span>{getStatusText()}</span>
      </div>
      {lastCheck && (
        <span className="text-xs text-gray-500">
          (Last check: {lastCheck})
        </span>
      )}
      <button
        onClick={checkBackendHealth}
        disabled={isChecking}
        className="text-blue-600 hover:text-blue-800 text-xs underline"
      >
        Refresh
      </button>
    </div>
  );
};

export default BackendStatus;
