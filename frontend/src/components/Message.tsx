import React, { useState } from "react";
import { User } from "../types/user"; // Assuming this is where your User type is defined
import ApiClient from "@/clients/api";
import { useRouter } from "next/router"; //
interface MessageProps {
  text: string;
  sentBy: User;
  sentAt: Date;
  view_user_id: string | null;
  token: string | null;
  messageId: string | any;
  chatroomId: string | any;
  likes: User[] | any;
  dislikes: User[] | any;
  editted: boolean;
  deleted: boolean;
}

const Message: React.FC<MessageProps> = ({
  text,
  sentBy,
  sentAt,
  view_user_id,
  token,
  messageId,
  chatroomId,
  likes,
  dislikes,
  editted,
  deleted,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState(text);
  const apiClient = new ApiClient("http", "localhost", 80);
  const router = useRouter(); // For navigation
  const handleLike = async () => {
    const update = await apiClient.reactToMessage(
      token,
      chatroomId,
      messageId,
      true
    );
  };

  const handleDislike = async () => {
    const update = await apiClient.reactToMessage(
      token,
      chatroomId,
      messageId,
      false
    );
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleDelete = async () => {
    const updateMessage = await apiClient.deleteMessage(
      token,
      chatroomId,
      messageId
    );
  };

  const handleFinishEdit = async () => {
    console.log("Edited text:", editedText);
    const updateMessage = await apiClient.editMessage(
      token,
      chatroomId,
      messageId,
      editedText
    );
    setIsEditing(false);
  };

  const handleNavigateToUser = (userId: string) => {
    // Implement navigation to user's page
    router.push(`/user/${userId}`);
  };

  const canEditOrDelete = sentBy.id === view_user_id;
  if (deleted) {
    return (
      <div className="message mb-4 p-3 bg-gray-100 rounded-lg shadow italic">
        Message deleted
      </div>
    );
  }

  //   return (
  //     <div className="message mb-4 p-3 bg-gray-100 rounded-lg shadow">
  //       {isEditing ? (
  //         <>
  //           <textarea
  //             className="w-full p-2 border border-gray-300 rounded-lg mb-2"
  //             value={editedText}
  //             onChange={(e) => setEditedText(e.target.value)}
  //           />
  //           <button
  //             onClick={handleFinishEdit}
  //             className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-4 rounded mr-2"
  //           >
  //             Finish
  //           </button>
  //         </>
  //       ) : (
  //         <>
  //           <p className="text-gray-800">{text}</p>
  //           <small className="text-gray-500">Sent by: {sentBy.username}</small>
  //           <small className="text-gray-500 block">
  //             Sent at: {new Date(sentAt).toLocaleTimeString()}
  //           </small>
  //           <div className="mt-2">
  //             <button onClick={handleLike} className="mr-2">
  //               👍 {likes.length}
  //             </button>
  //             <button onClick={handleDislike} className="mr-2">
  //               👎 {dislikes.length}
  //             </button>
  //             {canEditOrDelete && (
  //               <>
  //                 <button onClick={handleEdit} className="mr-2">
  //                   Edit
  //                 </button>
  //                 <button onClick={handleDelete}>Delete</button>
  //               </>
  //             )}
  //           </div>
  //         </>
  //       )}
  //     </div>
  //   );
  // };

  const userTooltip = (users: User[], reactionType: "like" | "dislike") => (
    <div className="absolute bottom-0 mb-6 left-0 invisible group-hover:visible bg-white border border-gray-300 rounded shadow-lg p-2 min-w-max whitespace-nowrap">
      {users.map((user) => (
        <div
          key={user.id}
          className="hover:bg-gray-100 p-1 rounded cursor-pointer"
          onClick={() => handleNavigateToUser(user.id)}
        >
          {user.username}
        </div>
      ))}
    </div>
  );

  return (
    <div
      className={`message mb-4 p-3 bg-gray-100 rounded-lg shadow ${
        deleted ? "text-gray-400" : "text-gray-800"
      }`}
    >
      {isEditing ? (
        <>
          <textarea
            className="w-full p-2 border border-gray-300 rounded-lg mb-2"
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
          />
          <button
            onClick={handleFinishEdit}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-4 rounded mr-2"
          >
            Finish
          </button>
        </>
      ) : (
        <div className={`${deleted ? "italic" : ""}`}>
          <p className={`text-sm ${editted && !deleted ? "mb-0" : "mb-2"}`}>
            {deleted ? "Message deleted" : text}
            {editted && !deleted && (
              <span className="text-xs text-gray-400"> (Edited)</span>
            )}
          </p>
          {!deleted && (
            <>
              <small className="text-xs text-gray-500">
                Sent by: {sentBy.username}
              </small>
              <small className="text-xs text-gray-500 block">
                Sent at: {new Date(sentAt).toLocaleTimeString()}
              </small>
              <div className="flex items-center space-x-2 mt-2">
                <div className="relative group inline-flex items-center">
                  <button
                    onClick={handleLike}
                    className="text-gray-500 hover:text-blue-500"
                  >
                    👍 {likes.length}
                  </button>
                  {likes.length > 0 && userTooltip(likes, "like")}
                </div>
                <div className="relative group inline-flex items-center">
                  <button
                    onClick={handleDislike}
                    className="text-gray-500 hover:text-blue-500"
                  >
                    👎 {dislikes.length}
                  </button>
                  {dislikes.length > 0 && userTooltip(dislikes, "dislike")}
                </div>
                {canEditOrDelete && (
                  <>
                    <button
                      onClick={handleEdit}
                      className="text-xs text-blue-500 hover:text-blue-600"
                    >
                      Edit
                    </button>
                    <button
                      onClick={handleDelete}
                      className="text-xs text-red-500 hover:text-red-600 ml-2"
                    >
                      Delete
                    </button>
                  </>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default Message;
