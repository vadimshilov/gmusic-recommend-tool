import sqlite3
from db.Migration import update_database_if_necessary


class Connection:
    __instance = None

    @staticmethod
    def instance():
        if Connection.__instance is None:
            Connection.__instance = Connection()
        return Connection()

    def __init__(self):
        self.connection = sqlite3.connect("db.db")
        self.connection.isolation_level = None
        update_database_if_necessary(self.connection)

    def get_cursor(self):
        return self.connection.cursor()

    def close(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()