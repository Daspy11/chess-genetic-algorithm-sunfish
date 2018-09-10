#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import re
import sys
import time
import test
import sunfish
import tools
import random
import json
import pickle
from runstockfish import stockfishEvalFromPosition

print("Loaded")

startingPositions = [ #Hand-selected openings that are frequently played at a high level, as well as a starting position with no moves made.
    #These are stored using the portable format FEN, which Sunfish fortunately includes a parser for.
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", #Starting position
    "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 4 4", #Four Knights Game 0
    "r1bqkb1r/1ppp1ppp/p1n2n2/4p3/B3P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 5", #Ruy Lopez: Columbus Variation 1
    "rnbqkbnr/pp2pppp/2p5/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3", #Queen's Gambit: Slav Defence 2
    "rnbqkbnr/ppp1pppp/8/8/2pP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3", #Queen's Gambit: Accepted 3
    "rnbqk2r/ppppppbp/5np1/8/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 2 4", #King's Indian Defence 4
    "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 2 4", #Nimzo-Indian Defence 5
    "rnbqkb1r/pppppppp/8/3nP3/8/8/PPPP1PPP/RNBQKBNR w KQkq - 1 3", #Alekhine Defence 6
    "rnbqk2r/ppppppbp/5np1/8/8/5NP1/PPPPPPBP/RNBQK2R w KQkq - 2 4", #King's Indian Attack: Symmetrical Defence 7
    "rnbqkb1r/ppp1pppp/5n2/3p4/5P2/5N2/PPPPP1PP/RNBQKB1R w KQkq - 0 3", #Bird Opening 8 
    "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", #Giuoco Piano 9
    "rnbqkbnr/pp2pppp/3p4/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3", #Sicilian Defence 10
    "r1bqk1nr/pppp1ppp/3b4/4n3/3PP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 1 6", #Three Knights Opening 11
    "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", #Italian Game: Two Knights Defense 12
    "r1bqkbnr/pppp1ppp/2n5/8/4P3/8/PPP2PPP/RNBQKBNR b KQkq - 2 4", #Center Game 13
    "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3", #Berlin Defence 14
    "rnbqkbnr/ppp1pppp/8/8/2pP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3", #etc
    "rnbqkb1r/ppp1pppp/3p4/3nP3/2BP4/8/PPP2PPP/RNBQK1NR b KQkq - 1 4",
    "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
    "rnbqkb1r/ppp1pp1p/1n1p2p1/4P3/2PP1P2/8/PP4PP/RNBQKBNR w KQkq - 0 6",
    "rn1qkb1r/ppp1pppp/1n1p4/4Pb2/2PP1P2/8/PP4PP/RNBQKBNR w KQkq - 1 6",
    "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
    "rnbqkbnr/pppp1ppp/4p3/8/3P2P1/8/PPP1PP1P/RNBQKBNR b KQkq - 0 2",
    "rnbqkbn1/ppppppr1/8/7p/8/5PP1/PPPPP2P/RNBQKBNR w KQq - 0 1",
    "rnbqkb1r/pppppppp/5n2/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 0 1",
    "rnbqkb1r/ppp1pppp/3p4/3nP3/3P4/5N2/PPP2PPP/RNBQKB1R b KQkq - 1 4",
    "rnbqkb1r/pp2pppp/2pp4/3nP3/3P4/5N2/PPP1BPPP/RNBQK2R b KQkq - 1 5",
    "r1bqkb1r/pp1npp1p/2p3p1/3n4/2PP4/5N2/PP2BPPP/RNBQK2R b KQkq - 0 8",
    "rnbqkb1r/ppp2ppp/4pn2/3p4/2P5/5NP1/PP1PPPBP/RNBQK2R b KQkq - 1 4",
    "rnbqk2r/ppp2ppp/4pn2/3p4/1bPP4/2N2N2/PP2PPPP/R1BQKB1R w KQkq - 2 5",
    "r2k3r/ppp1n1pp/2p1b3/2b1P1N1/8/2N5/PP3PPP/R1B2RK1 b - - 3 13",
    "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
    "r1bqkbnr/pp1ppppp/2n5/1Bp5/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
    "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/5N2/PP2PPPP/RNBQKB1R w KQkq - 0 4",
    "r1bqkbnr/pp1p1ppp/2n1p3/2p5/2B1P3/2N2N2/PPPP1PPP/R1BQK2R b KQkq - 1 4",
    "r1bqkbnr/pp1ppp1p/2n3p1/1Bp5/4P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 1 4",
    "rnbqkb1r/pp3ppp/2p1pn2/3p4/3P1B2/5N2/PPPNPPPP/R2QKB1R w KQkq - 0 5",
    "r1bqkbnr/pp1ppppp/2n5/1Bp5/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
    "r1bqkbnr/pp1p1ppp/2n1p3/2p5/2B1P3/2N2N2/PPPP1PPP/R1BQK2R b KQkq - 1 4",
    "rnbqk1nr/ppp1ppbp/3p2p1/8/3PP3/2N1B3/PPP2PPP/R2QKBNR b KQkq - 1 4",
    "r1bqkbnr/pp1p1ppp/2n1p3/2p5/2B1P3/2N2N2/PPPP1PPP/R1BQK2R b KQkq - 1 4",
    "r1bqkb1r/pp1pnpp1/2n1p2p/2p5/2B1P3/P1NP1N2/1PP2PPP/R1BQK2R b KQkq - 0 6",
    "r1bqk1nr/ppp3pp/2p2p2/2b1p3/4P3/5N2/PPPP1PPP/RNBQ1RK1 w kq - 0 6",
    "rnb1kbnr/pp1p1ppp/2p1p3/q7/3P1B2/5N2/PPP1PPPP/RN1QKB1R w KQkq - 2 4",
    "rnbqkbnr/ppp2ppp/4p3/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR b KQkq - 1 3",
    "rnbqkbnr/pp3ppp/3p4/2pPp3/2P1PP2/8/PP4PP/RNBQKBNR b KQkq - 0 5",
    "r1bqkbnr/pp1ppp1p/2n3p1/2p5/4P2P/5N2/PPPP1PP1/RNBQKB1R w KQkq - 1 4",
    "rnbqkb1r/ppp1pppp/1n1p4/4P3/2PP1P2/8/PP4PP/RNBQKBNR b KQkq - 0 5",
    "rnbqr1k1/pp3pbp/3p1np1/2pP4/4P3/2N5/PP1NBPPP/R1BQ1RK1 b - - 7 10",
    "r1bqk1nr/pp1pppbp/2n3p1/2p4P/2B1P3/5N2/PPPP1PP1/RNBQK2R b KQkq - 2 5",
    "rnbqr1k1/1p3pbp/p2p1np1/2pP4/4P3/2N5/PP1NBPPP/R1BQ1RK1 w - - 0 11",
    "r1bqr1k1/pp1n1pbp/3p1np1/2pP4/4P3/2N5/PP1NBPPP/R1BQ1RK1 w - - 8 11",
    "rnbqkb1r/pp1p1ppp/4pn2/2pP4/2P5/2N5/PP2PPPP/R1BQKBNR b KQkq - 1 4",
    "r1bqkb1r/pp1n1ppp/3p1n2/2pPp3/2P1P3/2NB4/PP2NPPP/R1BQK2R b KQkq - 3 7",
    "r2qkbnr/ppp2ppp/2np4/4p3/2B1PPb1/5N2/PPPP2PP/RNBQ1RK1 b kq - 3 5",
    "rnbqkbnr/1pp2pp1/p2pp2p/8/3PP3/2N1BN2/PPP2PPP/R2QKB1R b KQkq - 1 5",
    "r1bqkbnr/ppp2pp1/2np3p/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 0 5",
    "rnb2rk1/2p1qnbp/p3ppp1/1p6/2B1P3/P1N1BN2/1PP1QPPP/3RK2R w K - 0 12",
    "rnbqkb1r/pppp2pp/4ppn1/8/2B1P3/3P1Q1P/PPP2PP1/RNB1K1NR b KQkq - 0 5",
    "rnbqkbnr/pppp3p/4ppp1/7Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 4",
    "rnbq1bnr/pp1p1kpp/4pp2/2p5/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQ - 0 5",
    "rnbB1b2/pppp4/3kp1rn/8/3P4/8/PPP2PPP/RN2KBNR w KQ - 0 11",
    "r1bq1rk1/pp1p1nbp/n1p1ppp1/8/3PPP2/2N2N2/PPPBQ1PP/2KR1B1R w - - 2 10",
    "rnbqk2r/p2p1nbp/2p2pp1/1p2p3/4P1PP/1P3Q2/PBPPBP2/RN2K1NR w KQkq - 0 10",
    "rnbqk2r/ppppn1pp/4pp2/2b5/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 b kq - 4 5",
    "rnbqkbnr/pppp3p/4ppp1/7Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 4",
    "rn1qkbnr/1bpp2pp/p3pp2/1p6/4P3/2P3P1/PP1PBP1P/RNBQK1NR w KQkq - 2 6",
    "rn1qk1nr/pbp1ppbp/1p1p2p1/6BP/3P4/5N2/PPP1PPP1/RN1QKB1R w KQkq - 0 6",
    "rn1qk1nr/pbp1ppbp/1p1p2p1/6BP/3P4/4PN2/PPP2PP1/RN1QKB1R b KQkq - 0 6",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    "r1bqkbnr/pppp1ppp/2n5/8/4P3/8/PPP2PPP/RNBQKBNR b KQkq - 2 4",
    "rnbqkb1r/ppp1pppp/5n2/3p4/5P2/5N2/PPPPP1PP/RNBQKB1R w KQkq - 0 3",
    "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 2 4",
    "rnbqkbnr/ppp1pppp/8/8/2pP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3",
    "rnbqkb1r/ppp3pp/4pn2/3p1p2/2PP4/5NP1/PP2PPBP/RNBQK2R b KQkq - 1 5",
    "rnbqkb1r/pp1p2pp/2p1pn2/6B1/2PPp3/2N5/PP3PPP/R2QKBNR w KQkq - 0 6",
    "rnbqkbnr/pppp1pp1/4p3/8/7p/2PPP3/PP3PPP/RNBQKBNR w KQkq - 0 4",
    "r1bqkb1r/ppp2pp1/2n2n2/3pp1Bp/4P3/3P1N2/PPP1BPPP/RN1QK2R w KQkq - 0 6",
    "rnbqkb1r/pppp2pp/4pn2/5p2/2PP4/6P1/PP2PPBP/RNBQK1NR b KQkq - 1 4",
    "rnbqkb1r/ppppp2p/5np1/5p2/3PP3/2N5/PPP2PPP/R1BQKBNR b KQkq - 0 4",
    "rnbqkb1r/pp4pp/2p2n2/3p1pB1/3P4/2N1PN2/PP3PPP/R2QKB1R b KQkq - 0 7",
    "rnbqk2r/pp2b1pp/2p2n2/3p1pB1/3P4/2N1PN2/PP3PPP/R2QKB1R w KQkq - 1 8",
    "rnbqkb1r/ppp3pp/4pn2/3p1p2/2PP4/6P1/PP2PPBP/RNBQK1NR w KQkq - 0 5",
    "r1bqk1nr/pppp1ppp/2B5/2b1p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 0 4",
    "rnbqkb1r/pppp2pp/4pn2/5p2/3P4/3BPN2/PPP2PPP/RNBQK2R b KQkq - 3 4",
    "rnbqkb1r/ppppp2p/5np1/5p2/3P4/2N1P3/PPP2PPP/R1BQKBNR w KQkq - 0 4",
    "rn1qkbnr/1p3ppp/2p1p3/p2p1b2/PP1P4/B1N2N2/2P1PPPP/R2QKB1R w KQkq - 0 7",
    "rnb1kbnr/1p1ppppp/2p5/q7/8/2N5/P1PPPPPP/R1BQKBNR w KQkq - 0 4",
    "rn1qkb1r/pp2pppp/2p2n2/3p4/1P1P2b1/2N5/PBP1PPPP/R2QKBNR w KQkq - 1 5",
    "r1bqkbnr/1ppp1ppp/2n5/p7/P3p3/2R5/1PPPPPPP/1NBQKBNR w Kkq - 0 5",
    "r1bqkb1r/1ppp1ppp/2n2n2/p3p3/P7/1P4R1/2PPPPPP/1NBQKBNR w Kkq - 0 5",
    "r1bqk1nr/ppppbppp/2n1p3/8/P7/1P2P3/1BPP1PPP/RN1QKBNR b KQkq - 0 4",
    "rnbqkb1r/pppppp2/5n1p/6p1/3P4/3BPN2/PPP2PPP/RNBQK2R b KQkq - 3 4",
    "rnbqkbnr/pppppp1p/8/6p1/2PP4/8/PP2PPPP/RNBQKBNR b KQkq - 0 2",
    "r1bqkbnr/1pp1nppp/3p4/pP2p3/P7/B1P5/3PPPPP/RN1QKBNR w KQkq - 0 6",
    "rn1qkbnr/ppp2ppp/3pb3/4p3/8/3PBP2/PPP1P1PP/RN1QKBNR w KQkq - 1 4",
    "rnbqkbnr/ppp1pp1p/6p1/3p4/4N3/8/PPPPPPPP/R1BQKBNR w KQkq - 0 3",
    "rn1qkb1r/ppp1pppp/3p1n2/8/3P2b1/2N5/PPPBPPPP/R2QKBNR w KQkq - 3 4",
    "rnbqk1nr/ppp1ppbp/3p4/7R/3P4/2N5/PPP1PPP1/R1BQKBN1 b Qkq - 0 5",
    "rnbqk2r/ppppppbp/5np1/6B1/3P4/2N5/PPPQPPPP/R3KBNR b KQkq - 3 4",
    "rn1qkbnr/ppp2ppp/8/3p4/2P1p1b1/4PN2/PP1PBPPP/RNBQK2R w KQkq - 0 5",
    "r1bqkbnr/pp1p1ppp/2n5/2p1p3/2PP4/4PN2/PP3PPP/RNBQKB1R b KQkq - 0 4",
    "r1bqkbnr/pp2pppp/2n5/2Pp4/8/4PN2/PPP2PPP/RNBQKB1R b KQkq - 0 4",
    "rn1qkb1r/ppp1pppp/5n2/3pN3/3P2b1/2N5/PPP1PPPP/R1BQKB1R b KQkq - 4 4",
    "rnbqkbnr/ppp2ppp/4p3/8/3Pp3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4",
    "rnbqkbnr/ppp2pp1/3pp2p/8/3PP3/2N2N2/PPP2PPP/R1BQKB1R b KQkq - 1 4",
    "r1bqkbnr/ppp2pp1/2np3p/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 0 5",
    "r1bqkbnr/ppp2ppp/2np4/4p3/2B1PP2/5N2/PPPP2PP/RNBQK2R b KQkq - 1 4",
    "rnbqk2r/ppp1ppbp/3p1np1/8/2PPP3/2N5/PP3PPP/R1BQKBNR w KQkq - 0 5",
    "r1bqk2r/ppp1ppbp/2np1np1/8/3P1B1P/2N1P3/PPP1BPP1/R2QK1NR b KQkq - 1 6",
    "rnbqkb1r/pp1p1ppp/4pn2/2p5/3P1B2/2P1P3/PP3PPP/RN1QKBNR b KQkq - 0 4",
    "r1bqkb1r/2pp1ppp/p1n5/1p2p3/B2Pn3/5N2/PPP2PPP/RNBQ1RK1 w kq - 0 7",
    "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
]

startingPositonsEval = [58, 25, 45, 61, 48, 98, 32, 90, 45, 0, 25, 47, 57, 50, 32, 24, 48, -11, 50, 84, 86, -6, 61, 
148, 50, -15, -25, -28, 1, 46, -9, 47, -13, 41, 21, 0, 50, -13, 13, -10, 13, 20, 30, 96, -15, -26, 15, -56, -15, 30, 
65, 53, -69, -106, 47, -36, 57, -5, -16, 70, 173, 344, 237, 58, -38, 74, 69, 122, -28, 41, 7, 32, 0, 32, 48, -42, 90, 
66, 58, -37, 70, -53, 75, 81, 10, -4, 57, -71, -52, -35, -84, -122, -2, -24, -68, 44, -39, -40, 49, -45, 2, -9, -13, 
-17, -12, 81, -49, 57, 22, 85, 25, 11, 40, 47] #Positions evaluated with Stockfish at 5 second limit

class Helpers():

###################################### SUNFISH CODE ######################################
    def parseFEN(self,fen,pst):
        board, color, castling, enpas, _hclock, _fclock = fen.split()
        board = re.sub(r'\d', (lambda m: '.'*int(m.group(0))), board)
        board = list(21*' ' + '  '.join(board.split('/')) + 21*' ')
        board[9::10] = ['\n']*12
        #if color == 'w': board[::10] = ['\n']*12
        #if color == 'b': board[9::10] = ['\n']*12
        board = ''.join(board)
        wc = ('Q' in castling, 'K' in castling)
        bc = ('k' in castling, 'q' in castling)
        ep = sunfish.parse(enpas) if enpas != '-' else 0
        score = sum(pst[p][i] for i,p in enumerate(board) if p.isupper())
        score -= sum(pst[p.upper()][119-i] for i,p in enumerate(board) if p.islower())
        pos = sunfish.Position(board, score, wc, bc, ep, 0)
        return pos if color == 'w' else pos.rotate()

###################################### WRITTEN BY ME ######################################
    def pickRand(self,lst):
        selected = random.randrange(0, len(lst))
        return lst.pop(selected)

    def formPairs(self,lst):
        pairs = []
        while lst:
            rnd = self.pickRand(lst)
            rnd2 = self.pickRand(lst)
            pair = [rnd, rnd2]
            pairs.append(pair)
        return pairs    

    def evaluateStarts(self,starts):
        x=[]
        for i in range(0,len(starts)):
            print('working on line'+str(19+i))
            x.append(stockfishEvalFromPosition(starts[i],5000))
        return x

    def boardToFen(self,board,fen="",row=0): #We need to convert from Sunfish's internal board state to Forsyth-Edwards Notation, the official notation
        if row >= 8:
            d = fen[:-1]
            d += " w KQkq - 0 1" #This is solved using recursion
            return d
        currentrow = [board[8*row+i] for i in range(8)] #Get the row
        def compress(row,compressed="",depth=0,count=0):
            if depth >= 8: return compressed + (str(count) if count > 0 else "")

            if row[depth] == '.':
                return compress(row,compressed,depth+1,count+1)
            elif count > 0:
                return compress(row,compressed+str(count)+row[depth],depth+1,0)
            else:
                return compress(row,compressed+row[depth],depth+1,0)
            

        f = compress(currentrow)
        compressedrow = compress(currentrow) + "/"
        return self.boardToFen(board,fen+compressedrow,row+1)
        

    def removePadding(self,board):
        return board.replace("\n","").replace(" ","")

    def printPst(self,pst):
        for i in range(12):
            print(', '.join([str(pst[10*i+j]) for j in range(10)]))
class GeneticAlgorithm():

    ###################################### SUNFISH CODE ######################################
    def padSolution(self,solution):
        for k, table in solution.items():
            padrow = lambda row: (0,) + tuple(x+self.piece[k] for x in row) + (0,)
            solution[k] = sum((padrow(table[i*8:i*8+8]) for i in range(8)), ())
            solution[k] = (0,)*20 + solution[k] + (0,)*20
        return solution

    ###################################### WRITTEN BY ME ######################################
    def __init__(self,task,fromgeneration=1):
        self.generationcount = 1 #We track various statistics to check the program is working as intended
        self.gamesplayed = 1
        self.totalgames = 1
        self.whitewins = 0
        self.draws = 0
        self.blackwins = 0
        self.mutationrate = 3 #(%)
        self.piece = { 'P': 100, 'N': 280, 'B': 320, 'R': 479, 'Q': 929, 'K': 60000 }
        self.helper = Helpers()
        self.mutationrate = 0.03


        if task=="trainnew":
            print('Initialising Genetic Algorithm')
            print('Creating population of size 100')
            self.population = self.generateRandomGeneration(100)
            self.run()
        elif task=="train":
            fileobject = open("generation"+str(fromgeneration),"rb")
            self.population = pickle.load(fileobject)
            self.run()
        elif task=="view":
            fileobject = open("generation"+str(fromgeneration),"rb")
            self.population = pickle.load(fileobject)
            popsize = len(self.population)
            self.population
            for type in ['P','N','B','K','Q','R']:
                averages = [0 for p in range(100)]
                for solution in self.population:
                    for square in range(100):
                        averages[square] += solution[type][square] / popsize

                averages = [round(k) for k in averages]
                print(type + ': ')
                

    def selfPlay(self,pstwhite,pstblack):
        if pstwhite is None or pstblack is None: print("Null PST in Selfplay")
        startpos = startingPositions[random.randrange(0, len(startingPositions))]
        firstturn = startpos.split(' ')[1]
        startindex = 1 if firstturn == 'b' else 0
        startposindex = random.randrange(0, len(startingPositions))
        pos = self.helper.parseFEN(startingPositions[startposindex],pstwhite) #Select a random starting opening
        secs = 1
        for d in range(startindex,20):
            print("move: "+str(d))
            board = pos.board if d % 2 == 0 else pos.rotate().board
            pstCurrent = pstwhite if d % 2 == 0 else pstblack
            print("about to search")
            m, _ = sunfish.Searcher().search(pos, secs, pstCurrent) #Modified Sunfish searcher that takes in variable piece tables
            print("finished searching")
            if m is None: #If there are no valid moves
                return "W" if d % 2 == 0 else "B"
    
            pos = pos.move(m, pstCurrent) #Modify the board state with the selected move.
        
        fen = self.helper.boardToFen(self.helper.removePadding(pos.board))
        startingeval = startingPositonsEval[startposindex]
        return "W" if stockfishEvalFromPosition(fen) > startingeval else "B"
            

    def generateRandomSolution(self):
        nums = [[random.randint(0,1000) for i in range(64)]for j in range(6)] #384 random numbers total, 64 for each type of piece between 6 pieces
        solution = { #Sunfish uses tuple dicts for piece tables. Here, we format the solution.
            'P': tuple(nums[0]),
            'N': tuple(nums[1]),
            'B': tuple(nums[2]),
            'R': tuple(nums[3]),
            'Q': tuple(nums[4]),
            'K': tuple(nums[5]),
        }
        return self.padSolution(solution)


    def generateRandomGeneration(self,size=100):
        return [self.generateRandomSolution() for i in range(size)]

    def breedSolution(self,solution1,solution2):
        crossover = random.randint(1,63) #We select a random point in the sample to crossover. For example AAAAAA and BBBBBB could breed AABBBB and BBAAAA.
        newsolution1 = {
            'P': solution1[p][0:crossover] + solution2[p][crossover:64], #We use python list slicing to get elements before the crossover in solution 1, and after in solution 2
            'N': solution1[n][0:crossover] + solution2[n][crossover:64], #This can be done non-deterministically, however it is not economical for small dicts.
            'B': solution1[b][0:crossover] + solution2[b][crossover:64],
            'R': solution1[r][0:crossover] + solution2[r][crossover:64],
            'Q': solution1[q][0:crossover] + solution2[q][crossover:64],
            'K': solution1[k][0:crossover] + solution2[k][crossover:64]
        }
        newsolution2 = {
            'P': solution2[p][0:crossover] + solution1[p][crossover:64], 
            'N': solution2[n][0:crossover] + solution1[n][crossover:64],
            'B': solution2[b][0:crossover] + solution1[b][crossover:64],
            'R': solution2[r][0:crossover] + solution1[r][crossover:64],
            'Q': solution2[q][0:crossover] + solution1[q][crossover:64],
            'K': solution2[k][0:crossover] + solution1[k][crossover:64]
        }

        return [newsolution1,newsolution2]

    def mutateSolution(self,solution):
        for genome in solution:
            for dimension in genome:
                mrate = int(self.mutationrate * 100)
                dimension += random.randint(-mrate, mrate)

        return solution

    def run(self):

        while 1==1:
            #We output the current generation to the file

            pairs = self.helper.formPairs(self.population)
            for i in range(50):
                print('Playing game '+str(self.gamesplayed)+' in generation '+str(self.generationcount))
                print('W | B = '+str(self.whitewins)+' | '+str(self.blackwins))
                winner = self.selfPlay(pairs[i][0],pairs[i][1])
                print(winner+' Wins')
                self.gamesplayed += 1
                if winner == "W":
                    self.whitewins += 1
                    pairs[i].pop(1)
                else:
                    self.blackwins += 1
                    pairs[i].pop(0)

            winners = sum(pairs) #By this point, the pairs are length one, so we just join them into a single list
            winnerpairs = self.helper.formPairs(winners)
            newgeneration = [self.breedSolution(pair[0],pair[1]) for pair in winnerpairs]
            newgeneration = sum(newgeneration)
            newgeneration = [self.mutateSolution(m) for m in newgeneration]
            self.generationcount += 1

            

print('Train a new model (trainnew), open an existing model (train) or view generation averages (view)')
t = input()
k=0
if not t == "trainnew":
    print('What generation?')
    k = input()

p = GeneticAlgorithm(t,k)