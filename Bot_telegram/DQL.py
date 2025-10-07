import mysql.connector
from config import config

def get_product_data(PRODUCT_ID):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor(dictionary=True)
    SQL_Query = "SELECT * FROM Products WHERE product_id=%s"
    cur.execute(SQL_Query, (PRODUCT_ID,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result[0] if result else None

if __name__ == "__main__":
    data = get_product_data(100)
    print(data)
