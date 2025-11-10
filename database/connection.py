import mysql.connector
from decouple import config
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


# Class: Connection
# -----------------
# Handles all MySQL database connection operations.
# - Connects to the database using credentials from environment variables.
# - Reuses an existing connection if one is already open.
# - Provides a method to safely close the connection.
class Connection:
    def __init__(self):
        # Initialize a private connection attribute (starts as None)
        self.__connection = None

    # Method: connect_db
    # --------------------
    # Establishes a connection to the MySQL database.
    # - Uses credentials (host, user, password, etc.) from environment variables.
    # - Creates a new connection if not already connected.
    # - Returns the active MySQL connection.
    # - Raises a ConnectionError if the connection fails.
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
