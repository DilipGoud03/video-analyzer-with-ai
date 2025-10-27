import mysql.connector
from decouple import config
from dotenv import load_dotenv


load_dotenv()


class Connection:
    def __init__(self) -> None:
        pass

    def connect_db(self):
        try:
            return mysql.connector.connect(
                host=str(config("HOST")),
                user=str(config("USER")),
                password=str(config("PASSWORD")),
                database=str(config("DATABASE")),
                port=str(config("PORT"))
            )
        except Exception as e:
            raise PermissionError(str(e))
