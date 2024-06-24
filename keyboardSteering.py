from sshkeyboard import listen_keyboard
from threading import Thread

class KeyboardThread(Thread):

  def __init__(self, on_press, on_release) :
    super(KeyboardThread, self).__init__(name='keyboard-input-thread', daemon=True)
    self.on_press = on_press
    self.on_release = on_release
    self.start()

  def run(self):
    listen_keyboard(
      on_press=self.on_press,
      on_release=self.on_release,
    )
