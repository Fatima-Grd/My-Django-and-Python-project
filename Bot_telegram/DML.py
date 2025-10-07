import mysql.connector
from config import *

def insert_sample_products():
    products = [
        (100, 'pen', 'blue', 10.00, 100),
        (101, 'pencil', 'black', 8.00, 7),
        (102, 'ruler', '30CM', 20.00, 10),
        (103, 'eraser', 'white', 15.00, 40)
    ]
    
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    # ابتدا بررسی کنیم که آیا محصولات وجود دارند یا نه
    for product in products:
        product_id = product[0]
        cur.execute("SELECT * FROM Products WHERE product_id = %s", (product_id,))
        existing_product = cur.fetchone()
        
        if existing_product:
            print(f"⚠️ محصول با کد {product_id} از قبل وجود دارد - به روزرسانی می‌شود")
            cur.execute("""
                UPDATE Products 
                SET name = %s, description = %s, price = %s, inventory = %s 
                WHERE product_id = %s
            """, (product[1], product[2], product[3], product[4], product_id))
        else:
            print(f"✅ درج محصول جدید با کد {product_id}")
            cur.execute("""
                INSERT INTO Products (product_id, name, description, price, inventory)
                VALUES (%s, %s, %s, %s, %s)
            """, product)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ نمونه محصولات با موفقیت درج/به‌روزرسانی شدند")

def insert_product_data(product_id, name, description, price, inventory):
    """تابع جدید برای درج محصول"""
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    try:
        # بررسی وجود محصول
        cur.execute("SELECT * FROM Products WHERE product_id = %s", (product_id,))
        if cur.fetchone():
            print(f"⚠️ محصول با کد {product_id} از قبل وجود دارد")
            return False
        
        cur.execute("""
            INSERT INTO Products (product_id, name, description, price, inventory)
            VALUES (%s, %s, %s, %s, %s)
        """, (product_id, name, description, price, inventory))
        conn.commit()
        print(f"✅ محصول {product_id} با موفقیت درج شد")
        return True
    except Exception as e:
        print(f"❌ خطا در درج محصول: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def add_product_mid(product_data):
    """تابع جدید برای افزودن محصول از طریق ربات"""
    if len(product_data) == 5:
        return insert_product_data(*product_data)
    else:
        print("❌ داده‌های محصول ناقص است")
        return False

def insert_sample_users():
    users = [
        (100, 'ali_username', 'Ali', 'Alavi', 'male', '09121112222'),
        (101, 'reza_user', 'Reza', 'Rezaei', 'male', '09123334444'),
        (102, 'maryam_2023', 'Maryam', 'Mohammadi', 'female', '09125556666')
    ]
    
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    for user in users:
        user_id = user[0]
        cur.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
        if cur.fetchone():
            print(f"⚠️ کاربر با کد {user_id} از قبل وجود دارد - به روزرسانی می‌شود")
            cur.execute("""
                UPDATE Users 
                SET username = %s, first_name = %s, last_name = %s, gender = %s, phone = %s 
                WHERE user_id = %s
            """, (user[1], user[2], user[3], user[4], user[5], user_id))
        else:
            print(f"✅ درج کاربر جدید با کد {user_id}")
            cur.execute("""
                INSERT INTO Users (user_id, username, first_name, last_name, gender, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, user)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ نمونه کاربران با موفقیت درج/به‌روزرسانی شدند")

def create_sample_shopping_cart_items():
    cart_items = [
        (100, 100, 2),
        (100, 101, 1),
        (101, 102, 1),
        (102, 103, 3)
    ]
    
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    # حذف موارد قبلی
    cur.execute("DELETE FROM ShoppingCart")
    
    for item in cart_items:
        cur.execute("""
            INSERT INTO ShoppingCart (user_id, product_id, quantity)
            VALUES (%s, %s, %s)
        """, item)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ نمونه موارد سبد خرید با موفقیت درج شدند")

def create_sample_orders():
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    # حذف داده‌های قبلی
    cur.execute("DELETE FROM OrderItems")
    cur.execute("DELETE FROM Orders")
    
    orders = [
        (1000000, 100, 28.00, 'credit', 'completed'),
        (1000001, 101, 20.00, 'debit', 'completed'),
        (1000002, 102, 45.00, 'cash', 'pending')
    ]
    
    for order in orders:
        cur.execute("""
            INSERT INTO Orders (order_id, user_id, total_amount, payment_method, status)
            VALUES (%s, %s, %s, %s, %s)
        """, order)
    
    order_items = [
        (1000000, 100, 2, 10.00),
        (1000000, 101, 1, 8.00),
        (1000001, 102, 1, 20.00),
        (1000002, 103, 3, 15.00)
    ]
    
    for item in order_items:
        cur.execute("""
            INSERT INTO OrderItems (order_id, product_id, quantity, price_at_purchase)
            VALUES (%s, %s, %s, %s)
        """, item)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ نمونه سفارشات با موفقیت درج شدند")

if __name__ == "__main__":
    try:
        insert_sample_products()
        insert_sample_users()
        create_sample_shopping_cart_items()
        create_sample_orders()
        print("✅ پایگاه داده با موفقیت پر شد")
    except Exception as e:
        print(f"❌ خطا در پر کردن پایگاه داده: {e}")



