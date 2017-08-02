import elements
import flask
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import json
import base64
import uuid
import logging
import time
from math import floor
from logging.handlers import RotatingFileHandler

app = flask.Flask('elements')
games = {}
invites = {}
loghandler = RotatingFileHandler('elements.log')
loghandler.setLevel(logging.INFO)
app.logger.addHandler(loghandler)

def newID():
    u = uuid.uuid4()
#    u = base64.urlsafe_b64encode(u.bytes)
    u = u.hex
    if u not in games.keys():
        return u
    else:
        return newID()

def addGame():
    g = Game()
    ids = g.players.keys()
    for id in ids:
        games[id] = g
    return tuple(ids)

class Game:
    def __init__(self):
        self.created = floor(time.time())
        self.game = elements.GameState()
        self.players = {}
        self.players[newID()] = 0
        self.players[newID()] = 1
        self.room = newID()

##################################### Flask Code
@app.route('/static/<path:path>')
def send_static(path):
    return flask.send_from_directory('static', path)

@app.route("/game/new") # create new game, redirect to new page, give invite link, renders new game page
def newGame():
    id_player, id_invite = addGame()
    u = newID()
    invites[u] = id_invite
    return flask.render_template('newgame.html', game_id = id_player, invite_id = u)

@app.route("/game/<string:game_id>") # present game state
def game(game_id):
    g = games[game_id]
    p = g.players[game_id]
#    return flask.jsonify(elements.gameStateToJSON(g.game, p))
    return flask.render_template('game.html', game_id = game_id)

@app.route("/invite/<string:invite_id>")
def acceptInvitation(invite_id):
    if invite_id not in invites.keys():
        app.logger.error('Invalid invite key %s' % invite_id)
        return "Invite invalid"
    else:
        player_id = invites.pop(invite_id)
        app.logger.info('Invite used: %s' % invite_id)
        return flask.redirect(flask.url_for("game", game_id=player_id))#"/%s" % player_id))

## realtime socket part

socketio = SocketIO(app)

@socketio.on('message')
def handle_message(message):
    print('Received: ' + str(message))
    return "test"

@socketio.on('game')
def getGameState(game_id):
    if game_id in games.keys():
        g = games[game_id]
        p = g.players[game_id]
        if g.game.winner != None:
            if g.game.winner == p:
                emit("gameover", "you")
            else:
                emit("gameover", "other")
        room = g.room
        join_room(room)
        emit("game", elements.gameStateToJSON(g.game, p))
        print("Sent back game state for %s" % game_id)
    else:
        # in this case the client should reload
        pass

@socketio.on('move')
def processMove(data):
    print(data)
    game_id = data['game']
    # retreive game from database
    g = games[game_id]
    player_id = g.players[game_id]
    movetype = elements.str2Movetype(data['type'])
    if 'target' in data.keys():
        target = data['target']
    else:
        target = None
    move = elements.Move(player_id, movetype, target)
    # write back to database
    try:
        g.game.applyMove(move)
    except elements.InvalidMove:
        emit('error', "Invalid Move")
    room = g.room
    emit("requpdate", room=room)
#    emit("game", elements.gameStateToJSON(g.game, player_id), room=room)

@socketio.on("echo")
def echo(json):
    print(json)
    send(json, json=True)
