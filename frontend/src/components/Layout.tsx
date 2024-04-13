import React, { ReactNode } from "react";
import Link from "next/link";
import ApiClient from "@/clients/api";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { FiBell } from "react-icons/fi";
interface LayoutProps {
  children: ReactNode;
  username: string | null;
  userId: string | null;
  token: string | null;
  cookies: any;
}

interface Notification {
  type: string | null;
  userId: string | null;
  id: string | null;
  chatroomId: string | null;
  text: string | null;
  read: boolean | null;
  createdAt: any;
}

const Layout: React.FC<LayoutProps> = ({
  children,
  username,
  token,
  userId,
  cookies,
}) => {
  const router = useRouter();
  const [eventSource, setEventSource] = useState<EventSource | null>(null);
  const [showExpiryWarning, setShowExpiryWarning] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [transientNotification, setTransientNotification] = useState("");
  const [showTransientNotification, setShowTransientNotification] =
    useState(false);

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

  const handleNotificationClick = async (notification: any) => {
    try {
      // Assuming your ApiClient and deleteSession method return a Promise.
      const apiClient = new ApiClient("http", "localhost", 5000);
      const update = await apiClient.updateNotification(token, notification.id);
      setNotifications((prevNotifications) =>
        prevNotifications.filter((n) => n.id !== notification.id)
      );

      router.push(`/chatroom/${notification.chatroomId}/chat`);
    } catch (error) {}
  };

  useEffect(() => {
    if (userId && token) {
      const newEventSource = new EventSource(
        `http://localhost/sse/notifications/${userId}`,
        { withCredentials: true }
      );
      setEventSource(newEventSource);

      newEventSource.onmessage = (event) => {
        const newNotification = JSON.parse(event.data);
        console.log(newNotification);
        const notification = {
          type: newNotification.type,
          text: newNotification.text,
          id: newNotification.id,
          userId: newNotification.user_id,
          chatroomId: newNotification.chatroom_id,
          createdAt: newNotification.created_at, // Add created_at field
          read: newNotification.read,
        };

        setNotifications((prev) => {
          const updatedNotifications = [...prev, notification];
          return updatedNotifications.sort((a, b) => {
            // Parse the date strings into Date objects for comparison
            const dateA = new Date(a.createdAt || "");
            const dateB = new Date(b.createdAt || "");
            return dateB.getTime() - dateA.getTime(); // Compare timestamps
          });
        });

        // Show transient notification
        setTransientNotification(newNotification.text);
        setShowTransientNotification(true);

        // Hide transient notification after 3 seconds
        setTimeout(() => {
          setShowTransientNotification(false);
        }, 3000);
      };

      newEventSource.onerror = (error) => {
        console.error("EventSource failed:", error);
        newEventSource.close();
      };

      return () => {
        newEventSource.close();
      };
    }
  }, [userId, token]);
  const toggleNotifications = () => setShowNotifications(!showNotifications);
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
    <>
      <style>
        {`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes fadeOut {
          from { opacity: 1; }
          to { opacity: 0; }
        }

        .fade-in {
          animation: fadeIn 0.5s forwards;
        }

        .fade-out {
          animation: fadeOut 0.5s forwards;
        }
      `}
      </style>

      {showTransientNotification && (
        <div
          className={`fixed bottom-5 right-5 z-50 p-4 bg-gray-900 text-white rounded shadow-lg ${
            showTransientNotification ? "fade-in" : "fade-out"
          }`}
          style={{ transition: "opacity 0.5s" }}
        >
          {transientNotification}
        </div>
      )}
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
        <div className="fixed top-5 right-5 z-50">
          {showNotifications ? (
            <div className="mt-2 w-64 bg-white shadow-lg rounded-lg overflow-hidden">
              <div className="text-black p-4">
                <h3 className="font-semibold text-lg">Notifications</h3>
                <button
                  onClick={() => setShowNotifications(false)}
                  className="text-blue-500 hover:text-blue-700"
                >
                  Hide Notifications
                </button>
              </div>
              {/* Scrollable List for Unread Notifications */}
              <ul className="max-h-60 overflow-y-auto">
                {notifications
                  .filter((n) => !n.read)
                  .map((notification, index) => (
                    <li
                      key={notification.id}
                      className="border-b last:border-b-0"
                    >
                      <button
                        onClick={() => handleNotificationClick(notification)}
                        className="w-full text-left p-2"
                      >
                        {notification.text} -{" "}
                        {new Date(notification.createdAt).toLocaleString()}
                      </button>
                    </li>
                  ))}
              </ul>
            </div>
          ) : (
            <button
              className="relative text-3xl"
              onClick={() => setShowNotifications(true)}
            >
              <FiBell />
              {notifications.filter((n) => !n.read).length > 0 && (
                <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-100 bg-red-600 rounded-full">
                  {notifications.filter((n) => !n.read).length}
                </span>
              )}
            </button>
          )}
        </div>
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
    </>
  );
};

export default Layout;
