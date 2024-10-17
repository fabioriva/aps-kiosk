from Plc import Plc
from Rfid import Rfid
from snap7 import Area
from socketify import App, CompressOptions
from threading import Thread
from time import sleep
import logging

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)


def log(handler):
    def devlog_route(res, req):
        logging.info(
            f'{req.get_method()} {req.get_full_url()} {req.get_headers()=}')
        handler(res, req)
    return devlog_route


PATH = "/api/kiosk"
PORT = 9999


async def pin(res, req):
    json = await res.get_json()
    pin = int(json["pin"], 16)
    buf = bytearray(pin.to_bytes(2, byteorder='big'))
    plc.write(Area.DB, 37, 16, buf)
    res.cork_end(json)


def press_button(res, req):
    plc.write(Area.DB, 37, 15, bytearray([1]))
    res.end({"message": "press button"})


def release_button(res, req):
    plc.write(Area.DB, 37, 15, bytearray([0]))
    res.end({"message": "release button"})


def ws_open(ws):
    ws.subscribe(PATH + '/info')


def ws_message(ws, message, opcode):
    ws.publish(PATH, message, opcode)


def make_app(app, plc, rfid):
    app.ws("/*", {
        'compression': CompressOptions.SHARED_COMPRESSOR,
        'max_payload_length': 16 * 1024 * 1024,
        'idle_timeout': 0,
        'open': ws_open,
        'message': ws_message,
        'drain': lambda ws: logging.info('WebSocket backpressure: %i' % ws.get_buffered_amount()),
        'close': lambda ws, code, message: logging.info('WebSocket closed')
    })
    app.get(PATH + "/press", log(press_button))
    app.get(PATH + "/unpress", log(release_button))
    app.post(PATH + "/pin", pin)
    app.any("/*", log(lambda res, req: res.write_status(404).end("Not Found")))
    # S7 comm
    thread = Thread(target=plc.run, daemon=True)
    thread.start()
    # MFRC522 rfid
    thread_rfid = Thread(target=rfid.read, daemon=True)
    thread_rfid.start()


if __name__ == "__main__":
    app = App()
    plc = Plc(app)
    rfid = Rfid(plc)
    make_app(app, plc, rfid)
    app.listen(PORT, lambda config: logging.info(
        "Listening on port http://localhost:%d now\n" % (config.port)))
    app.run()
