import pigpio


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

    self.pi = pigpio.pi()

    self.pi.set_mode(self.in1_pin, pigpio.OUTPUT)
    self.pi.set_mode(self.in3_pin, pigpio.OUTPUT)

  def dutify(self, pwm_id, dc):
    self.pi.hardware_PWM(self.in2_pin if pwm_id == 1 else self.in4_pin, self.PWM_FREQ, dc * 10000)

  def go(self, speed, angle):
    self.speed = speed
    self.turn_angle = angle

    braked_duty = self.MIN_DUTY + (100 - self.MIN_DUTY) * abs(speed) * self.performance
    directed_duty = 100 - braked_duty if speed >= 0 else braked_duty
    lower_duty = max(self.MIN_DUTY, min(100, braked_duty * (1 - abs(angle) * 1.5)))
    lower_directed_duty = 100 - lower_duty if speed >= 0 else lower_duty
    higher_duty = max(self.MIN_DUTY, min(100, braked_duty * (1 + abs(angle) * 1.5)))
    higher_directed_duty = 100 - higher_duty if speed >= 0 else higher_duty

    self.pi.write(self.in1_pin, speed > 0)
    self.pi.write(self.in3_pin, speed > 0)

    print(f'go motors go!    speed={speed}  angle={angle}\n'
          f'                    bd={braked_duty} dd={directed_duty} hdd={higher_directed_duty}  ldd={lower_directed_duty}')

    self.pwm1.ChangeDutyCycle(higher_directed_duty if angle >= 0 else lower_directed_duty)
    self.pwm2.ChangeDutyCycle(lower_directed_duty if angle >= 0 else higher_directed_duty)

  def stop(self):
    self.speed = 0.0
    self.pi.write(self.in1_pin, 0)
    self.pi.write(self.in3_pin, 0)
    self.dutify(1, 0)
    self.dutify(2, 0)

  def brake(self, on):
    self.performance = 0.5 if on else 1.0
    self.go(speed=self.speed, angle=self.turn_angle)

  def rotate(self, side):
    left = side == "left"
    self.pi.write(self.in1_pin, not left)
    self.pi.write(self.in3_pin, left)
    self.dutify(1, 100 if left else 0)
    self.dutify(2, 0 if left else 100)
