import { supabaseServer as supabase } from '@/lib/supabase-server';

function toCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

function toCamelDeep(obj: any): any {
  if (!obj || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(toCamelDeep);
  const result: any = {};
  for (const key of Object.keys(obj)) {
    result[toCamel(key)] = toCamelDeep(obj[key]);
  }
  return result;
}

export async function supabaseComics(params: {
  q?: string;
  publisher?: string;
  page?: number;
  limit?: number;
}) {
  const { q, publisher, page = 1, limit = 20 } = params;
  const from = (page - 1) * limit;
  const to = from + limit - 1;

  let query = supabase.from('comics').select('*, publisher(*), volumes:volumes(*)');

  if (q) {
    query = query.or(
      `title.ilike.%${q}%,authors.cs.{${q}},series.ilike.%${q}%`
    );
  }

  if (publisher) {
    query = query.eq('publisher.slug', publisher);
  }

  const { data, error, count } = await query
    .order('updated_at', { ascending: false })
    .range(from, to);

  if (error) throw error;

  const comicsWithDetails = await Promise.all(
    (data || []).map(async (comic: any) => {
      const gifts = await supabase
        .from('gifts')
        .select('*')
        .eq('volume_id', comic.volumes?.[0]?.id || null)
        .is('volume_id', comic.volumes?.[0]?.id || null);
      
      const volumes = comic.volumes || [];
      volumes.forEach((v: any) => {
        v.gifts = (gifts.data || []).filter((g: any) => g.volume_id === v.id);
      });

      return {
        ...comic,
        volumes: volumes.map((v: any) => ({ ...v, gifts: v.gifts || [] })),
        eventGifts: [],
      };
    })
  );

  return {
    data: comicsWithDetails.map(toCamelDeep),
    pagination: {
      page,
      limit,
      total: count || 0,
      totalPages: Math.ceil((count || 0) / limit),
    },
  };
}

export async function supabaseComic(id: string) {
  const { data: comic, error } = await supabase
    .from('comics')
    .select('*, publisher(*), volumes:volumes(*)')
    .eq('id', id)
    .single();

  if (error) throw error;
  if (!comic) return null;

  const volumes = comic.volumes || [];
  const volumeIds = volumes.map((v: any) => v.id);

  const { data: gifts } = await supabase
    .from('gifts')
    .select('*')
    .in('volume_id', volumeIds);

  volumes.forEach((v: any) => {
    v.gifts = gifts?.filter((g: any) => g.volume_id === v.id) || [];
  });

  return toCamelDeep({ ...comic, eventGifts: [] });
}

export async function supabaseListings(params: {
  q?: string;
  condition?: string;
  minPrice?: string;
  maxPrice?: string;
  type?: string;
  status?: string;
  userId?: string;
  page?: number;
  limit?: number;
}) {
  const { q, condition, minPrice, maxPrice, type, status = 'active', userId, page = 1, limit = 20 } = params;
  const from = (page - 1) * limit;
  const to = from + limit - 1;

  let query = supabase
    .from('listings')
    .select('*, comic:comics(*), volume:volumes(*), gift:gifts(*), user:users(*)', { count: 'exact' })
    .eq('status', status);

  if (q) {
    query = query
      .ilike('comic.title', `%${q}%`)
      .ilike('volume.title', `%${q}%`)
      .ilike('gift.name', `%${q}%`);
  }

  if (condition) {
    query = query.eq('condition', condition);
  }

  if (type) {
    query = query.eq('listing_type', type);
  }

  if (userId) {
    query = query.eq('user_id', userId);
  }

  if (minPrice) {
    query = query.gte('price', parseInt(minPrice));
  }

  if (maxPrice) {
    query = query.lte('price', parseInt(maxPrice));
  }

  const { data, error, count } = await query
    .order('created_at', { ascending: false })
    .range(from, to);

  if (error) throw error;

  return {
    data: (data || []).map(toCamelDeep),
    pagination: {
      page,
      limit,
      total: count || 0,
      totalPages: Math.ceil((count || 0) / limit),
    },
  };
}

export async function supabaseListing(id: string) {
  const { data, error } = await supabase
    .from('listings')
    .select('*, comic:comics(*), volume:volumes(*), gift:gifts(*), user:users(*)')
    .eq('id', id)
    .single();

  if (error) throw error;

  return toCamelDeep(data);
}

export async function supabasePublishers() {
  const { data, error } = await supabase
    .from('publishers')
    .select('id, name, slug')
    .order('name', { ascending: true });

  if (error) throw error;

  return (data || []).map(toCamelDeep);
}
