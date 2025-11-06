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
    # Method: delete_video
    # Description:
    #   Deletes a video record from the 'videos' table based on ID.
    #   - Returns True when deletion is successful.
    # ------------------------------------------------------------
    def delete_video(self, video_id: int) -> bool:
        query = "DELETE FROM `videos` WHERE `id` = %s"
        with self.__db.cursor() as cursor:
            cursor.execute(query, (video_id,))
        return True

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
            conditions = []

            if filter:
                query += " WHERE (`id` LIKE %s OR `video_name` LIKE %s OR `language` LIKE %s)"
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
    #   - Supports updating video type, language, and suitability.
    #   - Returns True on successful update.
    # ------------------------------------------------------------
    def update_video(
        self,
        video_id: int,
        video_type: int,
        video_category: str,
        language: str,
        suitability: str
    ) -> bool:

        query = "UPDATE `videos` SET "
        values = []
        updates = []

        if video_type is not None:
            updates.append("`video_type` = %s")
            values.append(video_type)

        if language:
            updates.append("`language` = %s")
            values.append(language)
        
        if suitability:
            updates.append("`suitability` = %s")
            values.append(suitability)

        query += ", ".join(updates) + " WHERE `id` = %s"
        values.append(video_id)

        with self.__db.cursor() as cursor:
            cursor.execute(query, tuple(values))
        return True
