export interface ErrorResponse {
  detail: string;
}

export interface CreateUserResponse {
  username: string;
  id: string;
}

export interface CreateSessionResponse {
  access_token: string;
  expires: Date;
}
export interface User {
  username: string;
  id: string;
  online: boolean | null;
}
