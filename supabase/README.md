# Supabase Migrations

This directory contains SQL migration files for setting up the database schema.

## Migration Files

### 001_initial_schema.sql
Creates the initial database schema including:
- pgvector extension for embeddings
- Enum types (intent_type, reminder_status_type)
- Tables: profiles, entries, reminders, global_context
- Row Level Security (RLS) policies
- Automatic triggers for updated_at timestamps
- Auto-profile creation on user signup

### 002_vector_search_function.sql
Creates a function for semantic search using vector similarity.

## How to Run Migrations

### Option 1: Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Open the migration file (`001_initial_schema.sql`)
4. Copy and paste the entire SQL content
5. Click **Run** to execute
6. Repeat for `002_vector_search_function.sql`

### Option 2: Supabase CLI

If you have Supabase CLI installed:

```bash
# Link to your project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

### Option 3: psql

```bash
psql -h db.your-project.supabase.co -U postgres -d postgres -f migrations/001_initial_schema.sql
```

## Verification

After running the migrations, verify the setup:

```bash
# From the backend directory
python verify_supabase.py
```

This script will:
- Test the Supabase connection
- Verify all tables exist
- Check pgvector extension
- Test basic CRUD operations

## Schema Overview

### profiles
- Linked to Supabase Auth users
- Stores user profile information
- Auto-created on user signup

### entries
- Main table for notes and reminders
- Contains content, summary, intent, category
- Stores OpenAI embeddings (1536 dimensions)
- Indexed for fast queries and vector search

### reminders
- Linked to entries with intent='REMINDER'
- Stores due_date and status
- Indexed for efficient filtering

### global_context
- Key-value store for user-specific context variables
- Linked to users via `user_id` foreign key
- Example: 'next_release_date', 'preferred_timezone'
- **RLS Policy**: 
  - Users can only access their own context (SELECT, INSERT, UPDATE, DELETE)
  - Each user can have their own values for the same keys
  - Unique constraint on (user_id, key) ensures one value per key per user

## Row Level Security (RLS)

All tables have RLS enabled with policies that:
- Users can only access their own data (entries, reminders, profiles, global_context)
- Each table enforces user isolation through `user_id` checks
- Service role can bypass RLS (for admin operations)

## Vector Search

The `search_similar_entries` function enables semantic search:
- Takes a query embedding and user_id
- Returns similar entries ordered by similarity
- Uses cosine distance for similarity calculation

Example usage:
```sql
SELECT * FROM search_similar_entries(
    'user-uuid-here',
    '[0.1, 0.2, ...]'::vector(1536),
    0.7,  -- threshold
    10    -- limit
);
```

