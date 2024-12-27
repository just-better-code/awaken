from npyscreen import NPSAppManaged
from awaken.tui.main_form import MainForm

class App(NPSAppManaged):
    def __init__(self, args : dict):
        self._args = args
        super().__init__()

    def onStart(self):
        self._args_form = self.addForm('MAIN', MainForm, data=self._args, name='Stay awake')

    def while_waiting(self) -> None:
        pass