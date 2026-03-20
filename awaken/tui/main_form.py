from npyscreen import FormBaseNew, SimpleGrid

class MainForm(FormBaseNew):
    def __init__(self, data: dict, *args, **kwargs):
        self._data = data
        super().__init__(*args, **kwargs)

    def create(self):
        self._table = self.add(SimpleGrid, relx=1, rely=2, values=[
            ['idle', self._data.get('idle')],
            ['delay', self._data.get('delay')],
            ['key', self._data.get('key')],
            ['dist', self._data.get('dist')],
            ['speed', self._data.get('speed')],
            ['random', self._data.get('random')],
        ])

    def update_table(self, data):
        self._table.values = data
        self._table.update()
