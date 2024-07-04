import neopixel
import board

led = neopixel.NeoPixel(board.D18, 60)
led.fill((255, 0, 0))