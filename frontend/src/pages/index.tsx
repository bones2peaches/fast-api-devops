import Layout from "../components/Layout";
import { GetServerSideProps, InferGetServerSidePropsType } from "next";

// Define the props that HomePage will receive
type HomePageProps = {
  token: string | null;
  userId: string | null;
  username: string | null;
};

const HomePage = ({ token, userId, username }: HomePageProps) => {
  return (
    <Layout username={username} token={token} userId={userId}>
      <h2 className="text-2xl font-bold">Home Page</h2>
      <p>This is the content of the home page.</p>
    </Layout>
  );
};

export default HomePage;

// Type the `context` parameter with `GetServerSideProps`
export const getServerSideProps: GetServerSideProps<HomePageProps> = async (
  context
) => {
  // Extract the token from the cookie in the request
  const token = context.req.cookies.session_token || null;
  const userId = context.req.cookies.user_id || null;
  const username = context.req.cookies.username || null;

  console.log(context.req.headers.cookie);
  // Use the token to fetch data or verify the user session
  // ...

  return {
    props: {
      token,
      userId,
      username, // Pass the token to the component
    },
  };
};
