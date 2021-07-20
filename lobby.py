import threading

from game_logic import Game, Board, Player
from game_modes import SingleTrapStrategy
lock = threading.Lock()

class Lobby:
    def __init__(self, lbid=0):
        self.game = None
        self.id = lbid
        self.players = {}
        self.max_players = 2
        self.wild = True
        self.ffa = True
        self.deadly_mines = True
        self.mine = 100
        self.width = 30
        self.height = 30
        self.started = False
        self.ended = False
        self.score_win = False

    def update(self, lobby):
        with lock:
            self.players = lobby.players
            self.max_players = lobby.max_players
            self.wild = lobby.wild
            self.ffa = lobby.ffa
            self.deadly_mines = lobby.deadly_mines
            self.mine = lobby.mine
            self.width = lobby.width
            self.height = lobby.height
            self.started = lobby.started
            self.ended = lobby.ended
            self.score_win = lobby.score_win

    def make_move(self, x, y, player):
        with lock:
            if self.game:
                update_cells, self.ended, _ = self.game.make_move(x, y, player.id)
                for i, player in self.game.players.items():
                    view = player.get_view(update_cells)
                    self.players[i].send_game_update(view)

    def start_game(self):
        with lock:
            if not self.game:
                self.game = Game(self.width, self.height, self.players.keys())
                self.game.set_traps(SingleTrapStrategy(self.mine))
                self.started = True
                for player in self.players.values():
                    player.start_game()
            return self.started

    def get_board(self):
        with lock:
            return Board(self.width, self.height, self.players.keys())

    def add_player(self, player_thread):
        with lock:
            if len(self.players) < self.max_players:
                self.players[player_thread.id] = player_thread
                return self
            return None

    def remove_player(self, player):
        with lock:
            return self.players.pop(player, None)
