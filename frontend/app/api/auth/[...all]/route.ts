/**
 * Better Auth API route handler.
 * Handles all authentication requests at /api/auth/*
 */
import { toNextJsHandler } from "better-auth/next-js";
import { auth } from "@/lib/auth-server";

/**
 * Export Next.js route handlers for Better Auth.
 */
const handler = toNextJsHandler(auth);

export const GET = handler.GET;
export const POST = handler.POST;
