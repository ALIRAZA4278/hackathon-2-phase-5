"""
FastAPI dependencies for authentication and authorization.
Per specs/security.md
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import get_settings

# Security scheme for JWT Bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependency that extracts and verifies the JWT token from the Authorization header.

    Security Flow:
    1. Extract token from Authorization header (Bearer <token>)
    2. Decode and verify JWT signature using BETTER_AUTH_SECRET
    3. Check token expiration
    4. Extract user_id from 'sub' claim
    5. Return user_id for route handlers

    Raises:
        HTTPException 401: For all authentication failures
    """
    settings = get_settings()
    token = credentials.credentials

    try:
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm]
        )

        # Extract user_id from 'sub' claim
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return user_id

    except JWTError as e:
        # Handle specific JWT errors
        error_message = str(e).lower()
        if "expired" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def verify_user_access(url_user_id: str, jwt_user_id: str) -> None:
    """
    Verify that the URL user_id matches the JWT user_id.

    Security: This prevents users from accessing other users' data
    by manipulating the URL.

    Args:
        url_user_id: User ID from the URL path
        jwt_user_id: User ID extracted from JWT token

    Raises:
        HTTPException 403: If user IDs don't match
    """
    if url_user_id != jwt_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )
