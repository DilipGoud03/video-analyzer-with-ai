from database.connection import Connection
import mysql.connector
from enumeration.suitability import SuitabilityEnum

# ------------------------------------------------------------
# Class: VideoTableService
# Description:
#   Handles all CRUD operations for the 'videos' table.
#   Features include:
#     - Insert, update, delete, and fetch video records
#     - Filter and list videos by name, or category
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
            self.__db.commit()
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
    #   - Supports keyword search (ID, name, category) and suitability
    #   - Returns a list of dictionaries containing video details.
    # ------------------------------------------------------------
    def video_list(self, suitability: SuitabilityEnum, filter: str = ""):
        try:
            query = "SELECT * FROM `videos`"
            values = []
            if suitability:
                query += " WHERE `suitability` = %s"
                values.append(suitability)

            if filter:
                query += " AND (`id` LIKE %s OR `video_name` LIKE %s OR `category` LIKE %s)"
                search = f"%{filter}%"
                values.extend([search, search, search])

            with self.__db.cursor(dictionary=True) as cursor:
                cursor.execute(query, tuple(values))
                return cursor.fetchall()

        except mysql.connector.Error as e:
            raise ProcessLookupError(f"MySQL Query Failed: {e}")

    # ------------------------------------------------------------
    # Method: update_video
    # Description:
    #   Updates details for an existing video record.
    #   - Dynamically builds the UPDATE query based on non-empty fields.
    #   - Supports updating video type, category, and suitability.
    #   - Returns True on successful update.
    # ------------------------------------------------------------
    def update_video(self, video_name: str, category: str = "", suitability: str = "") -> bool:
        try:
            updates = []
            values = []

            if category and category.strip() != "":
                updates.append("`category` = %s")
                values.append(category)

            if suitability and suitability.strip() != "":
                updates.append("`suitability` = %s")
                values.append(suitability)

            if not updates:
                print("No fields to update.")
                return False

            query = f"UPDATE `videos` SET {', '.join(updates)} WHERE `video_name` = %s"
            values.append(video_name)

            with self.__db.cursor() as cursor:
                cursor.execute(query, tuple(values))
                if cursor.rowcount == 0:
                    print("No video found with that name.")
                    return False

            self.__db.commit()
            return True

        except mysql.connector.Error as e:
            print(f"MySQL error: {e}")
            return False
    