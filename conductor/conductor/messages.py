from box import Box


def is_join_request(message):
    return message.body.action == 'join'


def is_challenge_request(message):
    return message.body.action == 'challenge'


def question(text):
    return Box(question=text)


def joined(user):
    return Box(event='joined', user=user)


def challenged(user):
    return Box(event='challenged', user=user)


def reply(answers):
    return Box(action='reply', answers=answers)


def lost(user):
    return Box(event='lost', user=user)


def end(winner):
    return Box(event='end', winner=winner)
