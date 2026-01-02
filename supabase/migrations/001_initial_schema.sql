-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create enum types
CREATE TYPE intent_type AS ENUM ('NOTE', 'REMINDER');
CREATE TYPE reminder_status_type AS ENUM ('PENDING', 'COMPLETED');

-- Create profiles table (linked to Supabase Auth)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security on profiles
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can view their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

-- Create policy: Users can update their own profile
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Create entries table
CREATE TABLE IF NOT EXISTS entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    summary TEXT,
    intent intent_type NOT NULL,
    category TEXT,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_entries_user_id ON entries(user_id);

-- Create index on intent for filtering
CREATE INDEX IF NOT EXISTS idx_entries_intent ON entries(intent);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_entries_created_at ON entries(created_at DESC);

-- Create vector similarity search index (using ivfflat for approximate nearest neighbor)
CREATE INDEX IF NOT EXISTS idx_entries_embedding ON entries 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Enable Row Level Security on entries
ALTER TABLE entries ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can view their own entries
CREATE POLICY "Users can view own entries" ON entries
    FOR SELECT USING (auth.uid() = user_id);

-- Create policy: Users can insert their own entries
CREATE POLICY "Users can insert own entries" ON entries
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create policy: Users can update their own entries
CREATE POLICY "Users can update own entries" ON entries
    FOR UPDATE USING (auth.uid() = user_id);

-- Create policy: Users can delete their own entries
CREATE POLICY "Users can delete own entries" ON entries
    FOR DELETE USING (auth.uid() = user_id);

-- Create reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    due_date TIMESTAMPTZ NOT NULL,
    status reminder_status_type DEFAULT 'PENDING',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on entry_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_reminders_entry_id ON reminders(entry_id);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminders(status);

-- Create index on due_date for sorting and filtering
CREATE INDEX IF NOT EXISTS idx_reminders_due_date ON reminders(due_date);

-- Enable Row Level Security on reminders
ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can view reminders for their own entries
CREATE POLICY "Users can view own reminders" ON reminders
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM entries 
            WHERE entries.id = reminders.entry_id 
            AND entries.user_id = auth.uid()
        )
    );

-- Create policy: Users can insert reminders for their own entries
CREATE POLICY "Users can insert own reminders" ON reminders
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM entries 
            WHERE entries.id = reminders.entry_id 
            AND entries.user_id = auth.uid()
        )
    );

-- Create policy: Users can update reminders for their own entries
CREATE POLICY "Users can update own reminders" ON reminders
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM entries 
            WHERE entries.id = reminders.entry_id 
            AND entries.user_id = auth.uid()
        )
    );

-- Create policy: Users can delete reminders for their own entries
CREATE POLICY "Users can delete own reminders" ON reminders
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM entries 
            WHERE entries.id = reminders.entry_id 
            AND entries.user_id = auth.uid()
        )
    );

-- Create global_context table for user-specific context variables
CREATE TABLE IF NOT EXISTS global_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, key)
);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_global_context_user_id ON global_context(user_id);

-- Create index on key for faster lookups
CREATE INDEX IF NOT EXISTS idx_global_context_key ON global_context(key);

-- Enable Row Level Security on global_context
ALTER TABLE global_context ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can view their own global context
CREATE POLICY "Users can view own global context" ON global_context
    FOR SELECT USING (auth.uid() = user_id);

-- Create policy: Users can insert their own global context
CREATE POLICY "Users can insert own global context" ON global_context
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create policy: Users can update their own global context
CREATE POLICY "Users can update own global context" ON global_context
    FOR UPDATE USING (auth.uid() = user_id);

-- Create policy: Users can delete their own global context
CREATE POLICY "Users can delete own global context" ON global_context
    FOR DELETE USING (auth.uid() = user_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_entries_updated_at BEFORE UPDATE ON entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reminders_updated_at BEFORE UPDATE ON reminders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_global_context_updated_at BEFORE UPDATE ON global_context
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to automatically create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to call the function when a new user is created
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

