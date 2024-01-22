import mysql.connector
import time
import datetime
import cv2

from threading import Thread

class Db_connector:
    def __init__(self, host, user, passwd, database, lock):

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

        #!!! DELETE IN PRODUCTION !!!
        Q1 = 'TRUNCATE TABLE exception'                 # !!! DELETE IN PRODUCTION !!!
        Q2 = 'TRUNCATE TABLE fines'                     # !!! DELETE IN PRODUCTION !!!
        self._cursor.execute(Q1)                        # !!! DELETE IN PRODUCTION !!!
        self._cursor.execute(Q2)                        # !!! DELETE IN PRODUCTION !!!
    
        self.stopped = False

        self.lock = lock
        
        self.synchronize = False
        self.last_processed = ''

    def start_db_supervison(self, Plates_local_databe):
        Thread(target= self._db_supervisor, args= (Plates_local_databe,)).start()

    def stop_db_supervisor(self):
        self.stopped = True

    def _db_supervisor(self, Plates_local_databe):
        while True:
            if self.stopped:
                break
            else:                                       #part of code to sync data with database
                if self.synchronize:
                    if len(Plates_local_databe.get_local_plates()) > 0:
                        self.lock.acquire()
                        bufor = Plates_local_databe.get_local_plates()[-1]
                        self.lock.release()
                        Plates_local_databe.delete_plate(bufor)
                        if bufor != self.last_processed:
                            self.last_processed = bufor
                            if self._check_exist(bufor):
                                if not self._check_ticket(bufor):
                                    self._add_fine(bufor)
                                    print(bufor, "got fine")
                                    #cv2.waitKey()
                            else:
                                self._add_exception(bufor)

                    else:
                        self.synchronize = False
                else:
                    time.sleep(10)
                

    def _check_ticket(self, plate_no): 
        Q = 'SELECT COUNT(tickets.ticket_id) FROM plate_detector.tickets WHERE  number_plate = (SELECT plates.plate_id FROM plate_detector.plates WHERE plates.plate_no = "' + plate_no + '")'
        self._cursor.execute(Q)
        results = [i[0] for i in self._cursor]
        if int(results[0]) >= 1:
            Q = 'SELECT max(tickets.expire_time) FROM plate_detector.tickets WHERE  number_plate = (SELECT plates.plate_id FROM plate_detector.plates WHERE plates.plate_no = "' + plate_no + '")'
            self._cursor.execute(Q)
            results = [i[0] for i in self._cursor]
            result = results[0]
            now = datetime.datetime.now()
            if result <= now:
                print(plate_no, " has expierd ticket")
                return False
            else:
                return True
        else:
            print(plate_no, " has no ticket")
            return False

    def _check_exist(self, plate_no):
        Q = 'SELECT COUNT(plates.plate_id) FROM plate_detector.plates WHERE plates.plate_no = "' + plate_no + '"'
        self._cursor.execute(Q)
        results = [i[0] for i in self._cursor]
        if results[0] == 1:
            return True
        else:
            print(plate_no, " does not exist")
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