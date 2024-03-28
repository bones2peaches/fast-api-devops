import React, { ReactNode } from "react";
import Link from "next/link";
import ApiClient from "@/clients/api";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

interface LayoutProps {
  children: ReactNode;
  username: string | null;
  userId: string | null;
  token: string | null;
  cookies: any;
}

const Layout: React.FC<LayoutProps> = ({
  children,
  username,
  token,
  userId,
  cookies,
}) => {
  const router = useRouter();

  const [showExpiryWarning, setShowExpiryWarning] = useState(false);

  useEffect(() => {
    const checkTokenExpiry = () => {
      // Ensure cookies object is available and expiry is defined
      if (cookies && cookies.expiry) {
        const expiryDate = new Date(cookies.expiry);
        expiryDate.setHours(expiryDate.getHours() - 4);
        const currentDate = new Date();
        const timeLeft = expiryDate.getTime() - currentDate.getTime();

        // If there's less than a minute left, show the expiry warning
        if (timeLeft < 60000 && timeLeft > 0) {
          setShowExpiryWarning(true);
          setToken(null);
          setUsername(null);
          setUserId(null);
        } else {
          setShowExpiryWarning(false);
        }
      }
    };

    // Check the token expiry every second
    const intervalId = setInterval(checkTokenExpiry, 1000);

    // Clean up the interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  const [_token, setToken] = useState<any>(token);
  const [loggedIn, setLoggedIn] = useState<boolean>(!!token);
  const [_username, setUsername] = useState<any>(username);
  const [_userId, setUserId] = useState<any>(userId);

  const logout = async () => {
    if (token) {
      try {
        // Assuming your ApiClient and deleteSession method return a Promise.
        const apiClient = new ApiClient("http", "localhost", 5000);
        const LogOut = await apiClient.deleteSession(token);
        if (!LogOut) {
          setToken(null);
          setUsername(null);
          setUserId(null);

          router.push("/");
        }
      } catch (error) {}
    }

    setLoggedIn(false);

    // Since we're awaiting the logout, this is a good place to redirect.
    router.push("/");
  };
  return (
    <div className="flex flex-col min-h-screen">
      {/* Your session expiry warning message */}
      {showExpiryWarning && (
        <div className="fixed top-0 left-0 right-0 bg-red-600 text-white text-center py-10 z-100">
          Your session is about to expire. Please log in again.
          <Link href="/login">
            <p className="hover:text-blue-300">Click Here to Login</p>
          </Link>
        </div>
      )}
      <header className="bg-blue-500 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-semibold">My Application</h1>
          <nav>
            <ul className="flex space-x-4">
              <li>
                <Link href="/">
                  <p className="hover:text-blue-300">Home</p>
                </Link>
              </li>
              {_username ? (
                <>
                  <li>
                    <a
                      onClick={logout}
                      className="hover:text-blue-300 cursor-pointer"
                    >
                      Logout
                    </a>
                  </li>
                  <li>{_username}</li>
                  <Link href="/chatroom/create">
                    <p className="hover:text-blue-300">Create Chat Room</p>
                  </Link>
                  <Link href="/chatroom/find">
                    <p className="hover:text-blue-300">Discover Chatroom</p>
                  </Link>
                </>
              ) : (
                <li>
                  <Link href="/login">
                    <p className="hover:text-blue-300">Login</p>
                  </Link>
                  <Link href="/create">
                    <p className="hover:text-blue-300">Create An Account</p>
                  </Link>
                </li>
              )}
              <li>
                <Link href="/contact">
                  <p className="hover:text-blue-300">Contact</p>
                </Link>
              </li>
            </ul>
          </nav>
        </div>
      </header>

      <main className="flex-1 p-4">{children}</main>

      <footer className="bg-gray-700 text-white p-4">
        <p className="container mx-auto">Footer Content</p>
      </footer>
    </div>
  );
};

export default Layout;
