import RPi.GPIO as io


class Drive:
  PWM_FREQ = 500
  MIN_DUTY = 40

  pwm1 = None
  pwm2 = None

  speed = 0.0
  turn_angle = 0.0
  performance = 1.0

  def __init__(self, p1, p2, p3, p4):

    self.in1_pin = p1
    self.in2_pin = p2
    self.in3_pin = p3
    self.in4_pin = p4

    self.init()

  def init(self):
      io.setmode(io.BCM)
      io.setup(self.in1_pin, io.OUT)
      io.setup(self.in2_pin, io.OUT)
      io.setup(self.in3_pin, io.OUT)
      io.setup(self.in4_pin, io.OUT)

      self.pwm1 = io.PWM(self.in2_pin, self.PWM_FREQ)
      self.pwm2 = io.PWM(self.in4_pin, self.PWM_FREQ)

      self.pwm1.start(0)
      self.pwm2.start(0)

  def go(self, speed, angle):
    self.speed = speed
    self.turn_angle = angle

    braked_duty = self.MIN_DUTY + (100 - self.MIN_DUTY) * abs(speed) * self.performance
    directed_duty = 100 - braked_duty if speed >= 0 else braked_duty
    lower_duty = max(self.MIN_DUTY, min(100, braked_duty * (1 - abs(angle))))
    lower_directed_duty = 100 - lower_duty if speed >= 0 else lower_duty
    higher_duty = max(self.MIN_DUTY, min(100, braked_duty * (1 + abs(angle))))
    higher_directed_duty = 100 - higher_duty if speed >= 0 else higher_duty

    io.output(self.in1_pin, speed > 0)
    io.output(self.in3_pin, speed > 0)

    print(f'go motors go!    speed={speed}  angle={angle}\n'
          f'                    bd={braked_duty} dd={directed_duty} hdd={higher_directed_duty}  ldd={lower_directed_duty}')

    self.pwm1.ChangeDutyCycle(higher_directed_duty if angle >= 0 else lower_directed_duty)
    self.pwm2.ChangeDutyCycle(lower_directed_duty if angle >= 0 else higher_directed_duty)

  def stop(self):
    self.speed = 0.0
    io.output(self.in1_pin, 0)
    io.output(self.in3_pin, 0)
    self.pwm1.ChangeDutyCycle(0)
    self.pwm2.ChangeDutyCycle(0)

  def brake(self, on):
    self.performance = 0.5 if on else 1.0
    self.go(speed=self.speed, angle=self.turn_angle)

  def rotate(self, side):
    left = side == "left"
    io.output(self.in1_pin, not left)
    io.output(self.in3_pin, left)
    self.pwm1.ChangeDutyCycle(100 if left else 0)
    self.pwm2.ChangeDutyCycle(0 if left else 100)

  def deinit(self):
    self.stop()
    self.pwm1.stop()
    self.pwm2.stop()
    io.cleanup()
    print("Vehicle control deinitialized.")

