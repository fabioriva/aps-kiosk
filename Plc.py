import snap7
import time
from socketify import OpCode

CHANNEL = "/api/kiosk/info"
IP = "192.168.20.55"
POLL = 0.5
RACK = 0
SLOT = 1


class Plc():
    def __init__(self, app):
        self.app = app
        self.client = snap7.client.Client()
        self.online = False
        self.data = dict()

    def connect(self):
        try:
            self.client.connect(IP, RACK, SLOT)
            self.online = self.client.get_connected()
        except Exception as e:
            self.err(e)

    def err(self, err):
        print("exception error:", err)
        e = self.client.get_last_error()
        print("snap7 error:", e, self.client.error_text(e))
        self.online = self.client.disconnect()

    def read(self, db, start, size):
        try:
            buffer = self.client.db_read(db, start, size)
            return {
                "comm": self.online,
                "lang": int.from_bytes(buffer[0:2], "big"),
                "page": int.from_bytes(buffer[2:4], "big"),
                "card": int.from_bytes(buffer[4:6], "big"),
                "digitNr": int.from_bytes(buffer[6:8], "big"),
                "errMesg": int.from_bytes(buffer[8:10], "big"),
                "successMesg": int.from_bytes(buffer[10:12], "big")
            }
        except Exception as e:
            self.err(e)

    def write(self, area, dbNr, start, buffer):
        try:
            # print(area, dbNr, start, buffer)
            # res = self.client.db_write(dbNr, start, buffer)
            res = self.client.write_area(area, dbNr, start, buffer)
            return res
        except Exception as e:
            self.err(e)

    def run(self):  # , f):
        self.connect()
        while 1:
            if (self.online):
                self.data = self.read(37, 2, 12)
                # watchdog DB37.DBX14.0
                self.write(snap7.Area.DB, 37, 14, bytearray([0b00000001]))
            else:
                self.data = dict(comm=False, lang=0, page=0, card=0,
                                 digitNr=0, errMesg=0, succesMsg=0)
                self.connect()
                print(
                    "Connected to PLC %s" % IP if self.online else "Connecting to PLC %s...." % IP)

            self.app.publish(CHANNEL, self.data,
                             opcode=OpCode.TEXT, compress=False)
            time.sleep(POLL)
