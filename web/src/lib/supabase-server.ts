import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseSecretKey = process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;

function createServer(): SupabaseClient {
  if (!supabaseUrl || !supabaseSecretKey) {
    throw new Error('Missing Supabase server environment variables');
  }
  return createClient(supabaseUrl, supabaseSecretKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });
}

export const supabaseServer = new Proxy({} as SupabaseClient, {
  get(_target, prop) {
    const client = createServer();
    return (client as any)[prop];
  },
}) as unknown as SupabaseClient;
