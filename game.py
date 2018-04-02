#import pokebase as pb
import json
from random import randint
import commandParser

#https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/89.png
json_data=open("poke_list.text").read()
nameList = json.loads(json_data);

class GameState:
    def __init__(self):
        self.isStart = False
        self.roomID = ""
        self.wrongCount = 0
        self.pokeName = ""
        self.awnsered = ""
        self.correctPos = 0
        self.len = 0
        self.hint = 0
        self.progress = 0
        self.path = ""


def checkPermission(state,roomID):
    if state.roomID == roomID :
        return True
    else :
        return False

def gameStart(state, roomID):
    if state.isStart == False :
        state.isStart = True
        state.roomID = roomID
        state.progress = 1
        return 0
    elif state.roomID == roomID :
        return 1
    else :
        return 2

def gameRestart(state):
    state.wrongCount = 0
    state.pokeName = ""
    state.awnsered = ""
    state.correctPos = 0
    state.len = 0
    state.hint = 0
    state.progress = 1
    state.path = ""

def gameEnd(state, roomID):
    if checkPermission(state, roomID) == True and state.isStart == True:
        state.wrongCount = 0
        state.pokeName = ""
        state.awnsered = ""
        state.correctPos = 0
        state.len = 0
        state.hint = 0
        state.progress = 0
        state.path = ""
        state.isStart = False
        return 0

def getQuestion(state):
    selectI = randint(0, 100) + 1
    #pic = pb.pokemon_sprite(selectI)
    state.pokeName = nameList[selectI-1].upper()
    state.len = len(state.pokeName)
    for i in range(0, state.len):
        state.awnsered = state.awnsered + "_ "
    state.progress = 2
    state.path = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/" + str(selectI) + ".png"
    print(state.path)

def awnserQuestion(state, awnser, roomID):
    if checkPermission(state, roomID) == False:
        return 1
    if(state.isStart == 0):
        return 2

    state.hint = 0
    awnser = awnser.upper()
    minSize = min(state.len, len(awnser))
    stringList = list(state.awnsered)
    a=0
    isCorrectSome = False
    for i in range(0, minSize):
        if awnser[i] == state.pokeName[i]:
            if(stringList[a] == '_'):
                state.correctPos += 1
                isCorrectSome = True
            stringList[a] = awnser[i]
        a+=2

    if(isCorrectSome):
        state.wrongCount = 0
    else:
        state.wrongCount += 1

    if(state.wrongCount >= 3 and state.len - state.correctPos > 1):
        for i in range(0, state.len*2, 2):
            if(stringList[i] == '_'):
                stringList[i] = state.pokeName[int(i*0.5)]
                state.correctPos += 1
                state.wrongCount = 0
                state.hint = 1
                break

    state.awnsered = "".join(stringList)
    return 0

def isCorret(state):
    if(state.correctPos == state.len):
        return True
        state.progress = 3
    else:
        return False


def test():
    print("start")
    state = GameState()

    gameStart(state, 1)

    while True:
        getQuestion(state)
        print(state.pokeName)
        print(state.awnsered)

        while True:
            awns = input("awnser: ")
            awnserQuestion(state, awns, 1)
            if(state.hint == 1):
                print("Hint!")
            print(state.awnsered)
            if(isCorret(state)):
                print("Correct")
                break
        gameRestart(state)
