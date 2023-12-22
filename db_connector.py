import mysql.connector

from threading import Thread

class db_connector:
    def __init__(self, host, user, passwd, database):

        self._db = mysql.connector.connect(
            host = host,
            user = user,
            passwd = passwd,
            database = database
        )

        if self._db.is_connected():
            self.is_connected = True
            self._cursor = self._db.cursor()
        else:
            self.is_connected = False

        self.stopped = False

    def start_db_supervison(self):
        Thread(target= self._db_supervisor, args= ()).start()

    def stop_db_supervisor(self):
        self.stopped = True

    def _db_supervisor(self):
        while True:
            if self.stopped:
                break
            else:
                #part of code to sync data with database
                pass

    def _check_exist(self, plate_no):
        Q = 'SELECT COUNT(plates.plate_id) FROM plate_detector.plates WHERE plates.plate_no = "' + plate_no + '"'
        self._cursor.execute(Q)
        results = [i[0] for i in self._cursor]
        if results[0] == 1:
            return True
        else:
            return False
        

    def _add_fine(self, plate_no):
        Q = 'INSERT INTO `plate_detector`.`fines`(`number_plate`) SELECT plates.plate_id FROM plate_detector.plates WHERE plates.plate_no = "' + plate_no + '"'
        self._cursor.execute(Q)
        self._db.commit()

    def _add_exception(self, plate_no):
        Q = 'SELECT COUNT(exception.exception_id) FROM plate_detector.exception WHERE exception.exception_plate_number = "' + plate_no + '"'
        self._cursor.execute(Q)
        results = [i[0] for i in self._cursor]
        if results[0] != 1:
            Q = 'INSERT INTO `plate_detector`.`exception`(`exception_plate_number`) VALUES ("' + plate_no + '")'
            self._cursor.execute(Q)
            self._db.commit()

database = db_connector("localhost", "root", "root", "plate_detector")