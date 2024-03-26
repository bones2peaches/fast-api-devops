// components/CreateChatRoom.tsx
import React, { useState } from "react";
import { ApiClient } from "../clients/api";
import { useRouter } from "next/router";

interface Props {
  token: string | null;
}

const CreateChatRoom: React.FC<Props> = ({ token }) => {
  const [name, setName] = useState("");
  const [category, setCategory] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const router = useRouter();
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const apiClient = new ApiClient("http", "localhost", 5000);

    // Clear any previous message
    setMessage(null);

    const response = await apiClient.createChatroom(token, name, category);
    console.log(response.detail);
    if ("dup" === response) {
      setMessage(
        `Error: there is all ready a chatroom with ${name}, try another`
      );
    } else {
      router.push(`/chatroom/${response["id"]}/chat`);

      // Optionally clear form or redirect user
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg overflow-hidden md:max-w-lg">
      <div className="md:flex">
        <div className="w-full p-4 px-5 py-5">
          <form onSubmit={handleSubmit}>
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-gray-700"
              >
                Chat Room Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                className="h-12 mt-2 px-3 w-full border-2 border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="mt-4">
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700"
              >
                Chat Room Category
              </label>
              <input
                id="category"
                name="category"
                type="text"
                required
                className="h-12 mt-2 px-3 w-full border-2 border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
            </div>
            <div className="mt-6">
              <button
                type="submit"
                className="py-2 w-full bg-indigo-600 hover:bg-indigo-700 rounded-md text-white text-lg"
                data-testid="create-account-submit"
              >
                Create Chat Room
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

export default CreateChatRoom;
