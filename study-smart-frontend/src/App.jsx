import React, { useEffect, useState } from "react";
import Login from "./components/Login";
import SchedulePage from "./components/SchedulePage";

function App() {
  const [token, setToken] = useState(null);
  const [userId, setUserId] = useState(null);

  // Rehydrate token from localStorage on load
  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedUserId = localStorage.getItem("userId");
    if (savedToken && savedUserId) {
      setToken(savedToken);
      setUserId(savedUserId);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    setToken(null);
    setUserId(null);
  };

  const handleResetSchedule = () => {
    setUserId((prev) => prev);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 to-sky-200 text-gray-800 font-sans">
      {!token ? (
        <Login onLogin={(t, id) => {
          setToken(t);
          setUserId(id);
        }} />
      ) : (
        <SchedulePage
          token={token}
          userId={userId}
          onLogout={handleLogout}
          onReset={handleResetSchedule}
        />
      )}
    </div>
  );
}

export default App;
