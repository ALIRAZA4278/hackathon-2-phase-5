/**
 * Better Auth server configuration.
 * Shared between auth routes and token generation.
 */
import { betterAuth } from "better-auth";
import { Pool } from "pg";

/**
 * Create PostgreSQL connection pool.
 */
const pool = new Pool({
  connectionString: process.env.DATABASE_URL!,
});

/**
 * Better Auth server instance.
 */
export const auth = betterAuth({
  database: pool,
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24,
    updateAge: 60 * 60,
  },
  secret: process.env.BETTER_AUTH_SECRET,
});
