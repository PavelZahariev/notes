import os
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the Supabase JWT and return user information.
    """
    token = credentials.credentials
    try:
        # Verify the token with Supabase
        # supabase.auth.get_user(token) validates the JWT and returns user info
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        user = user_response.user
        
        # Sync user profile to the 'profiles' table
        try:
            # last_sign_in_at might be a datetime object, ensure it's a string for serialization
            last_login = user.last_sign_in_at
            if hasattr(last_login, 'isoformat'):
                last_login = last_login.isoformat()
                
            supabase.table('profiles').upsert({
                'id': user.id,
                'email': user.email,
                'last_sign_in_at': last_login
            }).execute()
        except Exception as e:
            print(f"⚠️ Failed to sync user profile: {str(e)}")
            # We don't fail here, just log or handle as needed
            
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
