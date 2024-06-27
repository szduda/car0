
from time import sleep
import os

from drive_old import Drive
from keyboardSteering import KeyboardThread
from vehicleMonitor import BatteryMonitor

speed = 100  # if speed is set to less than 40 the motors might not work well
drive = Drive(12, 18, 13, 19)


def press(key):
  print(f'[{key}] pressed')

  global speed
  if key in map(str, range(3, 10)):
    speed = (int(key) + 1) * 10
    return

  match key:
    case 'w':
      drive.fwd(speed)
    case 's':
      drive.rev(speed)
    case 'a':
      drive.turn('l', speed)
    case 'd':
      drive.turn('r', speed)
    case 'space':
      drive.stop()
    case 'q':
      drive.deinit()


def release(key):
  if key != 'q':
    drive.stop()


keyboard_thread = KeyboardThread(press, release)
battery_monitor = BatteryMonitor(i2c_bus=1)

while True:
  os.system('clear')

  voltage, voltage_percent = battery_monitor.get_voltage()
  current, current_percent = battery_monitor.get_current()
  h, m = battery_monitor.get_time_until_discharge(voltage_percent, current)

  print('Battery info:\n\n')
  print('  %.1f V   (%.f%%)\n' % (voltage, voltage_percent))
  print('  %.f mA  (%.f%%)\n' % (current, current_percent))
  if h > 0:
    print(f'  {h}h {m}m  left')
  else:
    print(f'     {m}m  left')
  print("\n\n")

  sleep(1)
