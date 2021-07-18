from game_logic import Game
from game_logic import Board
from game_modes import *
from request import GameSerializer

game = Game(5, 5, trapper=SingleMineTrapper(5), player_number=2)
players = game.get_players()
serializer = GameSerializer(players)
turn = players[0]
player_boards = [Board(5, 5, players) for _ in players]
sts = SingleTrapStrategy(game)
game.inst_mine_strat(sts)
while True:
    input()
    update, end, turn = game.try_make_move(randrange(5), randrange(5), turn)
    views = [player.get_view(update) for player in players]

    for i in range(len(players)):
        player_boards[i].update(views[i])
        json_str = serializer.serialize_view(views[i])
        print(json_str)
        print(serializer.deserialize_view(json_str))
    game.board.print()
    print()
    for i in range(len(players)):
        player_boards[i].print(players[i])
        print()
