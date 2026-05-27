import pymysql
from pymysql.cursors import DictCursor
class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            host='localhost',
            user= 'root',
            password='root',
            port=3307,
            database='shoes',
            cursorclass=DictCursor
        )

    def login_user(self,login,password):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE login = %s and password = %s",(login,password))
            return cur.fetchone()

    def all_product(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name, description, price, quantity, image FROM products")
            return cur.fetchall()

    def all_categories(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name FROM categories")
            return cur.fetchall()

    def products_by_category(self, category_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name, description, price, quantity, image FROM products WHERE category_id = %s", (category_id,))
            return cur.fetchall()

    def add_product_bd(self, description, price, quantity, image):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO products (name, category_id, description, manufacture_id, supplier_id, price, quantity, discount, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (description, 1, description, 1, 1, price, quantity, 0, image)
            )
        self.conn.commit()

    def delete_product(self,id_prod):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM products WHERE id = %s",(id_prod,))
        self.conn.commit()

    def update_product(self,id_pro, description, price, quantity, image):
        with self.conn.cursor() as cur:
             cur.execute("UPDATE products SET description = %s, price = %s, quantity = %s, image = %s WHERE id = %s",( description, price, quantity, image,id_pro))
        self.conn.commit()


dao = Database()