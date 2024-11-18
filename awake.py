import pyautogui
import time
import sys
import datetime
import random
from iddle_time import IdleMonitor

# CONFIGURATION #
use_mouse_click = False
use_scroll = True
use_cursor_move = True
use_key_press = True

delay_min = 60
delay_delta = 10
mouse_move_count = 5
mouse_move_min = 50
mouse_move_delta = 50
scroll_min = 20
scroll_delta = 20

pyautogui.FAILSAFE = False
monitor = IdleMonitor.get_monitor()
work_sec = sleep_sec = 0


class Actor:

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


while True:
    delay = int(delay_min + random.random() * delay_delta)
    while monitor.get_idle_time() < delay:
        time.sleep(1)
        work_sec += 1

    if work_sec > delay:
        work_time = str(datetime.timedelta(seconds=(work_sec - delay)))
        sleep_time = str(datetime.timedelta(seconds=sleep_sec))
        sleep_sec = 0
        print("S:" + sleep_time)
        print("W:" + work_time)
        sys.stdout.flush()

    sleep_sec += monitor.get_idle_time()
    work_sec = 0
    if use_cursor_move:
        Actor.cursor()
    if use_key_press:
        Actor.key()
    if use_scroll:
        Actor.scroll()
    if use_mouse_click:
        Actor.mouse_btn()
