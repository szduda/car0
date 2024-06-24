from microdot.wsgi import Microdot, send_file, with_websocket
from microdot.sse import with_sse
from asyncio import sleep

from drive import Drive
from vehicleMonitor import BatteryMonitor

closing = False

speed = 100
drive = Drive(12, 18, 13, 19)

app = Microdot()
battery_monitor = BatteryMonitor(i2c_bus=1)


@app.route('/')
async def index(request):
  return send_file('static/index.html')


@app.route('/monitor')
@with_sse
async def monitor(request, sse):
  while not closing:
    voltage, voltage_percent = battery_monitor.get_voltage()
    current, current_percent = battery_monitor.get_current()
    h, m = battery_monitor.get_time_until_discharge(voltage_percent, current)
    await sleep(1)
    await sse.send({voltage, voltage_percent, current, current_percent, h, m})


@app.route('/steer')
@with_websocket
async def steer(request, ws):
  while True:
    cmd = await ws.receive()
    print(f'[{cmd}] command received')

    async def ok(): await ws.send('ok')

    global speed, closing

    if cmd in map(str, range(3, 10)):
      speed = (int(cmd) + 1) * 10
      await ok()
      continue

    match cmd:
      case 'fwd':
        drive.fwd(speed)
        await ok()
      case 'rev':
        drive.rev(speed)
        await ok()
      case 'rtl':
        drive.turn('l', speed)
        await ok()
      case 'rtr':
        drive.turn('r', speed)
        await ok()
      case 'stp':
        drive.stop()
        await ok()
      case 'bye':
        closing = True
        drive.deinit()
        await ws.send('farewell')
      case _:
        await ws.send('unknown command')


@app.route("/static/<path:path>")
def static(request, path):
    if ".." in path:
        # directory traversal is not allowed
        return "Not found", 404
    return send_file("static/" + path)


if __name__ == '__main__':
  try:
    print("Starting the server...")
    app.run()
  except KeyboardInterrupt:
    print("Deinitializing vehicle control...")
    drive.deinit()
    print("Server closed.")

