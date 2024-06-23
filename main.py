import RPi.GPIO as io
from time import sleep
from DFRobot_INA219 import INA219
import os
from sshkeyboard import listen_keyboard
from threading import Thread

##############################
# voltage and current sensor #
##############################

ina219_reading_mA = 1000
ext_meter_reading_mA = 1000

ina = INA219(1, INA219.INA219_I2C_ADDRESS4)

while not ina.begin():
  sleep(2)

ina.linear_cal(ina219_reading_mA, ext_meter_reading_mA)

MIN_VOLT = 2.7 * 2
MAX_VOLT = 4.1 * 2
MAX_mA = 2000.0

################
# motor driver #
################

speed = 100

io.setmode(io.BCM)

in1_pin = 12
in2_pin = 18
in3_pin = 13
in4_pin = 19

io.setup(in1_pin, io.OUT)
io.setup(in2_pin, io.OUT)
io.setup(in3_pin, io.OUT)
io.setup(in4_pin, io.OUT)

pwm1 = io.PWM(in2_pin, 500)
pwm2 = io.PWM(in4_pin, 500)

pwm1.start(0)
pwm2.start(0)


def fwd(duty=100):
  io.output(in1_pin, 1)
  # io.output(in2_pin, 0)
  io.output(in3_pin, 1)
  # io.output(in4_pin, 0)
  # pwm1.start(duty)
  pwm1.ChangeDutyCycle(100 - duty)
  pwm2.ChangeDutyCycle(100 - duty)


def rev(duty=100):
  io.output(in1_pin, 0)
  # io.output(in2_pin, 1)
  io.output(in3_pin, 0)
  # io.output(in4_pin, 1)
  pwm1.ChangeDutyCycle(duty)
  pwm2.ChangeDutyCycle(duty)


def stop():
  io.output(in1_pin, False)
  # io.output(in2_pin, False)
  io.output(in3_pin, False)
  # io.output(in4_pin, False)
  pwm1.ChangeDutyCycle(0)
  pwm2.ChangeDutyCycle(0)


def turn(side, duty=100):
  left = side == "l"
  left_duty = duty if left else 100 - duty
  io.output(in1_pin, not left)
  # io.output(in2_pin, left)
  io.output(in3_pin, left)
  # io.output(in4_pin, not left)
  pwm1.ChangeDutyCycle(left_duty)
  pwm2.ChangeDutyCycle(100 - left_duty)


####################
# keyboard control #
####################

def press(key):
  print(f'[{key}] pressed')

  global speed
  if key in map(str, range(3, 10)):
    speed = (int(key) + 1) * 10
    return

  match key:
    case 'w':
      fwd(speed)
    case 's':
      rev(speed)
    case 'a':
      turn('l', speed)
    case 'd':
      turn('r', speed)
    case 'space':
      stop()
    case 'q':
      stop()
      pwm1.stop()
      pwm2.stop()
      io.cleanup()


def release(key):
  if key != 'q':
    stop()


class KeyboardThread(Thread):

  def __init__(self) :
    super(KeyboardThread, self).__init__(name='keyboard-input-thread', daemon=True)
    self.start()

  def run(self):
    listen_keyboard(
      on_press=press,
      on_release=release,
    )


keyboard_thread = KeyboardThread()

while True:
  os.system('clear')

  voltage = ina.get_bus_voltage_V()
  voltage_percent = 100 * (voltage - MIN_VOLT) / (MAX_VOLT - MIN_VOLT)
  current = ina.get_current_mA()
  current_percent = 100 * current / MAX_mA

  print('Battery info:\n\n')
  print('  %.1f V   (%.f%%)\n' % (voltage, voltage_percent))
  print('  %.f mA  (%.f%%)\n\n' % (current, current_percent))

  sleep(1)
