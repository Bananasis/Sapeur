import json
from game_logic import Cell
from lobby import Lobby


def serialize_no_carriage(_, code):
    data = json.dumps({code: ""})
    return data


def deserialize_no_carriage(_):
    return None


def serialize_position(pos, code):
    data = json.dumps({code: {"x": pos[0], "y": pos[1]}})
    return data


def deserialize_position(data):
    return (int(data["x"]), int(data["y"]))


def deserialize_id(player_id):
    return int(player_id)


def serialize_id(player_id, code):
    data = json.dumps({code: str(player_id)})
    return data


def deserialize_player_id(player_id):
    return int(player_id)


def serialize_lobby_update(lobby_dict, code):
    lobby_dict_dict = {}
    for i, lobby in lobby_dict.items():
        lobby_dict_dict[i] = {"players": {i: "" for i in lobby.players.keys()}, "max_players": lobby.max_players,
                              "wild": lobby.wild,
                              "ffa": lobby.ffa,
                              "deadly_mines": lobby.deadly_mines, "mine": lobby.mine, "width": lobby.width,
                              "height": lobby.height,
                              "started": lobby.started, "ended": lobby.ended, "score_win": lobby.score_win}
    data = json.dumps({code: lobby_dict_dict})
    return data


def deserialize_lobby_update(lobby_dict_dict):
    lobbys = {}
    for i, lobby_dict in lobby_dict_dict.items():
        lobby = Lobby(int(i))
        lobby.players = {}

        for server_id in lobby_dict["players"].keys():
            lobby.players[int(server_id)] = None
        lobby.max_players = int(lobby_dict["max_players"])
        lobby.wild = bool(lobby_dict["wild"])
        lobby.ffa = bool(lobby_dict["ffa"])
        lobby.deadly_mines = bool(lobby_dict["deadly_mines"])
        lobby.mine = int(lobby_dict["mine"])
        lobby.width = int(lobby_dict["width"])
        lobby.height = int(lobby_dict["height"])
        lobby.started = bool(lobby_dict["started"])
        lobby.ended = bool(lobby_dict["ended"])
        lobby.score_win = bool(lobby_dict["score_win"])
        lobbys[int(i)] = lobby
    return lobbys


def serialize_game_update(view, code):
    dict_view = []
    for cell in view:
        player_open = {}
        for p, o in cell.open.items():
            player_open[p] = o
        dict_view.append({'pb': cell.blown_players,
                          'x': cell.x,
                          'y': cell.y,
                          'm': cell.mine,
                          'mc': cell.mine_counter,
                          'pr': player_open})
    view_dict = {code: dict_view}
    data = json.dumps(view_dict)
    return data


def deserialize_game_update(view_dict):
    view = []
    for cell_dict in view_dict:
        view.append(Cell(int(cell_dict['x']),
                         int(cell_dict['y']),
                         int(cell_dict['m']),
                         int(cell_dict['mc']),
                         ))

        for pid, r in cell_dict['pr'].items():
            view[-1].open[int(pid)] = bool(r)
        for pid, r in cell_dict['pb'].items():
            view[-1].blown_players[int(pid)] = bool(r)

    return view
