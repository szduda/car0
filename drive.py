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

  def fwd(self, duty=100):
    io.output(self.in1_pin, 1)
    io.output(self.in3_pin, 1)
    self.pwm1.ChangeDutyCycle(100 - duty)
    self.pwm2.ChangeDutyCycle(100 - duty)

  def rev(self, duty=100):
    io.output(self.in1_pin, 0)
    io.output(self.in3_pin, 0)
    self.pwm1.ChangeDutyCycle(duty)
    self.pwm2.ChangeDutyCycle(duty)

  def stop(self):
    io.output(self.in1_pin, 0)
    io.output(self.in3_pin, 0)
    self.pwm1.ChangeDutyCycle(0)
    self.pwm2.ChangeDutyCycle(0)

  def turn(self, side, duty=100):
    left = side == "l"
    left_duty = duty if left else 100 - duty
    io.output(self.in1_pin, not left)
    io.output(self.in3_pin, left)
    self.pwm1.ChangeDutyCycle(left_duty)
    self.pwm2.ChangeDutyCycle(100 - left_duty)

  def deinit(self):
    self.stop()
    self.pwm1.stop()
    self.pwm2.stop()
    io.cleanup()
