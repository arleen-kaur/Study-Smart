import React, { useState } from "react";
import { login, signup, getUserInfo } from "../services/api";

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isSignup, setIsSignup] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      if (isSignup) {
        await signup(username, password);
      }

      const token = await login(username, password);
      const userInfo = await getUserInfo(token);
      onLogin(token, userInfo.id);
    } catch (err) {
      if (isSignup && err.response?.status === 400) {
        setError("Username already taken.");
      } else if (!isSignup && err.response?.status === 401) {
        setError("Incorrect username or password.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-100 to-sky-200 px-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white w-full max-w-md rounded-3xl shadow-xl p-8 border border-indigo-100 transition-transform duration-300 hover:scale-[1.01]"
      >
        <h2 className="text-4xl font-extrabold text-indigo-700 mb-6 text-center drop-shadow-sm tracking-tight">
          {isSignup ? "Create Account" : "Study Smart"}
        </h2>

        <div className="space-y-4">
          {error && (
            <div className="bg-rose text-rose-700 border border-red-300 text-sm p-3 rounded-lg">
              {error}
            </div>
          )}

          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400 focus:outline-none"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400 focus:outline-none"
            required
          />

          <button
            type="submit"
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl font-semibold transition-transform hover:scale-[1.01] shadow-md"
          >
            {isSignup ? "Create Account" : "Login →"}
          </button>

          <p className="text-center text-sm text-gray-600 mt-3">
            {isSignup ? "Already have an account?" : "New user?"}{" "}
            <button
              type="button"
              onClick={() => {
                setIsSignup(!isSignup);
                setError("");
              }}
              className="text-indigo-600 font-semibold underline"
            >
              {isSignup ? "Log in" : "Create one"}
            </button>
          </p>
        </div>
      </form>
    </div>
  );
}

export default Login;
