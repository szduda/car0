from time import sleep
from DFRobot_INA219 import INA219

class BatteryMonitor:

    ina219_reading_mA = 1000
    ext_meter_reading_mA = 1000

    ACU_18650_COUNT = 2
    ACU_18650_mAH = 2600

    MIN_VOLT = 3.0 * ACU_18650_COUNT  # technically min V of an 18650 accumulator is ~2.7V, but the motor driver will cause a voltage drop when running
    MAX_VOLT = 4.2 * ACU_18650_COUNT
    MAX_mA = (1500.0 * 2) + 180 #  HR8833 motor driver limit is 1.5A per channel; RPI 0 2W draws ~180mA in this project

    def __init__(self, i2c_bus):
        self.ina = INA219(i2c_bus, INA219.INA219_I2C_ADDRESS4)

        while not self.ina.begin():
            sleep(2)

        self.ina.linear_cal(self.ina219_reading_mA, self.ext_meter_reading_mA)

    def get_voltage(self):
        voltage = self.ina.get_bus_voltage_V()
        voltage_percent = 100 * (voltage - self.MIN_VOLT) / (self.MAX_VOLT - self.MIN_VOLT)
        return voltage, voltage_percent

    def get_current(self):
        current = self.ina.get_current_mA()
        current_percent = 100 * current / self.MAX_mA
        return current, current_percent

    def get_time_until_discharge(self, voltage_percent, current):
        h, m_precent = divmod(self.ACU_18650_mAH * voltage_percent / current, 1)
        m = round(m_precent * 60)
        return round(h / 100), m
