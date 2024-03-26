// components/LoginForm.tsx
import React, { useState } from "react";
import { ApiClient } from "../clients/api";
import { useRouter } from "next/navigation";

const LoginForm: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const apiClient = new ApiClient("http", "localhost", 5000);

    // Clear any previous message
    setMessage(null);

    const response = await apiClient.createSession(username, password);
    console.log(response.detail);
    if ("detail" in response) {
      setMessage(`Error: ${response.detail}`);
    } else {
      // Success
      router.push("/");
      // Optionally clear form or redirect user
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg overflow-hidden md:max-w-lg">
      <div className="md:flex">
        <div className="w-full p-4 px-5 py-5">
          <h2 className="text-center text-3xl font-semibold text-gray-800 mb-4">
            Create an Account
          </h2>

          <form onSubmit={handleSubmit}>
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-gray-700"
              >
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="h-12 mt-2 px-3 w-full border-2 border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="mt-4">
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700"
              >
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="h-12 mt-2 px-3 w-full border-2 border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="mt-6">
              <button
                type="submit"
                className="py-2 w-full bg-indigo-600 hover:bg-indigo-700 rounded-md text-white text-lg"
                data-testid="create-account-submit"
              >
                Create Account
              </button>
            </div>
            {message && (
              <div className="text-center font-medium">{message}</div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
