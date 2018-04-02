def splitCommand(text):
    if(len(text) < 2 or text[0]!=':'):
        return None

    command = text[1:]
    return command
