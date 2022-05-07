import mysql.connector

class Database:
    def __init__(self, host, user, password, database):
        self.__db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.__cursor = self.__db.cursor()

    def get(self, sql):
        self.__cursor.execute(sql)

        return self.__cursor.fetchall()

    def insert_event(self, data):
        sql = "INSERT INTO events (id, title, source, image, created_at) VALUES (%s, %s, %s, %s, %s)"
        self.__cursor.execute(sql, data)
        self.__db.commit()
        print('[SUCCESS] New event fetched. [ID: ' + str(data[0]) + ']')

    def id_doesnt_exists(self, id):
        event = self.get("SELECT * FROM events WHERE id = " + str(id))

        if not event:
            return True

        return False

    def get_unposted_events(self):
        events = self.get("SELECT * FROM events WHERE is_posted = 0 ORDER BY created_at DESC")

        if not events:
            return False

        return events

    def mark_as_posted(self, events):
        sql = "UPDATE events SET is_posted = 1 WHERE id IN(" + str([event[0] for event in events])[1:-1] + ")"
        self.__cursor.execute(sql)
        self.__db.commit()
