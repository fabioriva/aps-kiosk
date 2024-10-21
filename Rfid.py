import logging
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from snap7 import Area
from time import sleep

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
logging.getLogger(__name__)

GPIO.setwarnings(False)


class Rfid():
    def __init__(self, plc):
        self.plc = plc
        self.reader = SimpleMFRC522()

    def run(self):
        try:
            while 1:
                self.read()
                sleep(0.5)
        except KeyboardInterrupt:
            GPIO.cleanup()
        finally:
            GPIO.cleanup()

    def read(self):
        id, text = self.reader.read()
        logging.info(f'Tag ID {id}, Data: {text}')
        buf = bytearray(id.to_bytes(6, byteorder='big'))
        self.plc.write(Area.DB, 37, 18, buf)

    def write(self, text):
        self.reader.write(text)
        logging.info(f'Tag written: {text}')
