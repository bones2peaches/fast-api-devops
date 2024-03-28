import {
  ErrorResponse,
  CreateUserResponse,
  CreateSessionResponse,
} from "../types/user";

// Import fetch in a Node.js environment. Uncomment the following line if needed.
// import fetch from "node-fetch";

export class ApiClient {
  private protocol: string;
  private host: string;
  private port: number;
  private baseUrl: string;

  constructor(protocol: string, host: string, port: number) {
    this.protocol = protocol;
    this.host = host;
    this.port = port;
    this.baseUrl = `${this.protocol}://${this.host}:${this.port}`;
  }

  async createUser(username: string, password: string): Promise<any> {
    const url = `${this.baseUrl}/api/user`;
    const payload = { username: username, password: password };
    const requestOptions: RequestInit = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    };

    try {
      const response = await fetch(url, requestOptions);

      if (response.status === 400) {
        // Assuming the server returns a JSON object with an error field
        const errorResponse: ErrorResponse = await response.json();
        return errorResponse;
      } else if (response.ok) {
        const data: CreateUserResponse = await response.json();
        return data;
      } else {
        // Handle other unexpected statuses
        throw new Error("Unexpected response from the server");
      }
    } catch (error) {
      console.error("Error creating user:", error);
      throw error; // Or return a specific error object
    }
  }

  async createSession(username: string, password: string): Promise<any> {
    const url = `${this.baseUrl}/api/user/session`;
    const payload = { username: username, password: password };
    const requestOptions: RequestInit = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include",
    };

    try {
      const response = await fetch(url, requestOptions);

      if (response.status === 400) {
        // Assuming the server returns a JSON object with an error field
        const errorResponse: ErrorResponse = await response.json();
        return errorResponse;
      } else if (response.ok) {
        const data: CreateSessionResponse = await response.json();
        return data;
      } else {
        // Handle other unexpected statuses
        throw new Error("Unexpected response from the server");
      }
    } catch (error) {
      console.error("Error creating user:", error);
      throw error; // Or return a specific error object
    }
  }

  async deleteSession(token: string | null): Promise<any> {
    const url = `${this.baseUrl}/api/user/session`;
    const requestOptions: RequestInit = {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
    };

    const response = await fetch(url, requestOptions);
    return null;
  }

  async createChatroom(
    token: string | null,
    name: string,
    category: string
  ): Promise<any> {
    const url = `${this.baseUrl}/api/chatroom`;
    const payload = { name: name, category: category };
    const requestOptions: RequestInit = {
      method: "POST",
      body: JSON.stringify(payload),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    };

    const response = await fetch(url, requestOptions);
    if (response.status == 400) {
      return "dup";
    } else {
      const data = response.json();
      return data;
    }
  }

  async getChatroom(
    token: string | null,
    chatroom_id: string | any
  ): Promise<any> {
    const url = `${this.baseUrl}/api/chatroom/${chatroom_id}`;
    const requestOptions: RequestInit = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    };

    const response = await fetch(url, requestOptions);
    if (response.status == 404) {
      return null;
    } else {
      const data = response.json();
      return data;
    }
  }

  async getChatrooms(
    token: string | null,
    page: number | any,
    per_page: number
  ): Promise<any> {
    const url = `${this.baseUrl}/api/chatrooms?page=${page}&per_page=${per_page}`;
    const requestOptions: RequestInit = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    };

    const response = await fetch(url, requestOptions);
    if (response.status == 404) {
      return null;
    } else {
      const data = response.json();

      return data;
    }
  }

  async getChatroomUsers(
    token: string | null,
    chatroom_id: string | null
  ): Promise<any> {
    const url = `${this.baseUrl}/api/chatroom/${chatroom_id}/user`;
    const requestOptions: RequestInit = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    };

    const response = await fetch(url, requestOptions);
    if (response.status == 404) {
      return null;
    } else {
      const data = response.json();

      return data;
    }
  }

  async joinChatroom(
    token: string | null,
    chatroomId: string | any
  ): Promise<any> {
    const url = `${this.baseUrl}/api/chatroom/${chatroomId}/user?access_token=${token}`;
    const requestOptions: RequestInit = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    };

    const response = await fetch(url, requestOptions);
    if (response.status == 403) {
      return null;
    } else {
      const data = response.body;
      return data;
    }
  }

  async sendMessage(
    token: string | null,
    chatroomId: string | null,
    messageText: string
  ): Promise<any> {
    // Construct the URL for the API endpoint to send a message to a specific chatroom
    const url = `${this.baseUrl}/api/chatroom/${chatroomId}/message?access_token=${token}`;

    // Prepare the request options, including the method, headers, and body with the message text
    const requestOptions: RequestInit = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ text: messageText }), // Convert the message object to a JSON string
    };

    try {
      const response = await fetch(url, requestOptions);

      if ([200, 201, 202].includes(response.status)) {
        // Parse the JSON response body
        return response; // Return the parsed data
      } else if (response.status == 403) {
        throw new Error(
          "Access forbidden. Please check your authentication token."
        );
      } else {
        const errorText = await response.text(); // Extract text for error details
        throw new Error(`Failed to send message: ${errorText}`);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      throw error; // Re-throw to be handled by the caller
    }
  }

  async editMessage(
    token: string | null,
    chatroomId: string | null,
    messageId: string,
    messageText: string
  ): Promise<any> {
    // Construct the URL for the API endpoint to send a message to a specific chatroom
    const url = `${this.baseUrl}/api/chatroom/${chatroomId}/update?access_token=${token}`;

    // Prepare the request options, including the method, headers, and body with the message text
    const requestOptions: RequestInit = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        text: messageText,
        action: "edit",
        message_id: messageId,
        like: null,
      }), // Convert the message object to a JSON string
    };

    try {
      const response = await fetch(url, requestOptions);

      if ([200, 201, 202].includes(response.status)) {
        // Parse the JSON response body
        return response; // Return the parsed data
      } else if (response.status == 403) {
        throw new Error(
          "Access forbidden. Please check your authentication token."
        );
      } else {
        const errorText = await response.text(); // Extract text for error details
        throw new Error(`Failed to send message: ${errorText}`);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      throw error; // Re-throw to be handled by the caller
    }
  }

  async reactToMessage(
    token: string | null,
    chatroomId: string | null,
    messageId: string,
    isLike: boolean
  ): Promise<any> {
    // Construct the URL for the API endpoint to send a message to a specific chatroom
    const url = `${this.baseUrl}/api/chatroom/${chatroomId}/update?access_token=${token}`;

    // Prepare the request options, including the method, headers, and body with the message text
    const requestOptions: RequestInit = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        text: null,
        action: "reaction",
        message_id: messageId,
        liked: isLike,
      }), // Convert the message object to a JSON string
    };

    try {
      const response = await fetch(url, requestOptions);

      if ([200, 201, 202].includes(response.status)) {
        // Parse the JSON response body
        return response; // Return the parsed data
      } else if (response.status == 403) {
        throw new Error(
          "Access forbidden. Please check your authentication token."
        );
      } else {
        const errorText = await response.text(); // Extract text for error details
        throw new Error(`Failed to send message: ${errorText}`);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      throw error; // Re-throw to be handled by the caller
    }
  }

  async deleteMessage(
    token: string | null,
    chatroomId: string | null,
    messageId: string
  ): Promise<any> {
    // Construct the URL for the API endpoint to send a message to a specific chatroom
    const url = `${this.baseUrl}/api/chatroom/${chatroomId}/update?access_token=${token}`;

    // Prepare the request options, including the method, headers, and body with the message text
    const requestOptions: RequestInit = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        text: null,
        action: "delete",
        message_id: messageId,
        liked: null,
      }), // Convert the message object to a JSON string
    };

    try {
      const response = await fetch(url, requestOptions);

      if ([200, 201, 202].includes(response.status)) {
        // Parse the JSON response body
        return response; // Return the parsed data
      } else if (response.status == 403) {
        throw new Error(
          "Access forbidden. Please check your authentication token."
        );
      } else {
        const errorText = await response.text(); // Extract text for error details
        throw new Error(`Failed to send message: ${errorText}`);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      throw error; // Re-throw to be handled by the caller
    }
  }
}

export default ApiClient;
