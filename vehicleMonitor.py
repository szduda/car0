from time import sleep
from DFRobot_INA219 import INA219


class BatteryMonitor:

    ina219_reading_mA = 1000
    ext_meter_reading_mA = 1000

    ACU_18650_COUNT = 2
    ACU_18650_mAH = 2600

    MIN_VOLT = 3.0 * ACU_18650_COUNT  # technically min V of an 18650 accumulator is ~2.7V, but the motor driver will cause a voltage drop when running
    MAX_VOLT = 4.2 * ACU_18650_COUNT
    MAX_mA = (1500.0 * 2) + 180       # HR8833 motor driver limit is 1.5A per channel; RPI 0 2W draws ~180mA in this project

    avg_window = 5
    hourses = [0]*avg_window
    minuteses = [0]*avg_window
    prev_time_index = avg_window - 1

    def __init__(self, i2c_bus):
        self.ina = INA219(i2c_bus, INA219.INA219_I2C_ADDRESS4)

        while not self.ina.begin():
            sleep(2)

        self.ina.linear_cal(self.ina219_reading_mA, self.ext_meter_reading_mA)

    def get_voltage(self):
        voltage = self.ina.get_bus_voltage_V()
        voltage_percent = 100 * (voltage - self.MIN_VOLT) / (self.MAX_VOLT - self.MIN_VOLT)
        return round(voltage, 3), round(voltage_percent)

    def get_current(self):
        current = self.ina.get_current_mA()
        current_percent = 100 * current / self.MAX_mA
        return round(current), round(current_percent)

    def get_time_until_discharge(self, voltage_percent, current):
        hx100, m_precent = divmod(self.ACU_18650_mAH * voltage_percent / current, 1)
        h = hx100 / 100.0
        m = m_precent * 60

        i = self.prev_time_index % self.avg_window
        self.prev_time_index = i
        self.hourses.insert(i, h)
        self.minuteses.insert(i, m)

        def is_positive(num): return num > 0
        hs = list(filter(is_positive, self.hourses))
        ms = list(filter(is_positive, self.minuteses))

        avg_h = sum(hs) / len(hs)
        avg_m = sum(ms) / len(ms)

        return round(avg_h), round(avg_m / 10) * 10
