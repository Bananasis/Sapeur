from game_modes import *


class Player:
    def __init__(self, player_id):
        self.id = player_id

    def get_view(self, cells):
        view = []
        for cell in cells:
            if cell.is_open(self.id):
                view.append(cell)
        return view


class Game:
    def __init__(self, w, h, player_ids):
        self.players = {x: Player(x) for x in player_ids}
        self.board = Board(w, h, self.players.keys())
        self.turn_order = list(self.players.keys())
        self.blowup = BlowUpStrategy(self.players)
        self.setup = SetUpStrategy(self.board)
        self.get_mine = MineCounterStrategy(self.players)
        self.get_reveal = RevealCounterStrategy(self.players)
        self.end = WinStrategy(self.players)
        self.player_lost = LooseStrategy(self.players)
        self.turn = 0

    def set_traps(self, trapper):
        trapper(self.board)
        return self

    def blow_strat(self, s):
        self.blowup = s
        return self

    def mine_coun_strat(self, s):
        self.get_mine = s
        return self

    def revl_coun_strat(self, s):
        self.get_reveal = s
        return self

    def inst_mine_strat(self, s):
        self.install_mine = s
        return self

    def win_strat(self, s):
        self.end = s
        return self

    def loos_strat(self, s):
        self.player_lost = s
        return self

    def get_players(self):
        return self.players

    def get_player(self, player_id):
        return self.players[player_id]

    def try_make_move(self, x, y, player_id):
        if 0 <= x < self.board.width and 0 <= y < self.board.height:
            if self.board.can_move(x, y) and player_id == self.turn_order[self.turn]:
                return self.make_move(x, y, player_id)

        return [], self.end(), self.turn

    def make_move(self, x, y, player_id):
        update_cells = []
        if not self.board.is_open(x, y, player_id):
            if self.board.is_boobytrapped(x, y):
                self.blowup(self, player_id)
                self.board.blowup(x, y, player_id)
                update_cells = [self.board.get(x, y)]
            else:
                if self.get_reveal(player_id):
                    update_cells = self.board.reveal(x, y, player_id)

        else:
            if self.get_mine(player_id):
                if self.setup(x, y):
                    update_cells = [self.board.get(x, y)] + self.board.get_neighbors(x, y)
        if update_cells:
            self.next_turn()
        return update_cells, self.end(), self.turn

    def next_turn(self):
        for i in range(len(self.turn_order)):
            self.turn = (self.turn + 1) % len(self.players)
            if not self.player_lost(self.turn_order[self.turn]):
                return True
        return False


class Board:
    def __init__(self, w, h, players):
        self.cell_list = []
        self.width = w
        self.height = h
        for i in range(w):
            self.cell_list.append([])
            for j in range(h):
                self.cell_list[i].append(Cell(i, j, players=players))

        for i in range(w - 1):
            for j in range(h - 1):
                self.cell_list[i][j].neighbors['RIGHT'] = self.cell_list[i + 1][j]
                self.cell_list[i][j].neighbors['UP'] = self.cell_list[i][j + 1]
                self.cell_list[i][j].neighbors['UP_RIGHT'] = self.cell_list[i + 1][j + 1]

                self.cell_list[i][j + 1].neighbors['DOWN'] = self.cell_list[i][j]
                self.cell_list[i + 1][j].neighbors['LEFT'] = self.cell_list[i][j]
                self.cell_list[i + 1][j + 1].neighbors['DOWN_LEFT'] = self.cell_list[i][j]

        for i in range(w - 1):
            for j in range(1, h):
                self.cell_list[i][j].neighbors['DOWN_RIGHT'] = self.cell_list[i + 1][j - 1]
                self.cell_list[i + 1][j - 1].neighbors['UP_LEFT'] = self.cell_list[i][j]

        for i in range(w - 1):
            self.cell_list[i][h - 1].neighbors['RIGHT'] = self.cell_list[i + 1][h - 1]
            self.cell_list[i + 1][h - 1].neighbors['LEFT'] = self.cell_list[i][h - 1]

        for j in range(h - 1):
            self.cell_list[w - 1][j].neighbors['UP'] = self.cell_list[w - 1][j + 1]
            self.cell_list[w - 1][j + 1].neighbors['DOWN'] = self.cell_list[w - 1][j]

    def add_mine(self, x, y):
        self.cell_list[x][y].add_mine()

    def is_boobytrapped(self, x, y):
        return self.cell_list[x][y].is_boobytrapped()

    def reveal(self, x, y, player_id):
        return self.cell_list[x][y].reveal(player_id)

    def can_move(self, x, y):
        return self.cell_list[x][y].can_move()

    def is_open(self, x, y, player_id):
        return self.cell_list[x][y].is_open(player_id)

    def get(self, x, y):
        return self.cell_list[x][y]

    def update(self, view):
        for cell in view:
            self.cell_list[cell.x][cell.y].update(cell)

    def get_neighbors(self, x, y):
        return list(self.cell_list[x][y].neighbors.values())

    def print(self, player_id=None):
        for lst in self.cell_list:
            print()
            for cell in lst:
                cell.print(player_id)

    def blowup(self, x, y, player_id):
        self.cell_list[x][y].blown_players[player_id] = True
        self.cell_list[x][y].open[player_id] = True


class Cell:
    def __init__(self, x, y, mines=0, mine_counter=0, players=()):
        self.x = x
        self.y = y
        self.blown_players = dict.fromkeys(players, False)
        self.open = dict.fromkeys(players, False)
        self.mine = mines
        self.neighbors = {}
        self.mine_counter = mine_counter

    def can_move(self):
        return not all(self.open.values())

    def add_mine(self):
        self.mine += 1
        for _, n in self.neighbors.items():
            n.increment_mine_counter()

    def increment_mine_counter(self):
        self.mine_counter += 1

    def is_boobytrapped(self):
        return self.mine != 0

    def is_open(self, player_id):
        return self.open[player_id]

    def update(self, cell):
        self.open = cell.open
        self.mine = cell.mine
        self.blown_players = cell.blown_players
        self.mine_counter = cell.mine_counter

    def reveal(self, player_id):
        opened_list = []
        if not self.open[player_id]:
            self.open[player_id] = True
            opened_list.append(self)
            if self.mine_counter == 0:
                for _, n in self.neighbors.items():
                    opened_list += n.reveal(player_id)
        return opened_list

    def print(self, player):
        char = self.mine_counter

        if self.mine > 0:
            char = "M"
        if player and not self.open[player.id]:
            char = "H"
        print(char, end=' ')
