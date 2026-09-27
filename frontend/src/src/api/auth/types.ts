export interface User{
    username: string;
    is_superuser: boolean;
    is_totp_enabled: boolean;
    avatar_url?: string;
}

export interface UserUpdateData {
    username?: string;
    password?: string;
}

export interface UserCreateData {
    username: string;
    plain_password: string;
}

export interface UserReadData {
    id: string;
    username: string;
    avatar_url?: string;
    is_superuser: boolean;
    is_banned: boolean;
    is_totp_enabled: boolean;
}

export interface Session {
  session_id: string;
  created_at: string;
  device: string;
  ip: string;
}

export type APIKey = {
  id: string;
  name: string;
  key_hint: string;
  created_at: Date;
  last_used_at: Date;
}

export type APIKeyCreateResult = {
  id: string;
  name: string;
  key_hint: string;
  created_at: Date;
  last_used_at: Date;
  key: string; // The actual API key that should be shown to the user only once
}