import RPi.GPIO as io


class Drive:
  PWM_FREQ = 500

  def __init__(self, p1, p2, p3, p4):
    io.setmode(io.BCM)

    self.in1_pin = p1
    self.in2_pin = p2
    self.in3_pin = p3
    self.in4_pin = p4

    io.setup(self.in1_pin, io.OUT)
    io.setup(self.in2_pin, io.OUT)
    io.setup(self.in3_pin, io.OUT)
    io.setup(self.in4_pin, io.OUT)

    self.pwm1 = io.PWM(self.in2_pin, self.PWM_FREQ)
    self.pwm2 = io.PWM(self.in4_pin, self.PWM_FREQ)

    self.pwm1.start(0)
    self.pwm2.start(0)

    self.speed = 60
    self.direction = ''
    self.turn_angle = 1.0

  def set_speed(self, speed):
    self.speed = speed

  def fwd(self):
    self.direction = 'fwd'
    io.output(self.in1_pin, 1)
    io.output(self.in3_pin, 1)
    self.pwm1.ChangeDutyCycle(100 - self.speed)
    self.pwm2.ChangeDutyCycle(100 - self.speed)

  def rev(self, duty=60):
    self.direction = 'rev'
    io.output(self.in1_pin, 0)
    io.output(self.in3_pin, 0)
    self.pwm1.ChangeDutyCycle(self.speed)
    self.pwm2.ChangeDutyCycle(self.speed)

  def stop(self):
    self.direction = ''
    self.turn_angle = 1.0
    io.output(self.in1_pin, 0)
    io.output(self.in3_pin, 0)
    self.pwm1.ChangeDutyCycle(0)
    self.pwm2.ChangeDutyCycle(0)

  def turn(self, side, angle=1.0):
    self.turn_angle = angle
    left = side == "l"
    # left_duty = duty if left else 100 - duty
    io.output(self.in1_pin, not left)
    io.output(self.in3_pin, left)

    turn_duty = self.speed * (1 - angle)
    directed_turn_duty = turn_duty if self.direction is 'rev' else 100 - turn_duty

    if left:
      self.pwm1.ChangeDutyCycle(directed_turn_duty)
    else:
      self.pwm2.ChangeDutyCycle(directed_turn_duty)

  def deinit(self):
    self.stop()
    self.pwm1.stop()
    self.pwm2.stop()
    io.cleanup()
