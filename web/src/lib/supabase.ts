import { createClient as createSupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

function getSupabaseConfig() {
  if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error('Missing Supabase environment variables');
  }

  return { supabaseUrl, supabaseAnonKey };
}

export function createClient() {
  const { supabaseUrl, supabaseAnonKey } = getSupabaseConfig();
  return createSupabaseClient(supabaseUrl, supabaseAnonKey);
}

export function createBrowserClient() {
  const { supabaseUrl, supabaseAnonKey } = getSupabaseConfig();
  return createSupabaseClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  });
}

export const supabase = createClient();
