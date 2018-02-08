import pymysql


class DBase:

    def __init__(self, credentials):

        info = (credentials["dbhost"], credentials["dbuser"],
                credentials["dbpass"], credentials["dbname"])

        self.connection = pymysql.connect(host=info[0],
                                          user=info[1],
                                          password=info[2],
                                          db=info[3],
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def get_user(self, name):
        with self.connection.cursor() as cursor:
            sql = """
                  SELECT * FROM users 
                  WHERE psn_name = %s 
                  LIMIT 1
                  """
            cursor.execute(sql, name)
        self.connection.commit()
        return cursor.fetchone()

    def update_user_tokens (self, user_info):
        with self.connection.cursor() as cursor:
            sql = """
                  UPDATE users
                  SET access_token = %s, access_token_expire = %s, refresh_token = %s, refresh_token_expire = %s
                  """
            cursor.execute(sql, (user_info['access_token'],
                                 user_info['access_token_expire'],
                                 user_info['refresh_token'],
                                 user_info['refresh_token_expire']))
        self.connection.commit()

    def get_parsed_data(self, type, time):
        with self.connection.cursor() as cursor:
            sql = """
                  SELECT * FROM parsed_data
                  WHERE type = %s
                  AND expire > %s
                  ORDER BY id DESC
                  LIMIT 1
                  """
            cursor.execute(sql, (type, time))
        self.connection.commit()
        return cursor.fetchone()

    def add_parsed_data(self, type, json_data, added, expire, image_name):
        with self.connection.cursor() as cursor:
            sql = """
                  INSERT INTO parsed_data
                  (type, json_data, added, expire, image_name)
                  VALUES (%s, %s, %s, %s, %s)    
                  """
            cursor.execute(sql, (type, json_data, added, expire, image_name))
        self.connection.commit()
