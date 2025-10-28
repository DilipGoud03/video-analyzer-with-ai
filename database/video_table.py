from database.connection import Connection
import mysql.connector


class VideoTableService:
    def __init__(self):
        self.__connection = Connection()
        self.__db = self.__connection.connect_db()

    def add_video(self, video_name: str, video_type: int) -> bool:
        if not self.get_video_by_name(video_name):
            query = "INSERT INTO `videos` (`video_name`, `video_type`) VALUES (%s, %s)"
            with self.__db.cursor() as cursor:
                cursor.execute(query, (video_name, video_type))
            return True
        return False

    def delete_video(self, video_id: int) -> bool:
        query = "DELETE FROM `videos` WHERE `id` = %s"
        with self.__db.cursor() as cursor:
            cursor.execute(query, (video_id,))
        return True

    def get_video_by_name(self, name: str):
        try:
            query = "SELECT * FROM `videos` WHERE `video_name` = %s"
            with self.__db.cursor(dictionary=True) as cursor:
                cursor.execute(query, (name,))
                return cursor.fetchone()
        except mysql.connector.Error as e:
            raise LookupError(f"MySQL Query Failed: {e}")

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
