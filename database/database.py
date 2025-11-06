from aiomysql import DictCursor, connect
from pymysql import Error

import logging

from utils.logger import get_db_logger



class DataBase:
    def __init__(self, host: str, port: int, db_name: str, user: str, password: str):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user = user
        self.password = password

    async def execute(self, query: str, *parameters):
        cursor = await self.__execute(query, *parameters)
        return cursor.rowcount

    async def select_all(self, query: str, *parameters):
        cursor = await self.__execute(query, *parameters)
        return await cursor.fetchall()

    async def select_one(self, query: str, *parameters):
        cursor = await self.__execute(query, *parameters)
        return await cursor.fetchone()

    async def __execute(self, query: str, *parameters):
        try:
            con = await self.__open_connection()
            async with con.cursor() as cur:
                await cur.execute(query, parameters)
                return cur
        except Error as e:
            get_db_logger().log(logging.ERROR, f"Error while executing query [{query}]: {str(e)}")
            return None

    async def __open_connection(self):
        try:
            return await connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db_name,
                port=self.port,
                cursorclass=DictCursor,
                autocommit=True
                )
        except Error as e:
            get_db_logger().log(logging.ERROR, f"Error while opening sql connection: {str(e)}")
            return None

    async def create_tables(self):
        await self.execute(
            """
CREATE TABLE IF NOT EXISTS `cart` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT,
    `good_id` VARCHAR(10),
    `brand` INT
)            
"""
        )

    async def add_good_to_cart(self, user_id: int, good_id: str, brand: int):
        await self.execute(
            """INSERT INTO `cart` (`user_id`, `good_id`, `brand`)
VALUES (%s, %s, %s)""",
            user_id, good_id, brand
        )

    async def delete_from_cart(self, user_id: int, good_id: str, brand: int):
        await self.execute(
            """DELETE FROM `cart` WHERE `user_id` = %s AND `good_id` = %s
AND brand = %s LIMIT 1""",
            user_id, good_id, brand
        )

    
    async def delete_good_from_cart(self, user_id: int, good_id: str):
        await self.execute(
            """DELETE FROM `cart` WHERE `user_id` = %s AND `good_id` = %s""",
            user_id, good_id
        )

    async def get_user_cart(self, user_id):
        """Получение содержимого корзины пользователя, отдельно высчитывается количество каждого отдельного товара и сумма каждого отдельного товара"""
        return await self.select_all(
            '''SELECT `good_id`, `user_id`, count(`good_id`) as number, `brand` FROM `cart`
WHERE `user_id` = %s GROUP BY `good_id`''',
            user_id,
        )

    async def count_goods_in_cart(self, user_id, good_id, brand):
        cart_info = await self.select_one(
            """
SELECT count(`id`) as `number` FROM `cart` WHERE `user_id` = %s AND `good_id` = %s           
""",
            user_id, good_id
        )

        if cart_info:
            return cart_info['number']
        else:
            return None

    

    async def clear_user_cart(self, user_id):
        await self.execute(
            "DELETE FROM `cart` WHERE `user_id` = %s",
            user_id,
        )
