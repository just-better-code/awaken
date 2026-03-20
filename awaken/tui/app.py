import threading

from npyscreen import NPSAppManaged
from awaken.tui.main_form import MainForm
from threading import Event
from time import sleep
from awaken import Actor, Scheduler
from logging import Logger

class App(NPSAppManaged):
    def __init__(self, args: dict, log: Logger):
        self._args = args
        self._log = log
        self._user_activity = Event()
        self._system_activity = Event()
        self._actor = Actor(self._system_activity, self._user_activity)
        self._scheduler = Scheduler(
            self._system_activity,
            self._user_activity,
            self._args.get('idle'),
            self._args.get('delay'),
        )
        self._main = threading.Thread(target=self._perform, daemon=True)
        super().__init__()

    def onStart(self):
        self._args_form = self.addForm('MAIN', MainForm, data=self._args, name='Stay awake')
        self._main.start()

    def _perform(self) -> None:
        self._log.info('*** Lets work ***')
        while True:
            self._scheduler.ping()
            if self._scheduler.is_must_wake_up():
                self._actor.move_cursor(self._args.get('dist'))
                self._actor.press_key(self._args.get('key'))
            sleep(1)

    # def while_waiting(self) -> None:
    #     self._update_data_in_ui()
    #
    # def _update_data_in_ui(self):
    #     new_data = {}
    #     self._args_form.update_table(new_data)