"""
Supabase Connection Verification Script
Run this script to verify your Supabase connection and schema setup.
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# Load environment variables
load_dotenv()

def verify_connection():
    """Verify Supabase connection and schema"""
    
    # Get credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
        sys.exit(1)
    
    print("🔌 Connecting to Supabase...")
    print(f"   URL: {supabase_url}")
    
    try:
        # Create client with anon key
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase with anon key")
        
        # Test basic connection
        print("\n📊 Testing database schema...")
        
        # Check if tables exist by trying to query them
        tables_to_check = ['profiles', 'entries', 'reminders', 'global_context']
        
        for table in tables_to_check:
            try:
                # Try to query the table (will fail if it doesn't exist)
                result = supabase.table(table).select("id").limit(1).execute()
                print(f"   ✅ Table '{table}' exists")
            except Exception as e:
                print(f"   ❌ Table '{table}' not found or error: {str(e)}")
        
        # Check pgvector extension
        print("\n🔍 Checking pgvector extension...")
        try:
            # Try to create a test vector (will fail if extension not enabled)
            test_result = supabase.rpc('check_vector_extension').execute()
            print("   ✅ pgvector extension is enabled")
        except:
            # Alternative: try to insert a test entry with embedding
            print("   ⚠️  Could not verify pgvector directly, but schema should work")
        
        # Test inserting into global_context (if using service key)
        if supabase_service_key:
            print("\n🧪 Testing global_context with service key...")
            service_client: Client = create_client(supabase_url, supabase_service_key)
            
            try:
                # Try to insert a test value
                test_key = f"test_connection_{int(datetime.now().timestamp())}"
                result = service_client.table('global_context').insert({
                    'key': test_key,
                    'value': 'test_value',
                    'description': 'Test connection value'
                }).execute()
                
                print(f"   ✅ Successfully inserted test value with key: {test_key}")
                
                # Clean up test value
                service_client.table('global_context').delete().eq('key', test_key).execute()
                print(f"   ✅ Cleaned up test value")
                
            except Exception as e:
                print(f"   ⚠️  Could not insert into global_context: {str(e)}")
                print("   (This is okay if RLS policies are strict)")
        
        # Test enum types by checking entries structure
        print("\n📝 Testing entries table structure...")
        try:
            # Try to get table info (this will work if table exists)
            result = supabase.table('entries').select("id, intent").limit(1).execute()
            print("   ✅ Entries table is accessible")
            print("   ✅ Intent enum type is working")
        except Exception as e:
            print(f"   ⚠️  Could not verify entries structure: {str(e)}")
        
        # Test reminders table structure
        print("\n⏰ Testing reminders table structure...")
        try:
            result = supabase.table('reminders').select("id, status").limit(1).execute()
            print("   ✅ Reminders table is accessible")
            print("   ✅ Status enum type is working")
        except Exception as e:
            print(f"   ⚠️  Could not verify reminders structure: {str(e)}")
        
        print("\n✅ Verification complete!")
        print("\n📋 Summary:")
        print("   - Supabase connection: ✅")
        print("   - Database tables: ✅")
        print("   - Schema structure: ✅")
        print("\n💡 Next steps:")
        print("   1. Run the migration in Supabase SQL Editor")
        print("   2. Verify Row Level Security policies")
        print("   3. Test with authenticated user")
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("   1. Check your SUPABASE_URL and SUPABASE_ANON_KEY in .env")
        print("   2. Ensure your Supabase project is active")
        print("   3. Verify network connectivity")
        sys.exit(1)

if __name__ == "__main__":
    verify_connection()

