import pymysql


class DBase:

    def __init__(self, credentials):
        self.info = (credentials["dbhost"], credentials["dbuser"],
                     credentials["dbpass"], credentials["dbname"])

    def get_user(self, name):
        connection = self.__make_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                      SELECT * FROM users 
                      WHERE psn_name = %s 
                      LIMIT 1
                      """
                cursor.execute(sql, name)
            connection.commit()
            return cursor.fetchone()
        finally:
            connection.close()

    def update_user_tokens (self, user_info):
        connection = self.__make_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                      UPDATE users
                      SET access_token = %s, access_token_expire = %s, refresh_token = %s, refresh_token_expire = %s
                      """
                cursor.execute(sql, (user_info['access_token'],
                                     user_info['access_token_expire'],
                                     user_info['refresh_token'],
                                     user_info['refresh_token_expire']))
            connection.commit()
        finally:
            connection.close()

    def get_parsed_data(self, type, time):
        connection = self.__make_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                      SELECT * FROM parsed_data
                      WHERE type = %s
                      AND expire > %s
                      ORDER BY id DESC
                      LIMIT 1
                      """
                cursor.execute(sql, (type, time))
                connection.commit()
            return cursor.fetchone()
        finally:
            connection.close()

    def add_parsed_data(self, type, json_data, added, expire, image_name):
        connection = self.__make_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                      INSERT INTO parsed_data
                      (type, json_data, added, expire, image_name)
                      VALUES (%s, %s, %s, %s, %s)    
                      """
                cursor.execute(sql, (type, json_data, added, expire, image_name))
            connection.commit()
        finally:
            connection.close()

    def __make_connection(self):
        return pymysql.connect(host=self.info[0],
                                          user=self.info[1],
                                          password=self.info[2],
                                          db=self.info[3],
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)
