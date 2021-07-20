import json
from socket import socket

from serialization import *


class RequestManager:
    def __init__(self, socket):
        self.leftover = ""
        self.socket = socket
        self.deserialize = {}
        self.serialize = {}
        self.handle = {}

    def add_request(self, request, handler=lambda x: None):
        self.deserialize[request.code] = request.deserialize
        self.serialize[request.code] = request.serialize
        self.handle[request.code] = handler
        return self

    def get_request(self):
        bits = self.socket.recv(4096)
        self.leftover += bits.decode("utf-8")
        print(b"got: " + bits)
        b = 0
        br = 0
        for e in range(len(self.leftover)):
            if self.leftover[e] == '{':
                br += 1
            if self.leftover[e] == '}':
                br -= 1
            if br == 0:
                [(request, data_dict)] = json.loads(self.leftover[b: e + 1]).items()
                b = e + 1
                if request in self.deserialize:
                    data = self.deserialize[request](data_dict)
                    self.handle[request](data)
        self.leftover = self.leftover[b:]

    def make_request(self, data, request):
        if request in self.serialize:
            json_str = self.serialize[request](data)

            try:
                self.socket.sendall(bytes(json_str, 'utf-8'))
                print("sent: " + json_str)
            except socket.error as error:
                print(error)

    def manage(self, request, data):
        self.handle[request](data)
        pass


class Request:
    def __init__(self, serialize, deserialize, code):
        self.code = code
        self.serialize = lambda x: serialize(x, code)
        self.deserialize = deserialize


id_request = lambda x: Request(serialize_id, deserialize_id, x + "_id_request")
no_cariage_request = lambda x: Request(serialize_no_carriage, deserialize_no_carriage, x + "_nc_request")
pos_recuest = lambda x: Request(serialize_position, deserialize_position, x + "_pos_request")
lobby_list_request = lambda x: Request(serialize_lobby_update, deserialize_lobby_update, x + "_ll_request")
game_request = lambda x: Request(serialize_game_update, deserialize_game_update, x + "_game_request")
