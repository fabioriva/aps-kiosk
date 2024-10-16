import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from snap7 import Area
from time import sleep

class Rfid():
  def __init__(self, plc):
      self.plc = plc
      self.reader = SimpleMFRC522()

  def read(self):
      try:
            while 1:
                  id, text = self.reader.read()
                  print("ID: %s Text: %s" % (id, text))
                  buf = bytearray(id.to_bytes(6, byteorder='big'))
                  self.plc.write(Area.DB, 37, 18, buf)
                  sleep(0.5)
      except KeyboardInterrupt:
            GPIO.cleanup()

  def write(self, text):
      try:
        self.reader.write(text)
        print("Tag written: %s" % text)
      finally:
        GPIO.cleanup()
           
          
      