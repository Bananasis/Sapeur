import socket
from threading import Thread
from request import *
from game_window import SapeurApp


class Client(Thread):
    def __init__(self, ip="192.168.1.101", port=9999):
        super().__init__()
        self.board = None
        self.game_window = None
        self.lobby_dict = {}
        self.lobby_id = -1
        self.server_id = -1

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.request_manager = RequestManager(self.socket)
        self.request_manager.add_request(id_request("server"), self.set_server_id)
        self.request_manager.add_request(id_request("lobby"), self.set_lobby_id)
        self.request_manager.add_request(lobby_list_request("update"), self.set_lobbys)
        self.request_manager.add_request(no_cariage_request("start_game"), lambda _: self.start_game())
        self.request_manager.add_request(game_request("update"), self.update_board)

        self.request_manager.add_request(pos_recuest("move"))
        self.request_manager.add_request(id_request("connect_lobby"))
        self.request_manager.add_request(no_cariage_request("create_lobby"))
        self.request_manager.add_request(no_cariage_request("leave_lobby"))

    def run(self):
        while True:
            self.request_manager.get_request()

    def start_game(self):
        if self.lobby_id in self.lobby_dict:
            self.board = self.lobby_dict[self.lobby_id].get_board()

    def set_server_id(self, pid):
        self.server_id = pid

    def make_move(self, pos):
        self.request_manager.make_request(pos, "move_pos_request")

    def set_lobby_id(self, lid):
        self.lobby_id = lid

    def set_lobbys(self, lobby_dict):
        self.lobby_dict = lobby_dict

    def update_board(self, view):
        if self.board:
            self.board.update(view)
            self.game_window.update_board()


c = Client()
c.start()
c.request_manager.make_request(None, "create_lobby_nc_request")
c.request_manager.make_request(None, "start_game_nc_request")
SapeurApp(c).run()
