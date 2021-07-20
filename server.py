import socket
import threading
from threading import Thread

from lobby import Lobby
from request import RequestManager, id_request, lobby_list_request, no_cariage_request, game_request, pos_recuest

lock = threading.Lock()


class Server(Thread):
    def __init__(self, bind_ip='0.0.0.0', bind_port=9999):
        Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((bind_ip, bind_port))
        except socket.error as e:
            str(e)

        self.socket.listen(4)

        print('Listening on {}:{}'.format(bind_ip, bind_port))
        self.player_id = 0
        self.lobby_id = 0
        self.player_threads = {}
        self.lobby = {}

    def run(self):
        while True:
            try:
                client_sock, address = self.socket.accept()
                print('Accepted connection from {}:{}'.format(address[0], address[1]))
                pl_thread = PlayerHandlingThread(client_sock, self.player_id, self)
                self.player_threads[self.player_id] = pl_thread
                pl_thread.start()
                self.player_id += 1
            except Exception as error:
                print(error)

    def create_lobby(self, player):
        with lock:
            self.lobby_id += 1
            lobby = Lobby(self.lobby_id)
            self.lobby[self.lobby_id] = lobby
            return self.lobby[self.lobby_id].add_player(player)

    def add_player_to_lobby(self, player, lobby_id):
        with lock:
            return self.lobby[lobby_id].add_player(player)

    def send_lobby_list(self):
        with lock:
            for pt in self.player_threads.values():
                pt.send_lobby_list()

    def disconnect(self, player_thread):
        self.player_threads.pop(player_thread.id)


class PlayerHandlingThread(Thread):
    def __init__(self, client_socket, player_id, server):
        Thread.__init__(self)
        self.server = server
        self.socket = client_socket
        self.id = player_id
        self.lobby = None
        self.request_manager = RequestManager(client_socket)

        self.request_manager.add_request(id_request("server"))
        self.request_manager.add_request(id_request("lobby"))
        self.request_manager.add_request(lobby_list_request("update"))
        self.request_manager.add_request(no_cariage_request("start_game"), lambda _: self.try_start_game())
        self.request_manager.add_request(game_request("update"))

        self.request_manager.add_request(pos_recuest("move"), lambda x: self.make_move(x[0], x[1]))
        self.request_manager.add_request(id_request("connect_lobby"), self.join_lobby)
        self.request_manager.add_request(no_cariage_request("create_lobby"), lambda _: self.create_lobby())
        self.request_manager.add_request(no_cariage_request("leave_lobby"), lambda _: self.leave_lobby())

    def run(self):
        self.request_manager.make_request(self.id, "server_id_request")
        self.send_lobby_list()
        while True:
            try:
                self.request_manager.get_request()
            except socket.error as error:
                print(error)
                self.server.disconnect(self)
                break

    def create_lobby(self):
        self.lobby = self.server.create_lobby(self)
        self.server.send_lobby_list()
        self.request_manager.make_request(self.lobby.id, "lobby_id_request")

    def make_move(self, x, y):
        if self.lobby:
            self.lobby.make_move(x, y, self)

    def join_lobby(self, lobby_id):
        self.lobby = self.server.add_player_to_lobby(self, lobby_id)
        if self.lobby:
            self.server.send_lobby_list()
            self.request_manager.make_request(self.lobby.id, "lobby_id_request")

    def leave_lobby(self):
        self.lobby = self.lobby.remove_player(self)

    def send_lobby_list(self):
        self.request_manager.make_request(self.server.lobby, "update_ll_request")

    def send_game_update(self, view):
        self.request_manager.make_request(view, "update_game_request")

    def update_lobby(self, lobby):
        self.server.lobby.update(lobby)

    def try_start_game(self):
        if self.lobby:
            self.lobby.start_game()

    def start_game(self):
        self.request_manager.make_request(None, "start_game_nc_request")


s = Server()
s.start()
