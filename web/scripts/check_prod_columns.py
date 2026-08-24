import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'postgresql://postgres:%40ThanhVy2323%40@db.kfseqrvwvkjbdyywlobp.supabase.co:5432/postgres'
conn = psycopg2.connect(url)
cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'publishers' ORDER BY ordinal_position")
cols = [row[0] for row in cur.fetchall()]
print('Publishers columns:', cols)

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'comics' ORDER BY ordinal_position")
cols2 = [row[0] for row in cur.fetchall()]
print('Comics columns:', cols2)

cur.close()
conn.close()
