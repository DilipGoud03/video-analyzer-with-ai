from database.connection import Connection
import mysql.connector


# Class: VideoTableService
# ------------------------
# Manages all operations related to the 'videos' table in the database.
# Features:
# - Add, update, delete, and fetch video records.
# - Filter videos by name, category, or language.
# - Handles MySQL errors gracefully and ensures clean query execution.
class VideoTableService:
    def __init__(self):
        # Initialize a database connection using the Connection class
        self.__connection = Connection()
        self.__db = self.__connection.connect_db()

    # Function: add_video
    # -------------------
    # Adds a new video record to the 'videos' table.
    # - Checks if the video already exists before inserting.
    # - Returns True if insertion is successful, False otherwise.
    def add_video(self, video_name: str, video_type: int) -> bool:
        if not self.get_video_by_name(video_name):
            query = "INSERT INTO `videos` (`video_name`, `video_type`) VALUES (%s, %s)"
            with self.__db.cursor() as cursor:
                cursor.execute(query, (video_name, video_type))
            return True
        return False

    # Function: delete_video
    # ----------------------
    # Deletes a video record from the database based on its ID.
    # - Returns True if deletion is successful.
    def delete_video(self, video_id: int) -> bool:
        query = "DELETE FROM `videos` WHERE `id` = %s"
        with self.__db.cursor() as cursor:
            cursor.execute(query, (video_id,))
        return True

    # Function: get_video_by_name
    # ----------------------------
    # Fetches a video record by its name.
    # - Returns a dictionary containing video details if found, else None.
    # - Raises LookupError if the MySQL query fails.
    def get_video_by_name(self, name: str):
        try:
            query = "SELECT * FROM `videos` WHERE `video_name` = %s"
            with self.__db.cursor(dictionary=True) as cursor:
                cursor.execute(query, (name,))
                return cursor.fetchone()
        except mysql.connector.Error as e:
            raise LookupError(f"MySQL Query Failed: {e}")

    # Function: video_list
    # --------------------
    # Retrieves a list of videos with optional filters.
    # - Supports filtering by keyword (id, name, or language).
    # - Supports category-based filtering (e.g., 'All', 'Music', 'Education', etc.).
    # - Returns a list of video records as dictionaries.
    def video_list(self, filter: str = "", category: str = ""):
        try:
            query = "SELECT * FROM `videos`"
            values = []

            conditions = []
            if filter:
                query += " WHERE (`id` LIKE %s OR `video_name` LIKE %s OR `language` LIKE %s)"
                search = f"%{filter}%"
                values.extend([search, search, search])

            if category and category.lower() != "all":
                if filter:
                    query += " AND "
                else:
                    query += " WHERE "
                query += "`category` = %s"
                values.append(category)

            with self.__db.cursor(dictionary=True) as cursor:
                cursor.execute(query, tuple(values))
                return cursor.fetchall()
        except mysql.connector.Error as e:
            raise ProcessLookupError(f"MySQL Query Failed: {e}")

    # Function: update_video
    # ----------------------
    # Updates existing video details in the database.
    # - Accepts optional fields like type, category, language, and suitability.
    # - Builds the SQL UPDATE query dynamically based on provided values.
    # - Returns True after successful update.
    def update_video(self, video_id: int, video_type: int, video_category: str, language: str, suitability: str) -> bool:
        query = "UPDATE `videos` SET "
        values = []
        updates = []

        if video_type is not None:
            updates.append("`video_type` = %s")
            values.append(video_type)
        if video_category:
            updates.append("`video_category` = %s")
            values.append(video_category)
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
