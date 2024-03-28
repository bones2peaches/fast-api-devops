// pages/create-account.tsx
import React from "react";
import CreateChatRoom from "../../components/CreateChatRoom";
import Layout from "../../components/Layout"; // Make sure to import Layout
import { GetServerSideProps, InferGetServerSidePropsType } from "next";

type HomePageProps = {
  token: string | null;
  userId: string | null;
  username: string | null;
  cookies: any;
};

const CreateChatRoomPage: React.FC<HomePageProps> = ({
  token,
  userId,
  username,
  cookies,
}) => {
  if (token === null) {
    // User is not logged in, prompt to login
    return (
      <Layout username={null} userId={null} token={null} cookies={null}>
        <div className="py-10">
          <div className="max-w-md mx-auto bg-white shadow-lg rounded-lg p-8">
            <h2 className="mb-6 text-center text-3xl font-bold text-gray-900">
              Please Login To Create a Chat Room
            </h2>
          </div>
        </div>
      </Layout>
    );
  } else {
    // User is logged in, show the chat room creation form
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
              Create a Chat Room
            </h2>
            {/* Make sure the CreateChatRoom component is imported and token is a valid prop */}
            <CreateChatRoom token={token} />
          </div>
        </div>
      </Layout>
    );
  }
};

export default CreateChatRoomPage;

export const getServerSideProps: GetServerSideProps<HomePageProps> = async (
  context
) => {
  // Extract the token from the cookie in the request
  const token = context.req.cookies.session_token || null;
  const userId = context.req.cookies.user_id || null;
  const username = context.req.cookies.username || null;
  const cookies = context.req.cookies;

  // Use the token to fetch data or verify the user session
  // ...

  return {
    props: {
      token,
      userId,
      username,
      cookies, // Pass the token to the component
    },
  };
};
