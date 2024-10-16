from Plc import Plc
from snap7 import Area
from socketify import App, AppOptions, OpCode, CompressOptions
from threading import Thread

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
    print('A WebSocket got connected!')
    # ws.send("Hello World!", OpCode.TEXT)
    ws.subscribe(PATH + '/info')


def ws_message(ws, message, opcode):
    # Ok is false if backpressure was built up, wait for drain
    # ok = ws.send(message, opcode)
    ws.publish(PATH, message, opcode)


def make_app(app, plc):
    app.ws("/*", {
        'compression': CompressOptions.SHARED_COMPRESSOR,
        'max_payload_length': 16 * 1024 * 1024,
        'idle_timeout': 0,
        'open': ws_open,
        'message': ws_message,
        'drain': lambda ws: print('WebSocket backpressure: %i' % ws.get_buffered_amount()),
        'close': lambda ws, code, message: print('WebSocket closed')
    })
    app.get(PATH + "/press", press_button)
    app.get(PATH + "/unpress", release_button)
    app.post(PATH + "/pin", pin)
    app.any("/*", lambda res, req: res.write_status(404).end("Not Found"))
    # S7 comm
    thread = Thread(target=plc.run, daemon=True)
    thread.start()


if __name__ == "__main__":
    app = App()
    plc = Plc(app)
    make_app(app, plc)
    app.listen(PORT, lambda config: print(
        "Listening on port http://localhost:%d now\n" % (config.port)))
    app.run()
