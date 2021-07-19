from kivy import Config
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen

Config.set('graphics', 'resizable', True)
from kivy.uix.image import Image


class TestApp(App):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.sg = SapeurGame(game)

    def build(self):
        self.sg = SapeurGame(self.game)
        return self.sg


class SapeurGame(FloatLayout):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.board = GameBoard(game.board)
        game.game_window = self.board
        self.add_widget(self.board)


class GameBoard(GridLayout):
    def __init__(self, board, **kwargs):
        super().__init__(**kwargs)
        self.board = board
        self.cols = board.width
        self.rows = board.height
        self.cells = {}
        for i in range(board.width):
            for j in range(board.height):
                cell = Cell(board.cell_list[i][j], source='resources/empty-block.png')
                cell.bind(on_press=make_move)
                cell.coords = (i, j)
                self.cells[(i, j)] = cell
                self.add_widget(cell)

    def update_board(self):
        for cell in self.cells.values():
            cell.update_status()
        pass


class Cell(ButtonBehavior, Image):
    def __init__(self, cell, **kwargs):
        super().__init__(**kwargs)
        self.new_source = 'resources/empty-block.png'
        self.cell = cell
        Clock.schedule_interval(lambda _: self.update_src(), 0.05)

    def update_src(self):
        self.source = self.new_source

    def update_status(self):
        texture = 'resources/empty-block.png'
        if self.cell.is_open(self.parent.parent.game.server_id):
            if self.cell.is_boobytrapped():
                if self.cell.blown_players[self.parent.parent.game.server_id]:
                    texture = 'resources/bomb-at-clicked-block.png'
                else:
                    texture = 'resources/revealed-bomb.png'
            else:
                if not self.cell.can_move():
                    texture = 'resources/' + str(self.cell.mine_counter) + '.png'
                else:
                    texture = 'resources/u' + str(self.cell.mine_counter) + '.png'
        self.new_source = texture


def make_move(instance):
    instance.parent.parent.game.make_move((instance.cell.x, instance.cell.y))


class MenuScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class SapeurApp(App):

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(SettingsScreen(name='settings'))

        return sm


if __name__ == '__main__':
    SapeurApp().run()
