from microdot.wsgi import Microdot, send_file, with_websocket
from microdot.sse import with_sse
from asyncio import sleep

from drive import Drive
from vehicleMonitor import BatteryMonitor

closing = False

speed = 0.6
angle = 0.0

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
      new_speed = int(cmd)
      if speed != 0:
        print(f'go with speed={new_speed} angle={angle}')
        drive.go(speed=new_speed, angle=angle)
        speed = new_speed
        await ok()
      else:
        print('request ignored; for now speed can be changed only while driving')
      continue

    if ':' in cmd:
      param, value_str = cmd.split(':')
      if param == 'speed':
        if value_str not in ["0", ""]:
          new_speed = float(value_str)
          speed = new_speed
          print(f'go with speed={speed} new_speed={new_speed} angle={angle}')
          drive.go(speed=speed, angle=angle)
        else:
          print(f'go with speed 0? wat? ah, ok - just stop')
          drive.stop()

      if param == 'angle':
        if speed != 0:
          new_angle = float(value_str)
          angle = new_angle
          print(f'go with speed={speed} new_angle={new_angle}, angle={angle}')
          drive.go(speed=speed, angle=angle)
        else:
          print('can\'t touch this (angle when speed=0)')

      continue

    match cmd:
      case 'rtl':
        print(f'rotate left')
        drive.rotate('left')
        await ok()
      case 'rtr':
        print(f'rotate right')
        drive.rotate('right')
        await ok()
      case 'stp':
        print('drive stop')
        drive.stop()
        speed = 0
        await ok()
      case 'bye':
        print('drive deinit; closing=True')
        drive.deinit()
        closing = True
        await ws.send('farewell')
      case _:
        print('unknown command')
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
