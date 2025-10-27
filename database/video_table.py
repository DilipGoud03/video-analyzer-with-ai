from database.connection import Connection


class VideoTableService:
    def __init__(self) -> None:
        self.__connection = Connection()
        self.__db = self.__connection.connect_db()

    def add_video(self, video_name: str, video_path: str, video_type: int):
        db = self.__db.cursor()
        query = "INSERT INTO `videos` (`video_name`, `video_path`, `video_type`) VALUES (%s, %s, %s)"
        db.execute(query, (video_name, video_path, video_type))
        self.__db.commit()
        db.close()

    def delete_video(self, id):
        query = f"DELETE FROM `videos` WHERE id = 1"

    def get_video_by_name(self, name: str):
        try:
            db = self.__db.cursor(dictionary=True)
            query = "SELECT * FROM `videos` WHERE `video_name` = %s"
            db.execute(query, (name,))
            data = db.fetchone()
            db.close()
            return data
        except Exception as e:
            raise LookupError(str(e))
