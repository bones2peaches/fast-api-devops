// components/SendMessageForm.tsx
import React, { useState } from "react";
import { useRouter } from "next/router";
import { ApiClient } from "../clients/api"; // Assume this client is set up for handling API requests
import Message from "./Message";

interface Props {
  token: string | null;
  chatroomId: string | any;
}

const SendMessageForm: React.FC<Props> = ({ token, chatroomId }) => {
  const [messageText, setMessageText] = useState("");
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    // Initialize the API client
    const apiClient = new ApiClient("http", "localhost", 80);

    // Clear any previous feedback message
    setFeedbackMessage(null);

    try {
      const response = await apiClient.sendMessage(
        token,
        chatroomId,
        messageText
      );
      // Assuming response contains a status indicating success or error
      if ([200, 201, 202].includes(response.status)) {
        setFeedbackMessage("Message sent successfully.");
        // Optionally, clear the message text field on successful send
        setMessageText("");
      } else {
        // Handle different types of errors accordingly
        console.log(response.status);
        setFeedbackMessage(
          response.errorMessage ||
            "An error occurred while sending the message."
        );
      }
    } catch (error) {
      console.error("SendMessageForm error:", error);
      setFeedbackMessage("An unexpected error occurred.");
    }
  };

  return (
    <div className="max-w-md mx-auto my-10 bg-white rounded-lg shadow-md">
      <form onSubmit={handleSubmit} className="p-5">
        <div>
          <label
            htmlFor="messageText"
            className="block text-sm font-medium text-gray-700"
          >
            Your Message
          </label>
          <textarea
            id="messageText"
            name="messageText"
            required
            rows={4}
            className="mt-2 p-3 w-full border-2 border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
          ></textarea>
        </div>
        <div className="mt-6">
          <button
            type="submit"
            className="py-2 px-4 w-full bg-indigo-600 hover:bg-indigo-700 rounded-md text-white text-lg"
          >
            Send Message
          </button>
        </div>
        {feedbackMessage && (
          <div className="mt-4 text-center text-sm font-medium text-gray-700">
            {feedbackMessage}
          </div>
        )}
      </form>
    </div>
  );
};

export default SendMessageForm;
