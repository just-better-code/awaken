import pyautogui


class Cursor:
    def __init__(self):
        self.init_x, self.init_y = pyautogui.position()


    def move_x(self, x: int):
        self.x += x

    def move_y(self, y: int):
        self.y += y


