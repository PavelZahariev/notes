-- Create invitations table to whitelist emails
CREATE TABLE IF NOT EXISTS public.invitations (
    email TEXT PRIMARY KEY,
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    invited_by UUID REFERENCES auth.users(id) -- Optional: track who invited them
);

-- Enable RLS on invitations
ALTER TABLE public.invitations ENABLE ROW LEVEL SECURITY;

-- Only authenticated users (admins) can see the invitation list
-- For now, let's keep it simple and only allow service_role or manually added policies
-- If you want specific users to be admins, you'd add a policy here.

-- Update the handle_new_user function to enforce invitation check
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the email is in the invitations list
    IF NOT EXISTS (SELECT 1 FROM public.invitations WHERE email = NEW.email) THEN
        RAISE EXCEPTION 'This email (%) has not been invited to join.', NEW.email;
    END IF;

    -- If invited, create the profile
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'avatar_url', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- The trigger 'on_auth_user_created' already exists from 001_initial_schema.sql
-- It will now use this updated function.
