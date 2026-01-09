/**
 * Custom JWT token endpoint.
 * Generates a JWT for authenticated users to use with the backend API.
 */
import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth-server";
import { SignJWT } from "jose";

export async function GET(request: NextRequest) {
  try {
    // Get the current session from Better Auth
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session?.user?.id) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    // Create a JWT token with the user ID
    const secret = new TextEncoder().encode(process.env.BETTER_AUTH_SECRET);

    const token = await new SignJWT({ sub: session.user.id })
      .setProtectedHeader({ alg: "HS256" })
      .setIssuedAt()
      .setExpirationTime("24h")
      .sign(secret);

    return NextResponse.json({ token });
  } catch (error) {
    console.error("Token generation error:", error);
    return NextResponse.json(
      { error: "Failed to generate token" },
      { status: 500 }
    );
  }
}
