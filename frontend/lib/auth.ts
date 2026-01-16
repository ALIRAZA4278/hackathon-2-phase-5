/**
 * Better Auth client configuration.
 * Per specs/features/authentication.md
 */
import { createAuthClient } from "better-auth/react";

/**
 * Better Auth client instance.
 * Provides authentication methods for the frontend.
 */
export const authClient = createAuthClient({
  baseURL: process.env.BETTER_AUTH_URL || "https://todo-app-chatbot-roan.vercel.app/",
});

/**
 * Export commonly used auth methods for convenience.
 */
export const {
  signIn,
  signUp,
  signOut,
  useSession,
} = authClient;

/**
 * Get JWT token for API calls.
 * Fetches a custom JWT from our token endpoint.
 */
export async function getApiToken(): Promise<string | null> {
  try {
    const response = await fetch("/api/token", {
      credentials: "include",
    });
    if (!response.ok) return null;
    const data = await response.json();
    return data.token || null;
  } catch {
    return null;
  }
}

/**
 * Get the current user's ID from the session.
 */
export async function getCurrentUserId(): Promise<string | null> {
  try {
    const session = await authClient.getSession();
    return session?.data?.user?.id || null;
  } catch {
    return null;
  }
}
