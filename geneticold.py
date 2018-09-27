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

print("Loaded")

startingPositions = [ #15 hand-selected openings that are frequently played at a high level, as well as a starting position with no moves made.
    tools.FEN_INITIAL, #These are stored using the portable format FEN, which Sunfish fortunately includes a parser for.
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
    "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3" #Berlin Defence 14
]

class GeneticAlgorithm(): #Use composition?

    ###################################### NOT WRITTEN BY ME ######################################
    def padSolution(self,solution): #Sunfish puts a ring of zeros on the outside of the board to detect whether a given move is valid.
        for k, table in solution.items(): #This function also pads the piece table so that it matches up.
            padrow = lambda row: (0,) + tuple(x+self.piece[k] for x in row) + (0,)
            solution[k] = sum((padrow(table[i*8:i*8+8]) for i in range(8)), ())
            solution[k] = (0,)*20 + solution[k] + (0,)*20
        return solution

    ###################################### WRITTEN BY ME ######################################
    def __init__(self): #Constructor that is run when the class is initialized
        self.generationcount = 1
        self.gamesplayed = 1
        self.totalgames = 1
        self.whitewins = 0
        self.draws = 0
        self.blackwins = 0
        self.mutationrate = 3 #(%)
        self.piece = { 'P': 100, 'N': 280, 'B': 320, 'R': 479, 'Q': 929, 'K': 60000 }


    def selfPlay(self,pstWhite,pstBlack): 
        #This function takes in two piece tables and plays a match between them. It returns "W", "D", or "B"
        #for a white win, draw, or black win. The range of the loop bounds the number of moves played.
        if pstWhite is None or pstBlack is None: print("Null PST in Selfplay")
        pos = tools.parseFEN(startingPositions[random.randint(0,14)],pstWhite) #Select a random starting opening from the list
        secs = random.randint(100,300) / 1000 #Random computation time from 10 to 100ms (0.01 to 0.1 seconds). This is to minimize total game repetition. 
        game = []
        for d in range(0,200):
            time.sleep(.001)
            print('#', end="") #Console output to monitor progress
            board = pos.board if d % 2 == 0 else pos.rotate().board
            pstCurrent = pstWhite if d % 2 == 0 else pstBlack
            m, _ = sunfish.Searcher().search(pos, secs, pstCurrent) #Modified Sunfish searcher that takes in variable piece tables
            if m is None: #If there are no valid moves
                return "W" if d % 2 == 0 else "B" #If there are no valid moves that means one side has been checkmated. The side that can't move loses
            #print("\nmove", tools.mrender(pos, m))
            pos = pos.move(m, pstCurrent) #Modify the board state with the selected move.
            if game.count(pos) >= 3: #Check for three move repetition
                return "D" #Match is a draw if the current position has appeared at least twice before
            game.append(pos)
        
        return "D" #Declare the game a draw if it doesn't end in 200 moves.

    def generateRandomSolution(self):
        nums = [[random.randint(-100,100) for i in range(64)]for j in range(6)] #384 random numbers total, 64 for each type of piece between 6 pieces
        solution = { #Sunfish uses tuple dicts for piece tables. Here, we format the solution.
            'P': tuple(nums[0]),
            'N': tuple(nums[1]),
            'B': tuple(nums[2]),
            'R': tuple(nums[3]),
            'Q': tuple(nums[4]),
            'K': tuple(nums[5])
        }

        return self.padSolution(solution) #We need to pad the solution


    def generateRandomGeneration(self,size=100): #We use a list comprehension to generate a list of random solutions
        return [self.generateRandomSolution() for i in range(size)]

    def breedSolution(self,solution1,solution2):
        crossover = random.randint(1,63) #We select a random point in the sample to crossover. For example AAAAAA and BBBBBB could breed AABBBB and BBAAAA.
        newsolution1 = {
            'P': solution1[p][0:crossover] + solution2[p][crossover:64], #We use python list slicing to get elements before the crossover in solution 1, and after in solution 2
            'N': solution1[n][0:crossover] + solution2[n][crossover:64], #This can be done non-deterministically, however it is not economical for small dicts.
            'B': solution1[b][0:crossover] + solution2[b][crossover:64], #The format [num1:num2] returns the part of the list bounded by
            'R': solution1[r][0:crossover] + solution2[r][crossover:64], #The two numbers.
            'Q': solution1[q][0:crossover] + solution2[q][crossover:64],
            'K': solution1[k][0:crossover] + solution2[k][crossover:64]
        }
        newsolution2 = {
            'P': solution2[p][0:crossover] + solution1[p][crossover:64], #We create two solutions as there are two parents to replace
            'N': solution2[n][0:crossover] + solution1[n][crossover:64],
            'B': solution2[b][0:crossover] + solution1[b][crossover:64],
            'R': solution2[r][0:crossover] + solution1[r][crossover:64],
            'Q': solution2[q][0:crossover] + solution1[q][crossover:64],
            'K': solution2[k][0:crossover] + solution1[k][crossover:64]
        }

        return [newsolution1,newsolution2]
    
    def pickRand(self,lst): #Pick a random item from a list
        selected = random.randrange(0, len(lst))
        return lst.pop(selected)

    def formPairs(self,lst): #Turns a list into a list of lists with length two
        pairs = []
        while lst:
            rand1 = self.pickRand(lst)
            rand2 = self.pickRand(lst)
            pair = rand1, rand2
            pairs.append(pair)
        return pairs

    def run(self): #Main loop
        print('Initialising Genetic Algorithm')
        print('Creating population of size 100')
        print('[#',end="")
        self.population = [self.generateRandomSolution]
        for i in range(99):
            self.population.append(self.generateRandomSolution())
            print('#',end=""),
        print(']\n')

        while 1==1:
            pairs = self.formPairs(self.population)
            for i in range(50): #50 games for 50 generations. Crossover is not implemented at this point.
                print('Playing game '+str(self.gamesplayed)+' in generation '+str(self.generationcount))
                print('W | D | B = '+str(self.whitewins)+' | '+str(self.draws)+' | '+str(self.blackwins))
                print('[',end="")
                winner = self.selfPlay(pairs[i][0],pairs[i][1])
                print(']')
                print('Draw\n' if winner=='D' else winner+' Wins')



n = GeneticAlgorithm()

n.run()
