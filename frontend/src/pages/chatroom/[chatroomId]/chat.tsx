import { useRouter } from "next/router";
import React from "react";
import Layout from "../../../components/Layout"; // Adjust the import path as necessary
import { GetServerSideProps, InferGetServerSidePropsType } from "next";
import { ApiClient } from "../../../clients/api";
import { useEffect, useState } from "react";
import SendMessageForm from "../../../components/SendMessageForum";
import { User } from "../../../types/user";

import Message from "@/components/Message";
import { join } from "path";

interface OnlineCount {
  online: number;
  offline: number;
}

interface ChatRoomDetails {
  id: string;
  name: string;
  category: string;
  created_at: Date;
  created_by: User;
  count: OnlineCount;
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

interface ChatRoomProps {
  token: string | null;
  userId: string | null;
  username: string | null;
  cookies: any;
  chatroomUsers: any | null;
  chatRoomMessages: ChatRoomMessages | null;
  chatRoomDetails: ChatRoomDetails | null;
  currentTime: string; // Add this line
}

const ChatRoomComponent: React.FC<ChatRoomProps> = ({
  token,
  userId,
  username,
  cookies,
  chatroomUsers,
  chatRoomMessages,
  chatRoomDetails,
  currentTime,
}) => {
  const router = useRouter();

  const { chatroomId } = router.query;
  const [users, setUsers] = useState(chatroomUsers);
  const [online, setOnline] = useState(0);
  const [showingUsers, setShowingUsers] = useState<boolean>(false);
  const [offline, setOffline] = useState(0);
  const [messages, setMessages] = useState<MessageOut[]>(
    chatRoomMessages?.messages || []
  );

  const showUserButtonText = showingUsers ? "Hide Users" : "Show Users";

  const [userPage, setUserPage] = useState<number>(1);
  const [joinTime, setJoinTime] = useState<Date>(new Date(currentTime));
  const [totalPages, setTotalPages] = useState<number>(0);
  const apiClient = new ApiClient("http", "localhost", 5000);

  const handleNextPage = () => {
    if (userPage < totalPages) {
      setUserPage(userPage + 1);
    }
  };

  const handlePreviousPage = () => {
    if (userPage > 1) {
      setUserPage(userPage - 1);
    }
  };

  const loadUsers = async (page: number) => {
    try {
      const response = await apiClient.getChatroomUsers(
        token,
        chatroomId,
        page,
        5 // Assuming this is the per_page value
      );
      setUsers(response.items);
      setTotalPages(response.total_pages);
      setUserPage(response.current_page);
      setShowingUsers(true); // Show users after loading
    } catch (error) {
      console.error("Failed to fetch users:", error);
    }
  };

  // Load users when the component mounts or userPage changes
  useEffect(() => {
    loadUsers(userPage);
  }, [userPage, online, offline]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    // Initialize the API client

    if (!showingUsers) {
      const response = await apiClient.getChatroomUsers(
        token,
        chatroomId,
        userPage,
        5
      );

      setUsers(response.items);

      setShowingUsers(true);
    } else {
      setUsers([]);

      setShowingUsers(false);
    }
  };

  const wsUrl = `ws://localhost/ws/chatroom/${chatroomId}`;

  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  useEffect(() => {
    const ws = new WebSocket(wsUrl, "ws+meta.nchan");
    const joinTime = new Date(); // Correctly capture the join time here

    ws.onopen = () => {
      console.log("WebSocket connection established at", currentTime);
      // No need to set joinTime here since it's derived from props
    };

    ws.onmessage = (event) => {
      const jsonEvent = JSON.parse(event.data.split("\n\n")[1]);

      if (jsonEvent.event === "user") {
        setUsers(jsonEvent.data);
        console.log(jsonEvent);
      } else if (jsonEvent.event === "message") {
        setMessages((prevMessages) => [...prevMessages, jsonEvent.data]);
      } else if (jsonEvent.event === "update") {
        setMessages((currentMessages) => {
          const updatedMessage: MessageOut = jsonEvent.data;
          const index = currentMessages.findIndex(
            (message) => message.id === updatedMessage.id
          );

          if (index === -1) {
            return currentMessages;
          }

          const updatedMessages = [...currentMessages];
          updatedMessages[index] = updatedMessage;

          return updatedMessages;
        });
      } else if (jsonEvent.event === "count_update") {
        console.log(jsonEvent.data.chatrooms);
        if (jsonEvent.data.chatrooms) {
          jsonEvent.data.chatrooms.forEach(
            (chatroom: {
              chatroom_id: string;
              online: number;
              offline: number;
            }) => {
              // Check if this chatroom's ID matches the one you're interested in
              if (chatroom.chatroom_id === chatroomId) {
                // Update your component's state with the online and offline counts
                setOnline(chatroom.online);
                setOffline(chatroom.offline);
              }
            }
          );
        }
      }
    };

    setWebsocket(ws);

    // Clean up on component unmount
    return () => {
      ws.close();
    };
  }, [wsUrl]);

  if (!token || !username) {
    return (
      <Layout username={null} userId={null} token={null} cookies={cookies}>
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
      <Layout
        username={username}
        userId={userId}
        token={token}
        cookies={cookies}
      >
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
      <Layout
        username={username}
        userId={userId}
        token={token}
        cookies={cookies}
      >
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
              <button
                onClick={handleSubmit}
                type="submit"
                className="py-2 px-4 w-full bg-indigo-600 hover:bg-indigo-700 rounded-md text-white text-lg"
              >
                {showUserButtonText}
              </button>

              <div>
                {showingUsers ? (
                  <div>
                    {userPage > 1 && (
                      <button
                        onClick={handlePreviousPage}
                        className="py-2 px-4 mr-2 bg-indigo-600 hover:bg-indigo-700 rounded-md text-white text-lg"
                      >
                        Previous Page
                      </button>
                    )}
                    {userPage < totalPages && (
                      <button
                        onClick={handleNextPage}
                        className="py-2 px-4 bg-indigo-600 hover:bg-indigo-700 rounded-md text-white text-lg"
                      >
                        Next Page
                      </button>
                    )}
                  </div>
                ) : null}
              </div>

              <div> online : {online}</div>
              <div>offline : {offline}</div>

              <ul className="list-none">
                {users?.map((user: any) => (
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
  const chatroomUsers: any | null = null; // Replace with actual data fetching logic
  const chatRoomMessages: ChatRoomMessages | null = null; // Replace with actual data fetching logic
  const token = context.req.cookies.session_token || null;
  const userId = context.req.cookies.user_id || null;
  const username = context.req.cookies.username || null;
  const cookies = context.req.cookies;

  const apiClient = new ApiClient("http", "localhost", 5000);
  const chatroomId = context.params?.chatroomId;
  const chatRoomDetails: ChatRoomDetails | null = await apiClient.getChatroom(
    token,
    chatroomId
  );
  const currentTime = new Date().toISOString();

  return {
    props: {
      token,
      userId,
      username,
      chatroomUsers,
      chatRoomMessages,
      chatRoomDetails,
      cookies,
      currentTime,
    },
  };
};
