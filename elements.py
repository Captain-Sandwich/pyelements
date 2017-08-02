import itertools as it
import random
import operator
import collections
import json
from enum import Enum

allCards = [1,1,2,2,3,3,4,4,5,5,6,6,6,6,6,6]

class MoveType(Enum):
    KNOCK = 1
    DROP6 = 2
    TAKE = 3
    PLAY = 4

Move = collections.namedtuple('Move', ['player', 'type', 'target'])

class InvalidMove(Exception):
    pass

def str2Movetype(s):
    s = s.upper()
    if s == 'PLAY':
        movetype = MoveType.PLAY
    elif s == 'KNOCK':
        movetype = MoveType.KNOCK
    elif s == 'DROP6':
        movetype = MoveType.DROP6
    elif s == 'TAKE':
        movetype = MoveType.TAKE
    return movetype


def other(x):
    if x == 0:
        return 1
    if x == 1:
        return 0

class Player:
    def __init__(self, hand):
        self.board = []
        self.hand = sorted(hand)

    @property
    def score(self):
        return sum(it.chain(self.board, self.hand))

class GameState:
    def __init__(self,seed=123):
        self.board = []
        random.seed(seed)
        deck = list(allCards)
        random.shuffle(deck)
        self.players = [Player(deck[:6]),Player(deck[6:12])]
        self.currentPlayer = random.choice([0, 1])
        self.knocker = None
        self.winner = None

    @property
    def limit(self):
        return sum(self.board)

    def getWinner(self):
        scores = [p.score for p in self.players]
        if self.knocker != None:
            if scores[other(self.knocker)] > self.limit or scores[self.knocker] > scores[other(self.knocker)]:
                return self.knocker
            else:
                return other(self.knocker)
        try:
            next(self.possibleMoves())
        except StopIteration:
            return other(self.currentPlayer)
        else:
            return None

    def possibleMoves(self):
        player = self.players[self.currentPlayer]
        if player.score <= self.limit:
            yield Move(self.currentPlayer, MoveType.KNOCK, None)
        if self.board:
            yield Move(self.currentPlayer, MoveType.TAKE, self.board[-1])
        if 6 in player.hand:
            yield Move(self.currentPlayer, MoveType.DROP6, None)
        for c in player.hand:
            yield Move(self.currentPlayer, MoveType.PLAY, c)

    def applyMove(self, move):
        if self.knocker != None:
            raise InvalidMove()
        player = self.players[self.currentPlayer]
        if move.player != self.currentPlayer:
            raise InvalidMove()
        if move not in self.possibleMoves():
            raise InvalidMove()
        if move.type == MoveType.DROP6:
            player.hand.remove(6)
        if move.type == MoveType.PLAY:
            player.hand.remove(move.target)
            self.board.append(move.target)
        if move.type == MoveType.TAKE:
            c = self.board.pop()
            player.board.append(c)
        if move.type == MoveType.KNOCK:
            self.knocker = self.currentPlayer

        # change player
        self.currentPlayer = other(self.currentPlayer)
        self.winner = self.getWinner()

    def run(self):
        while True:
            if self.getWinner() != None:
                print("winner %d" % self.getWinner())
                break
            move = random.choice(list(self.possibleMoves()))
            self.applyMove(move)
            print('-'*80)
            print(move)
            print(self.players[0].board, self.players[0].hand, self.players[0].score)
            print(self.board, self.limit)
            print(self.players[1].board, self.players[1].hand, self.players[1].score)

def gameStateToJSON(state, player=0):
    result = {}
    result['type'] = 'gamestate'
    result['board'] = state.board
    result['limit'] = state.limit
    result['playerHand'] = state.players[player].hand
    result['playerBoard'] = state.players[player].board
    result['playerScore'] = state.players[player].score
    result['otherHand'] = len(state.players[other(player)].hand)
    result['otherBoard'] = state.players[other(player)].board
    result['playerActive'] = state.currentPlayer == player
    result['gameOver'] = state.winner != None
    if state.winner != None:
        result['otherHandCards'] = state.players[other(player)].hand
    return result

if __name__ == '__main__':
    g = GameState(seed = random.randint(0, 2**32))
    print([p.score for p in g.players])
    print(list(g.possibleMoves()))
