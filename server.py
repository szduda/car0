from microdot.wsgi import Microdot, send_file, with_websocket
from microdot.sse import with_sse
from asyncio import sleep

from drive import Drive
from vehicleMonitor import BatteryMonitor

closing = False

speed = 60
angle = 30

drive = Drive(12, 18, 13, 19)

app = Microdot()
battery_monitor = BatteryMonitor(i2c_bus=1)


@app.route('/')
async def index(request):
  return send_file('static/index.html')


@app.route('/monitor')
@with_sse
async def monitor(request, sse):
  global closing
  while not closing:
    voltage, voltage_percent = battery_monitor.get_voltage()
    current, current_percent = battery_monitor.get_current()
    h, m = battery_monitor.get_time_until_discharge(voltage_percent, current)
    await sleep(2)
    await sse.send({
      'v': voltage,
      'vp': voltage_percent,
      'c': current,
      'cp': current_percent,
      'h': h,
      'm': m,
    })

  print('SSE endpoint closed')


@app.route('/steer')
@with_websocket
async def steer(request, ws):
  global speed, closing, angle
  while not closing:
    cmd = str(await ws.receive())
    print(f'[{cmd}] command received')

    async def ok():
      await ws.send('ok')

    if cmd in map(str, range(3, 10)):
      new_speed = (int(cmd) + 1) / 10.0
      if speed > 0:
        drive.go(speed=new_speed, angle=angle)
      speed = new_speed
      await ok()
      continue

    if ':' in cmd:
      param, value_str = cmd.split(':')
      if param == 'speed':
        speed = int(value_str) / 10.0
        if speed != 0:
          drive.go(speed=speed, angle=angle)
        else:
          drive.stop()

      if param == 'angle':
        angle = float(value_str)
        if speed != 0:
          drive.go(speed=speed, angle=angle)

    match cmd:
      case 'rtl':
        drive.rotate('left')
        await ok()
      case 'rtr':
        drive.rotate('right')
        await ok()
      case 'stp':
        drive.stop()
        speed = 0
        await ok()
      case 'bye':
        drive.deinit()
        closing = True
        await ws.send('farewell')
      case _:
        await ws.send('unknown command')

  print('WS endpoint closed')


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
