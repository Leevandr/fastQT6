import pymysql
from pymysql.cursors import DictCursor


class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            database="shoes",
            user="root",
            password="",
            port=3308,
            host="localhost",
            cursorclass=DictCursor
        )

    def cursor(self):
        return self.conn.cursor()

    def login(self, login, password):
        with self.cursor() as cur:
            cur.execute("select * from users where password = %s and login = %s", (password, login))
        return cur.fetchone()

    def get_all_products(self, search="", quantity="По умолчанию", suppiler="Все поставщики"):

        sql = """
              select p.id,
                     p.article,
                     p.title,
                     c.title      as category,
                     p.description,
                     m.title      as manufacture,
                     s.title      as suppiler,
                     p.price,
                     u.title      as unit,
                     p.quantity,
                     p.discount,
                     p.image_path as image
              from products p
                       join categories c on c.id = p.category_id
                       join manufactures m on m.id = p.manufacture_id
                       join suppilers s on s.id = p.suppiler_id
                       join units u on u.id = p.unit_id
                  where (p.article LIKE %s
                     or p.title LIKE %s
                     or p.description LIKE %s
                     or c.title LIKE %s
                     or m.title LIKE %s
                     or s.title LIKE %s
                     or u.title LIKE %s)
              """
        search_params = f'%{search}%'
        params = [
            search_params,
            search_params,
            search_params,
            search_params,
            search_params,
            search_params,
            search_params,
        ]

        if suppiler and suppiler != "Все поставщики":
            sql += ' and s.title = %s'
            params.append(suppiler)

        if quantity == "По возрастанию":
            sql += " order by p.quantity asc"
        elif quantity == "По убыванию":
            sql += " order by p.quantity desc"
        else:
            sql += " order by p.id asc"

        with self.cursor() as cur:
            cur.execute(sql, params)
        return cur.fetchall()

    def get_all_categories(self):
        with self.cursor() as cur:
            cur.execute("select * from categories")
        return cur.fetchall()

    def get_all_manufactures(self):
        with self.cursor() as cur:
            cur.execute("select * from manufactures")
        return cur.fetchall()

    def get_all_suppilers(self):
        with self.cursor() as cur:
            cur.execute("select * from suppilers")
        return cur.fetchall()

    def get_all_units(self):
        with self.cursor() as cur:
            cur.execute("select * from units")
        return cur.fetchall()

    def add_new_product(self, article, title, category_id, description, manufacture_id, suppiler_id, price, unit_id,
                        quantity, discount, image):
        with self.cursor() as cur:
            cur.execute(
                "insert into products(article,title,category_id,description,manufacture_id,suppiler_id,price,unit_id,quantity,discount,image_path)"
                "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (article, title, category_id, description, manufacture_id, suppiler_id, price, unit_id, quantity,
                 discount, image))
            cur.connection.commit()

    def get_unit_id(self, name):
        with self.cursor() as cur:
            cur.execute("select * from units where title = %s", (name,))
        return cur.fetchone()

    def get_suppiler_id(self, name):
        with self.cursor() as cur:
            cur.execute("select * from suppilers where title = %s", (name,))
        return cur.fetchone()

    def get_manufacture_id(self, name):
        with self.cursor() as cur:
            cur.execute("select * from manufactures where title = %s", (name,))
        return cur.fetchone()

    def get_category_id(self, name):
        with self.cursor() as cur:
            cur.execute("select * from categories where title = %s", (name,))
        return cur.fetchone()

    def edit_product(self, product_id, article, title, category_id, description, manufacture_id, suppiler_id, price,
                     unit_id, quantity, discount, image):
        with self.cursor() as cur:
            cur.execute("update products set "
                        "article = %s,"
                        "title = %s,"
                        "category_id = %s,"
                        "description = %s,"
                        "manufacture_id = %s,"
                        "suppiler_id = %s,"
                        "price = %s,"
                        "unit_id = %s,"
                        "quantity = %s,"
                        "discount = %s,"
                        "image_path = %s where id = %s",
                        (article, title, category_id, description, manufacture_id, suppiler_id, price, unit_id,
                         quantity, discount, image, product_id))
            cur.connection.commit()

    def delete_product(self, p_id):
        try:
            with self.cursor() as cur:
                cur.execute("delete from products where id = %s", (p_id,))
                cur.connection.commit()
            return True
        except pymysql.err.IntegrityError:
            return False

    def get_all_orders(self):
        with self.cursor() as cur:
            cur.execute("""
                select o.id,
                       o.product_id,
                       o.status_id,
                       o.pickup_point_id,
                       o.order_date,
                       o.delivery_date,
                       o.user_id,
                       p.article as article,
                       p.title as product,
                       os.title as status,
                       pp.address as pickup
                from orders o
                    join products p on p.id = o.product_id
                    join order_statuses os on os.id = o.status_id
                    join pickup_points pp on pp.id = o.pickup_point_id
                order by o.id desc
            """)
        return cur.fetchall()

    def get_all_statuses(self):
        with self.cursor() as cur:
            cur.execute("select * from order_statuses")
        return cur.fetchall()

    def get_all_pickup_points(self):
        with self.cursor() as cur:
            cur.execute("select * from pickup_points")
        return cur.fetchall()

    def add_order(self, product_id, status_id, pickup_point_id, order_date, delivery_date, user_id):
        with self.cursor() as cur:
            cur.execute(
                "insert into orders(product_id,status_id,pickup_point_id,order_date,delivery_date,user_id) "
                "values (%s,%s,%s,%s,%s,%s)",
                (product_id, status_id, pickup_point_id, order_date, delivery_date, user_id)
            )
            cur.connection.commit()

    def edit_order(self, order_id, product_id, status_id, pickup_point_id, order_date, delivery_date, user_id):
        with self.cursor() as cur:
            cur.execute(
                "update orders set product_id = %s, status_id = %s, pickup_point_id = %s, "
                "order_date = %s, delivery_date = %s, user_id = %s where id = %s",
                (product_id, status_id, pickup_point_id, order_date, delivery_date, user_id, order_id)
            )
            cur.connection.commit()

    def delete_order(self, order_id):
        with self.cursor() as cur:
            cur.execute("delete from orders where id = %s", (order_id,))
            cur.connection.commit()


dao = Database()
