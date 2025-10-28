import mysql.connector
from decouple import config
from dotenv import load_dotenv


load_dotenv()


class Connection:
    def __init__(self):
        self.__connection = None

    def connect_db(self):
        if not self.__connection or not self.__connection.is_connected():
            try:
                self.__connection = mysql.connector.connect(
                    host=config("HOST"),
                    user=config("USER"),
                    password=config("PASSWORD"),
                    database=config("DATABASE"),
                    port=config("PORT"),
                    autocommit=True
                )
            except mysql.connector.Error as e:
                raise ConnectionError(f"MySQL Connection Failed: {e}")
        return self.__connection

    def close_db(self):
        if self.__connection and self.__connection.is_connected():
            self.__connection.close()
