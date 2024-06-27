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

    self.speed = 0.0
    self.turn_angle = 0.0
    self.brake = 1.0

  def go(self, speed, angle):
    self.speed = speed
    self.turn_angle = angle

    braked_spead = speed * self.brake
    directed_duty = 100 - braked_spead if speed >= 0 else braked_spead
    lower_speed = braked_spead * (1 - abs(angle))
    lower_directed_duty = 100 - lower_speed if speed >= 0 else lower_speed

    io.output(self.in1_pin, speed > 0)
    io.output(self.in3_pin, speed > 0)

    self.pwm1.ChangeDutyCycle(directed_duty if angle >= 0 else lower_directed_duty)
    self.pwm2.ChangeDutyCycle(lower_directed_duty if angle >= 0 else directed_duty)

  def stop(self):
    self.speed = 0.0
    io.output(self.in1_pin, 0)
    io.output(self.in3_pin, 0)
    self.pwm1.ChangeDutyCycle(0)
    self.pwm2.ChangeDutyCycle(0)

  def brake(self, on):
    self.brake = 0.5 if on else 1.0
    self.go(speed=self.speed, angle=self.turn_angle)

  def rotate(self, side):
    left = side == "l"
    io.output(self.in1_pin, not left)
    io.output(self.in3_pin, left)
    self.pwm1.ChangeDutyCycle(100 if left else 0)
    self.pwm2.ChangeDutyCycle(100 if left else 0)

  def deinit(self):
    self.stop()
    self.pwm1.stop()
    self.pwm2.stop()
    io.cleanup()
