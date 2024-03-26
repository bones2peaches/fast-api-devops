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
  return (
    <div className="message mb-4 p-3 bg-gray-100 rounded-lg shadow">
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
        <>
          <p className="text-gray-800">
            {text}
            {editted && <span className="text-gray-500"> (Edited)</span>}
          </p>
          <small className="text-gray-500">Sent by: {sentBy.username}</small>
          <small className="text-gray-500 block">
            Sent at: {new Date(sentAt).toLocaleTimeString()}
          </small>
          <div className="mt-2">
            <div className="inline-flex items-center mr-2">
              <button onClick={handleLike} className="mr-1">
                👍 {likes.length}
              </button>
              {/* Hover to show usernames */}
              <div className="relative group">
                <span className="cursor-default">👤</span>
                <div className="absolute hidden group-hover:block z-10 bg-white border border-gray-200 rounded shadow-lg p-2">
                  {likes.map((like: User) => (
                    <div
                      key={like.id}
                      className="hover:bg-gray-100 p-1 rounded cursor-pointer"
                      onClick={() => handleNavigateToUser(like.id)}
                    >
                      {like.username}
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="inline-flex items-center mr-2">
              <button onClick={handleDislike} className="mr-1">
                👍 {dislikes.length}
              </button>
              {/* Hover to show usernames */}
              <div className="relative group">
                <span className="cursor-default">👤</span>
                <div className="absolute hidden group-hover:block z-10 bg-white border border-gray-200 rounded shadow-lg p-2">
                  {dislikes.map((like: User) => (
                    <div
                      key={like.id}
                      className="hover:bg-gray-100 p-1 rounded cursor-pointer"
                      onClick={() => handleNavigateToUser(like.id)}
                    >
                      {like.username}
                    </div>
                  ))}
                </div>
              </div>
            </div>
            {canEditOrDelete && (
              <>
                <button onClick={handleEdit} className="mr-2">
                  Edit
                </button>
                <button onClick={handleDelete}>Delete</button>
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Message;
