from random import randrange


class Trapper:
    def __init__(self, bomb_count):
        self.bomb_cont = bomb_count

    def __call__(self, board):
        for _ in range(self.bomb_cont):
            x, y = randrange(board.width), randrange(board.height)
            board.add_mine(x, y)


class SingleMineTrapper(Trapper):
    def __call__(self, board):
        for _ in range(self.bomb_cont):
            x, y = randrange(board.width), randrange(board.height)
            if not board.is_boobytrapped(x, y):
                board.add_mine(x, y)


class BlowUpStrategy:
    def __init__(self, players):
        self.players_blow_counter = dict.fromkeys(players, 0)
        pass

    def __call__(self, game, player):
        self.players_blow_counter[player] += 1
        pass


class MineCounterStrategy:
    def __init__(self, players):
        self.mines_left = dict.fromkeys(players, 1)
        pass

    def __call__(self, player):
        return self.mines_left[player]
        pass


class RevealCounterStrategy:
    def __init__(self, players):
        self.reveals_left = dict.fromkeys(players, 1)
        pass

    def __call__(self, player):
        return self.reveals_left[player]
        pass


class SetTrapStrategy:
    def __init__(self, mines):
        self.mines = mines
        pass

    def __call__(self, board):
        for _ in range(self.mines):
            x = randrange(0, board.width - 1)
            y = randrange(0, board.height - 1)
            board.add_mine(x, y)
        pass


class SingleTrapStrategy(SetTrapStrategy):
    def __call__(self, board):
        for _ in range(self.mines):
            x = randrange(0, board.width - 1)
            y = randrange(0, board.height - 1)
            if not board.is_boobytrapped(x, y):
                board.add_mine(x, y)


class LooseStrategy:
    def __init__(self, players):
        self.player_lost = dict.fromkeys(players, False)
        pass

    def __call__(self, player):
        return self.player_lost[player]
        pass


class WinStrategy:
    def __init__(self, players):
        self.player_score = dict.fromkeys(players, 0)
        self.winner = None
        pass

    def __call__(self):
        return self.winner
        pass
