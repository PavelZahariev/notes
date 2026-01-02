"""
Database Service
Handles interactions with Supabase database
"""
import os
from supabase import create_client, Client
from typing import Optional, List, Dict
from datetime import datetime

class DatabaseService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.client: Optional[Client] = None
        self.service_client: Optional[Client] = None
    
    def get_client(self) -> Client:
        """
        Get or create Supabase client (anon key - subject to RLS)
        """
        if not self.client:
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
            self.client = create_client(self.supabase_url, self.supabase_key)
        return self.client
    
    def get_service_client(self) -> Client:
        """
        Get or create Supabase service client (bypasses RLS)
        Required for global_context modifications
        """
        if not self.service_client:
            if not self.supabase_url:
                raise ValueError("SUPABASE_URL must be set")
            if not self.supabase_service_key:
                raise ValueError("SUPABASE_SERVICE_KEY must be set for global_context modifications")
            self.service_client = create_client(self.supabase_url, self.supabase_service_key)
        return self.service_client
    
    # Entry methods
    async def create_entry(
        self, 
        user_id: str, 
        content: str, 
        intent: str = "NOTE",
        summary: Optional[str] = None,
        category: Optional[str] = None,
        embedding: Optional[List[float]] = None
    ) -> dict:
        """
        Create a new entry in the database
        """
        entry_data = {
            "user_id": user_id,
            "content": content,
            "intent": intent,
            "summary": summary,
            "category": category,
        }
        
        if embedding:
            entry_data["embedding"] = embedding
        
        result = self.get_client().table("entries").insert(entry_data).execute()
        return result.data[0] if result.data else {}
    
    async def get_entries(
        self, 
        user_id: str,
        intent: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """
        Get entries for a user, optionally filtered by intent
        """
        query = self.get_client().table("entries").select("*").eq("user_id", user_id)
        
        if intent:
            query = query.eq("intent", intent)
        
        result = query.order("created_at", desc=True).limit(limit).offset(offset).execute()
        return result.data if result.data else []
    
    async def get_entry(self, entry_id: str) -> Optional[dict]:
        """
        Get a specific entry by ID
        """
        result = self.get_client().table("entries").select("*").eq("id", entry_id).execute()
        return result.data[0] if result.data else None
    
    async def update_entry(self, entry_id: str, updates: dict) -> dict:
        """
        Update an entry
        """
        result = self.get_client().table("entries").update(updates).eq("id", entry_id).execute()
        return result.data[0] if result.data else {}
    
    async def delete_entry(self, entry_id: str) -> bool:
        """
        Delete an entry (cascades to reminders)
        """
        result = self.get_client().table("entries").delete().eq("id", entry_id).execute()
        return True
    
    # Reminder methods
    async def create_reminder(
        self, 
        entry_id: str, 
        due_date: datetime,
        status: str = "PENDING"
    ) -> dict:
        """
        Create a new reminder for an entry
        """
        reminder_data = {
            "entry_id": entry_id,
            "due_date": due_date.isoformat(),
            "status": status
        }
        result = self.get_client().table("reminders").insert(reminder_data).execute()
        return result.data[0] if result.data else {}
    
    async def get_reminders(
        self, 
        user_id: str,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Get reminders for a user's entries
        """
        # Get reminders by joining with entries
        result = self.get_client().table("reminders").select(
            "*, entries(*)"
        ).eq("entries.user_id", user_id)
        
        if status:
            result = result.eq("status", status)
        
        result = result.order("due_date", desc=False).limit(limit).execute()
        return result.data if result.data else []
    
    async def update_reminder(self, reminder_id: str, updates: dict) -> dict:
        """
        Update a reminder
        """
        result = self.get_client().table("reminders").update(updates).eq("id", reminder_id).execute()
        return result.data[0] if result.data else {}
    
    # Global context methods (user-specific)
    async def get_global_context(self, user_id: str, key: str) -> Optional[str]:
        """
        Get a global context value by key for a specific user
        """
        result = self.get_client().table("global_context").select("value").eq("user_id", user_id).eq("key", key).execute()
        return result.data[0]["value"] if result.data else None
    
    async def set_global_context(self, user_id: str, key: str, value: str, description: Optional[str] = None) -> dict:
        """
        Set or update a global context value for a specific user
        RLS ensures users can only modify their own context
        """
        context_data = {
            "user_id": user_id,
            "key": key,
            "value": value,
            "description": description
        }
        # Upsert with user_id and key as unique constraint
        result = self.get_client().table("global_context").upsert(
            context_data,
            on_conflict="user_id,key"
        ).execute()
        return result.data[0] if result.data else {}
    
    async def get_all_global_context(self, user_id: str) -> Dict[str, str]:
        """
        Get all global context as a dictionary for a specific user
        """
        result = self.get_client().table("global_context").select("key, value").eq("user_id", user_id).execute()
        return {item["key"]: item["value"] for item in result.data} if result.data else {}
    
    async def delete_global_context(self, user_id: str, key: str) -> bool:
        """
        Delete a global context value by key for a specific user
        RLS ensures users can only delete their own context
        """
        result = self.get_client().table("global_context").delete().eq("user_id", user_id).eq("key", key).execute()
        return True
    
    # Vector similarity search
    async def search_similar_entries(
        self,
        user_id: str,
        embedding: List[float],
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[dict]:
        """
        Search for similar entries using vector similarity
        """
        # Use Supabase RPC for vector similarity search
        # Note: You may need to create a custom function in Supabase for this
        result = self.get_client().rpc(
            "search_similar_entries",
            {
                "user_id_param": user_id,
                "query_embedding": embedding,
                "match_threshold": threshold,
                "match_count": limit
            }
        ).execute()
        return result.data if result.data else []

