import psycopg2

DNS = "dbname=Application user=kuand"


with psycopg2.connect(DNS) as conn:
    with conn.cursor() as cur:
        cur.execute("""
                   UPDATE users
                   SET  last_name = %s 
                   WHERE chat_id = %s
                   """, ('birthday', 12))
        print(cur.pgcode)

