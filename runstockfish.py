import chess
import chess.uci
import sys


def stockfishEvalFromPosition(position,time=5000):
    handler = chess.uci.InfoHandler()
    engine = chess.uci.popen_engine('stockfish_9_x64') #give correct address of your engine here
    engine.info_handlers.append(handler)

    board = chess.Board(position)
    #give your position to the engine:
    engine.position(board)
    info_handler = chess.uci.InfoHandler()
    engine.info_handlers.append(info_handler)
    #Set your evaluation time, in ms:
    evaltime = time #so 5 seconds
    evaluation = engine.go(movetime=evaltime)

    return info_handler.info["score"][1].cp