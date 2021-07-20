import kivy
from kivy import Config
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Rectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatter import ScatterPlane
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

from client import Client

Config.set('graphics', 'resizable', True)
from kivy.uix.image import Image


class GameScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.sg = SapeurGame()
        self.add_widget(self.sg)
        self.game = None

    def start_game(self, game):
        self.game = game
        Clock.schedule_once(lambda _: self.sg.start_game(game))

    def update_board(self):
        Clock.schedule_once(lambda _: self.sg.gb.update_board())


class SapeurGame(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gb = GameBoard()
        self.add_widget(self.gb)
        self.game = None

    def start_game(self, game):
        self.game = game
        self.gb.start_game(game.board)

    pass


class GameBoard(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cells = {}
        self.board = None

    def start_game(self, board):
        self.board = board
        self.cols = board.width
        self.rows = board.height
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


class BackGround(ScatterPlane):
    def __init__(self, **kw):
        super().__init__(**kw)
        texture = Image(source="resources/revealed-bomb.png").texture
        texture.wrap = 'repeat'
        texture.uvsize = (50, 50)
        with self.canvas:
            Rectangle(size=(2048, 2048), texture=texture)


class MenuScreen(Screen):
    pass


class LobbyScreen(Screen):
    pass


class LobbyListScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class LobbyButton(Button):
    pass


class SapeurApp(App):

    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.lobby_buttons = {}
        self.client = client
        client.game_window = self
        client.start()
        self.lobby = None
        self.ll = None
        self.sm = None
        self.gs = None

    def sceldue_ll_update(self):
        Clock.schedule_once(lambda _: self.ll_update())

    def ll_update(self):
        #for li, lb in self.lobby_buttons.items():
           # if li not in self.client.lobby_dict.keys():
            #   self.ll.ids['container'].remove_widget(lb)
             #   self.lobby_buttons.pop(li)
        for li, l in self.client.lobby_dict.items():
            if li not in self.lobby_buttons.keys():
                mb = LobbyButton()
                mb.srcs="resources/revealed-bomb.png"
                mb.on_press = lambda: self.client.join_lobby(li)
                self.lobby_buttons[li] = mb
                self.ll.ids['container'].add_widget(mb)



    def sceldue_start_game(self, board):
        Clock.schedule_once(lambda _: self.start_game(board))

    def start_game(self, board):
        self.gs.start_game(board)
        self.sm.current = 'game'

    def join_lobby(self):
        Clock.schedule_once(lambda _: self.set_current("lobby"))

    def set_current(self, new_cur):
        self.sm.current = new_cur

    def build(self):
        # Create the screen manager
        self.lobby = LobbyScreen(name='lobby')
        self.gs = GameScreen(name='game')
        self.ll = LobbyListScreen(name='lobby_list')
        self.sm = ScreenManager(transition=SlideTransition(direction="right"))
        self.sm.add_widget(MenuScreen(name='menu'))

        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(self.ll)
        self.sm.add_widget(self.lobby)
        self.sm.add_widget(self.gs)
        return self.sm


if __name__ == '__main__':
    SapeurApp(Client()).run()
