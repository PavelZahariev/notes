from fastapi import APIRouter, HTTPException, Depends
from pydantic import EmailStr
from app.core.auth import get_current_user, supabase
from typing import List

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/invite")
async def invite_user(email: EmailStr, user: dict = Depends(get_current_user)):
    """
    Invite a user by adding their email to the invitations table.
    Note: For simplicity, any authenticated user can currently invite others.
    In a real app, you would add a check for admin roles here.
    """
    try:
        result = supabase.table("invitations").insert({"email": email, "invited_by": user.id}).execute()
        return {"message": f"Successfully invited {email}"}
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="This user has already been invited or is already a member.")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invitations")
async def list_invitations(user: dict = Depends(get_current_user)):
    """
    List all invited emails.
    """
    try:
        result = supabase.table("invitations").select("*").execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/invitations/{email}")
async def remove_invitation(email: str, user: dict = Depends(get_current_user)):
    """
    Remove an invitation.
    """
    try:
        result = supabase.table("invitations").delete().eq("email", email).execute()
        return {"message": f"Removed invitation for {email}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
