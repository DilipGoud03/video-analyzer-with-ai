from database.connection import Connection
import mysql.connector


# ------------------------------------------------------------
# Class: VideoTableService
# Description:
#   Handles all CRUD operations for the 'videos' table.
#   Features include:
#     - Insert, update, delete, and fetch video records
#     - Filter and list videos by name, or language
#     - Safe MySQL query execution with error handling
# ------------------------------------------------------------
class VideoTableService:
    # ------------------------------------------------------------
    # Method: __init__
    # Description:
    #   Initializes a new database connection using the
    #   Connection class. Establishes a persistent connection
    #   for all video-related operations.
    # ------------------------------------------------------------
    def __init__(self):
        self.__connection = Connection()
        self.__db = self.__connection.connect_db()

    # ------------------------------------------------------------
    # Method: add_video
    # Description:
    #   Inserts a new record into the 'videos' table.
    #   - Prevents duplicates by checking existing records first.
    #   - Returns True if insertion is successful, False otherwise.
    # ------------------------------------------------------------
    def add_video(self, video_name: str, video_type: int) -> bool:
        if not self.get_video_by_name(video_name):
            query = "INSERT INTO `videos` (`video_name`, `video_type`) VALUES (%s, %s)"
            with self.__db.cursor() as cursor:
                cursor.execute(query, (video_name, video_type))
            return True
        return False

    # ------------------------------------------------------------
    # Method: get_video_by_name
    # Description:
    #   Fetches a single video record using its name.
    #   - Returns a dictionary with video details if found, else None.
    #   - Raises LookupError in case of MySQL query failure.
    # ------------------------------------------------------------
    def get_video_by_name(self, name: str):
        try:
            query = "SELECT * FROM `videos` WHERE `video_name` = %s"
            with self.__db.cursor(dictionary=True) as cursor:
                cursor.execute(query, (name,))
                return cursor.fetchone()
        except mysql.connector.Error as e:
            raise LookupError(f"MySQL Query Failed: {e}")

    # ------------------------------------------------------------
    # Method: video_list
    # Description:
    #   Retrieves a list of videos with optional filtering.
    #   - Supports keyword search (ID, name, language)
    #   - Returns a list of dictionaries containing video details.
    # ------------------------------------------------------------
    def video_list(self, filter: str = ""):
        try:
            query = "SELECT * FROM `videos`"
            values = []

            if filter:
                query += " WHERE (`id` LIKE %s OR `video_name` LIKE %s OR `language` LIKE %s)"
                search = f"%{filter}%"
                values.extend([search, search, search])

            with self.__db.cursor(dictionary=True) as cursor:
                cursor.execute(query, tuple(values))
                return cursor.fetchall()

        except mysql.connector.Error as e:
            raise ProcessLookupError(f"MySQL Query Failed: {e}")
