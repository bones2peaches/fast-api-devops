import React from "react";
import Link from "next/link";
import Layout from "../../components/Layout"; // Adjust the import path as necessary
import { GetServerSideProps, InferGetServerSidePropsType } from "next";
import { ApiClient } from "../../clients/api";
import { useRouter } from "next/navigation";

interface ChatRoom {
  id: string;
  name: string;
  category: string;
  created_at: string;
  joined: boolean;
  created_by: {
    username: string;
    id: string;
    online: boolean;
  };
}

interface ChatRoomsPageProps {
  chatRooms: ChatRoom[];
  page: number;
  totalPages: number;
  token: string | null;
  userId: string | null;
  username: string | null;
  cookies: any;
}

const ChatRoomsPage: React.FC<ChatRoomsPageProps> = ({
  chatRooms,
  username,
  userId,
  token,
  page,
  totalPages,
  cookies,
}) => {
  const router = useRouter();
  const changePage = (newPage: number) => {
    router.push(`?page=${newPage}`);
  };

  const joinChatRoom = async (roomId: string, joined: boolean) => {
    console.log("Joining chat room:", roomId);

    // Initialize your API client
    const apiClient = new ApiClient("http", "localhost", 80);

    if (joined === false) {
      const joinRoom = await apiClient.joinChatroom(token, roomId);
    }
    router.push(`/chatroom/${roomId}/chat`);
  };

  return (
    <Layout username={username} userId={userId} token={token} cookies={cookies}>
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Chat Rooms</h1>
        {chatRooms.map((room) => (
          <div key={room.id} className="mb-2 p-4 border rounded shadow-sm">
            <h2 className="text-xl font-semibold">{room.name}</h2>
            <p>Category: {room.category}</p>
            <p>Created by: {room.created_by.username}</p>
            <p>Joined: {room.joined ? "Yes" : "No"}</p>
            <button
              onClick={() => joinChatRoom(room.id, room.joined)}
              className="mt-2 inline-block bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
            >
              Join
            </button>
          </div>
        ))}
      </div>
      <div className="mt-4">
        <div className="flex justify-between items-center">
          <button
            onClick={() => changePage(page - 1)}
            disabled={page <= 1}
            className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:bg-blue-300"
          >
            Previous
          </button>
          <span>
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => changePage(page + 1)}
            disabled={page >= totalPages}
            className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:bg-blue-300"
          >
            Next
          </button>
        </div>
      </div>
    </Layout>
  );
};

export default ChatRoomsPage;

export const getServerSideProps: GetServerSideProps<
  ChatRoomsPageProps
> = async (context) => {
  const page = context.query.page || 1; // Default to page 1 if no page query parameter is provided
  const perPage = 5; // Set how many items per page you want
  const token = context.req.cookies.session_token || null;
  const userId = context.req.cookies.user_id || null;
  const username = context.req.cookies.username || null;
  const cookies = context.req.cookies;
  const apiClient = new ApiClient("http", "localhost", 5000);
  const chatRooms = await apiClient.getChatrooms(token, page, perPage);
  console.log(chatRooms);

  return {
    props: {
      chatRooms: chatRooms.items,
      page: Number(page),
      totalPages: chatRooms.total_pages,
      token,
      userId,
      username,
      cookies, // Assuming the API returns the total number of pages
    },
  };
};
