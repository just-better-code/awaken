import pyautogui
import time
import sys
import datetime
import random
from iddle_time import IdleMonitor
from stay_awake.dto.CursorPosition import Cursor


class Actor:
    def __init__(self):
        pass

    def moveCursorTo(self, position: Cursor):

    @classmethod
    def cursor(self):
        init_x, init_y = pyautogui.position()
        for x in range(mouse_move_count - 1):
            sign_x = random.choice([-1, 1])
            sign_y = random.choice([-1, 1])
            mouse_move_x = mouse_move_min * (1 + random.random()) * sign_x
            mouse_move_y = mouse_move_min * (1 + random.random()) * sign_y
            pyautogui.moveRel(mouse_move_x, mouse_move_y, random.uniform(0.1, 0.5))

        pyautogui.moveTo(init_x, init_y, random.uniform(0.1, 0.5))

    @classmethod
    def scroll(self):
        scroll = int(scroll_min + random.random() * scroll_delta)
        for s in range(scroll):
            pyautogui.scroll(1, _pause=False)
        scroll = int(scroll_min + random.random() * scroll_delta)
        for s in range(scroll):
            pyautogui.scroll(-1, _pause=False)

    @classmethod
    def key(self):
        pyautogui.press("shift")

    @classmethod
    def mouse_btn(self):
        pyautogui.leftClick()
        pyautogui.rightClick()
        time.sleep(1)
        pyautogui.press("esc")