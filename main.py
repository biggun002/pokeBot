from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage
)

import game
import commandParser

app = Flask(__name__)

line_bot_api = LineBotApi('')
handler = WebhookHandler('')

stateList = {}

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if(event.source.type == 'user'):
        id = event.source.user_id
        profile = line_bot_api.get_profile(id)
    elif(event.source.type == 'room'):
        id = event.source.room_id
        profile = line_bot_api.get_room_member_profile(id, event.source.user_id)
    elif(event.source.type == 'group'):
        id = event.source.group_id
        profile = line_bot_api.get_group_member_profile(id, event.source.user_id)

    command = commandParser.splitCommand(event.message.text)
    if(command == None):
        return None

    if id in stateList:
        state = stateList[id]
    else:
        state = game.GameState()
        stateList[id] = state

    reply = []
    name = profile.display_name

    if(command == 'play'):
        ret = game.gameStart(state, id)
        if(ret == 0):
            reply.append(TextSendMessage(text="== Start Game ==\nWho's That Pokemon?\nStart command with colon\n:play = play game\n:end = end game\n:<awnser> = awnser Ex. :pikachu"))
        elif(ret == 1):
            reply.append(TextSendMessage(text="@%s\nGame already started"%name))
            line_bot_api.reply_message(
                event.reply_token, reply)
            return None
        elif(ret == 2):
            reply.append(TextSendMessage(text="@%s\nOther room playing, Please Wait"%name))
            line_bot_api.reply_message(
                event.reply_token, reply)
            return None
    elif(command == 'end'):
        ret = game.gameEnd(state, id)
        if(ret == 0):
            winner = ""
            winScore = 0
            text = "== End Game =="
            for key in state.score:
                text = text+"\n%s --> %d Points"%(key,state.score[key])
                if(state.score[key] > winScore):
                    winScore = state.score[key]
                    winner = key
            text = text + "\nThe winner is [%s] !"%winner
            reply.append(TextSendMessage(text=text))
            line_bot_api.reply_message(
                event.reply_token, reply)
            return None

    if(state.progress == 1):
        game.getQuestion(state)
        reply.append(ImageSendMessage(original_content_url=state.path, preview_image_url=state.path))
        reply.append(TextSendMessage(text=state.awnsered))
    elif(state.progress == 2):
        if(command == 'score'):
            text="=== Score ==="
            for key in state.score:
                text = text+"\n%s --> %d Points"%(key,state.score[key])
            reply.append(TextSendMessage(text=text))
            line_bot_api.reply_message(
                event.reply_token, reply)
            return None

        ret = game.awnserQuestion(state, command, name, id)
        if(ret == 1):
            reply.append(TextSendMessage(text="@%s\nOther room playing, Please Wait"%name))
            line_bot_api.reply_message(
                event.reply_token, reply)
            return None

        text = "@%s\n"%name + state.awnsered
        if(game.isCorret(state)):
            text = text + " --> CORRECT!\nScore = %d Points\nNext Question"%state.score[name]
            reply.append(StickerSendMessage(package_id='2', sticker_id='144'))
            reply.append(TextSendMessage(text=text))
            game.gameRestart(state)
            game.getQuestion(state)
            reply.append(ImageSendMessage(original_content_url=state.path, preview_image_url=state.path))
            reply.append(TextSendMessage(text=state.awnsered))
        else:
            text = text + " --> WRONG!"
            if(state.hint == 1):
                text = text + " --> HINT!"
            reply.append(TextSendMessage(text=text))
    if(len(reply) > 0):
        line_bot_api.reply_message(
            event.reply_token, reply)

if __name__ == "__main__":
    app.run()
