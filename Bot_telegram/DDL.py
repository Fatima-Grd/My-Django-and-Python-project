import mysql.connector
from config import *

def drop_n_create_database(database):
    conn = mysql.connector.connect(user=config['user'], password=config['password'], host=config['host'])
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {database};")
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {database};")
    conn.commit()
    cur.close()
    conn.close()
    print(f'database created successfully')
    
def create_table_Products():
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE Products (
                       product_id        INT NOT NULL AUTO_INCREMENT,
                       name              VARCHAR(50) NOT NULL,
                       description       VARCHAR(80),
                       price             DECIMAL(10, 2) NOT NULL,
                       inventory         INT NOT NULL DEFAULT 0,
                       created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                       PRIMARY KEY (product_id)
                       )AUTO_INCREMENT=100""") 
    conn.commit()
    cur.close()
    conn.close()
    print(f'table Products created successfully')

def create_table_Users():
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE Users (
                     user_id    INT AUTO_INCREMENT PRIMARY KEY,
                     username     VARCHAR(50),
                     first_name   VARCHAR(50),
                     last_name    VARCHAR(50),
                     gender       ENUM('male', 'female', 'other') DEFAULT NULL,
                     phone        VARCHAR(20),
                     join_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     last_active  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )AUTO_INCREMENT=100""")
    conn.commit()
    cur.close()
    conn.close()
    print(f'table Users created successfully')

def create_table_ShoppingCart():
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE ShoppingCart (
                   cart_item_id     INT AUTO_INCREMENT PRIMARY KEY,
                   user_id          INT NOT NULL,
                   product_id       INT NOT NULL,
                   quantity         INT NOT NULL DEFAULT 1,
                   created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   is_active        TINYINT(1) DEFAULT 1,
                   FOREIGN KEY (user_id) REFERENCES Users(user_id),
                   FOREIGN KEY (product_id) REFERENCES Products(product_id)
                )AUTO_INCREMENT=1000000""")
    conn.commit()
    cur.close()
    conn.close()
    print(f'table ShoppingCart created successfully')
    
def create_table_Orders():
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE Orders (
                   order_id        INT AUTO_INCREMENT PRIMARY KEY,
                   user_id         INT NOT NULL,
                   order_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   total_amount    DECIMAL(10, 2) NOT NULL,
                   payment_method  ENUM('credit', 'debit', 'cash') NOT NULL,
                   status          ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
                   FOREIGN KEY (user_id) REFERENCES Users(user_id)
                )AUTO_INCREMENT=1000000""")
    conn.commit()
    cur.close()
    conn.close()
    print(f'table Orders created successfully')

def create_table_OrderItems():
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE OrderItems (
                    order_item_id     INT AUTO_INCREMENT PRIMARY KEY,
                    order_id          INT NOT NULL,
                    product_id        INT NOT NULL,
                    quantity          INT NOT NULL DEFAULT 1,
                    price_at_purchase DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
                    FOREIGN KEY (product_id) REFERENCES Products(product_id)
                )AUTO_INCREMENT=1000000""")
    conn.commit()
    cur.close()
    conn.close()
    print(f'table OrderItems created successfully')

if __name__ == "__main__":
    #drop_n_create_database(DATABASE)
    create_table_Products()
    create_table_Users()
    create_table_ShoppingCart()
    create_table_Orders()
    create_table_OrderItems()
print("✅ تمام جداول با موفقیت ایجاد شدند")
