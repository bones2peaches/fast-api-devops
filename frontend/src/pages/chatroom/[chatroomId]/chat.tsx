import { useRouter } from "next/router";
import React from "react";
import Layout from "../../../components/Layout"; // Adjust the import path as necessary
import { GetServerSideProps, InferGetServerSidePropsType } from "next";
import { ApiClient } from "../../../clients/api";
import { useEffect, useState } from "react";
import SendMessageForm from "../../../components/SendMessageForum";
import { User } from "../../../types/user";

import Message from "@/components/Message";

interface ChatRoomDetails {
  id: string;
  name: string;
  category: string;
  created_at: Date;
  created_by: User;
}

interface MessageOut {
  text: string;
  sent: Date;
  likes: User[];
  dislikes: User[];
  sent_by: User;
  id: string;
  editted: boolean;
  deleted: boolean;
}

interface ChatRoomMessages {
  messages: MessageOut[];
}

interface ChatroomUsers {
  users: User[];
}

interface ChatRoomProps {
  token: string | null;
  userId: string | null;
  username: string | null;
  chatroomUsers: ChatroomUsers | null;
  chatRoomMessages: ChatRoomMessages | null;
  chatRoomDetails: ChatRoomDetails | null; // Add this line
}

const ChatRoomComponent: React.FC<ChatRoomProps> = ({
  token,
  userId,
  username,
  chatroomUsers,
  chatRoomMessages,
  chatRoomDetails,
}) => {
  const router = useRouter();
  const { chatroomId } = router.query;
  const [users, setUsers] = useState(chatroomUsers);

  const [messages, setMessages] = useState<MessageOut[]>(
    chatRoomMessages?.messages || []
  );

  const wsUrl = `ws://localhost/ws/chatroom/${chatroomId}/user`;
  console.log(wsUrl);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    // Initialize WebSocket connection
    const ws = new WebSocket(wsUrl, "ws+meta.nchan");
    ws.onmessage = (event) => {
      console.log(event);
      const jsonEvent = JSON.parse(event.data.split("\n\n")[1]);
      console.log(jsonEvent);
      setUsers(jsonEvent);
    };

    setWebsocket(ws);

    // Clean up on component unmount
    return () => ws && ws.close();
  }, [wsUrl]);

  const wsMessageUrl = `ws://localhost/ws/chatroom/${chatroomId}/message`;
  const [messageWebsocket, setMessageWebsocket] = useState<WebSocket | null>(
    null
  );
  useEffect(() => {
    // Initialize WebSocket connection
    const ws = new WebSocket(wsMessageUrl, "ws+meta.nchan");

    ws.onmessage = (event) => {
      console.log("New message event received:", event);
      const newMessage: MessageOut = JSON.parse(event.data.split("\n\n")[1]);
      console.log("Parsed new message:", newMessage);

      // Update the messages state to include the new message
      setMessages((prevMessages) => [...prevMessages, newMessage]);
    };

    setMessageWebsocket(ws);

    // Clean up on component unmount
    return () => ws.close();
  }, [wsMessageUrl]);

  const wsUpdateUrl = `ws://localhost/ws/chatroom/${chatroomId}/update`;
  const [updateWebsocket, setUpdateWebsocket] = useState<WebSocket | null>(
    null
  );
  useEffect(() => {
    const ws = new WebSocket(wsUpdateUrl, "ws+meta.nchan");

    ws.onmessage = (event) => {
      const updatedMessage: MessageOut = JSON.parse(
        event.data.split("\n\n")[1]
      );
      console.log("Update event received:", updatedMessage);
      setMessages((currentMessages) => {
        // Find the index of the message that needs to be updated
        const index = currentMessages.findIndex(
          (message) => message.id === updatedMessage.id
        );

        // If no message is found, just return the current messages without changes
        if (index === -1) {
          return currentMessages;
        }

        // Create a new array with the updated message
        const updatedMessages = [...currentMessages];
        updatedMessages[index] = updatedMessage;

        return updatedMessages;
      });
    };

    return () => ws.close();
  }, [wsUpdateUrl]);

  if (!token || !username) {
    return (
      <Layout username={null} userId={null} token={null}>
        <div className="py-10">
          <div className="max-w-md mx-auto bg-white shadow-lg rounded-lg p-8">
            <h2 className="mb-6 text-center text-3xl font-bold text-gray-900">
              Please Login to View the Chat Room
            </h2>
          </div>
        </div>
      </Layout>
    );
  }

  if (!chatRoomDetails) {
    return (
      <Layout username={username} userId={userId} token={token}>
        <div className="py-10">
          <div className="max-w-md mx-auto bg-white shadow-lg rounded-lg p-8">
            <h2 className="mb-6 text-center text-3xl font-bold text-gray-900">
              Chat Room Not Found
            </h2>
          </div>
        </div>
      </Layout>
    );
  } else {
    return (
      <Layout username={username} userId={userId} token={token}>
        <div className="flex flex-col md:flex-row justify-between space-x-0 md:space-x-4 py-10">
          <div className="md:w-1/4 p-8">
            <h1 className="text-3xl font-bold mb-2">{chatRoomDetails.name}</h1>
            <p className="text-sm mb-1">
              Category:{" "}
              <span className="text-gray-600">{chatRoomDetails.category}</span>
            </p>
            <p className="text-sm mb-1">
              Created at:{" "}
              <span className="text-gray-600">
                {new Date(chatRoomDetails.created_at).toLocaleDateString()}
              </span>
            </p>
            <p className="text-sm mb-1">
              Created by:{" "}
              <span className="text-gray-600">
                {chatRoomDetails.created_by.username}
              </span>
            </p>
          </div>
          <div className="flex flex-1 flex-col md:flex-row">
            <div className="md:w-1/4 bg-white shadow-lg rounded-lg p-4 m-2">
              <h3 className="text-lg font-semibold mb-4">Chatroom Users</h3>
              {users?.users.length ? (
                <ul className="list-none">
                  {users.users.map((user) => (
                    <li
                      key={user.id}
                      className={`mb-1 ${
                        user.online ? "text-green-500" : "text-gray-500"
                      }`}
                    >
                      {user.username}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No users in chatroom</p>
              )}
            </div>
            <div className="md:w-3/4 bg-white shadow-lg rounded-lg p-4 m-2">
              <h3 className="text-lg font-semibold mb-4">Messages</h3>
              {messages.length ? (
                <div className="md:w-3/4 bg-white shadow-lg rounded-lg p-4 m-2">
                  <h3 className="text-lg font-semibold mb-4">Messages</h3>
                  <div
                    className="overflow-y-auto"
                    style={{ maxHeight: "500px" }}
                  >
                    {messages.map((message) => (
                      <Message
                        key={message.id}
                        text={message.text}
                        sentBy={message.sent_by}
                        sentAt={message.sent}
                        view_user_id={userId}
                        messageId={message.id}
                        token={token}
                        chatroomId={chatroomId}
                        likes={message.likes}
                        dislikes={message.dislikes}
                        editted={message.editted}
                        deleted={message.deleted}
                      />
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">No messages in chatroom</p>
              )}
            </div>
          </div>
          <div className="md:w-1/4 m-2">
            <SendMessageForm token={token} chatroomId={chatroomId} />
          </div>
        </div>
      </Layout>
    );
  }
};

export default ChatRoomComponent;

// GetServerSideProps to fetch the data
export const getServerSideProps: GetServerSideProps<ChatRoomProps> = async (
  context
) => {
  // ... Your logic to get chatroomUsers and chatRoomMessages
  const chatroomUsers: ChatroomUsers | null = null; // Replace with actual data fetching logic
  const chatRoomMessages: ChatRoomMessages | null = null; // Replace with actual data fetching logic
  const token = context.req.cookies.session_token || null;
  const userId = context.req.cookies.user_id || null;
  const username = context.req.cookies.username || null;

  const apiClient = new ApiClient("http", "localhost", 5000);
  const chatroomId = context.params?.chatroomId;
  const chatRoomDetails: ChatRoomDetails | null = await apiClient.getChatroom(
    token,
    chatroomId
  );

  return {
    props: {
      token,
      userId,
      username,
      chatroomUsers,
      chatRoomMessages,
      chatRoomDetails,
    },
  };
};
