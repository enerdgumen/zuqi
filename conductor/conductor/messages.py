from box import Box


def is_challenge_request(message):
    return message.body.action == 'challenge'


def question(text):
    return Box(event='question', question=text)


def joined(user):
    return Box(event='joined', user=user)


def left(user):
    return Box(event='left', user=user)


def challenged(user):
    return Box(event='challenged', user=user)


def reply(answers, timeout):
    return Box(event='reply', answers=answers, timeout=timeout)


def lost(user):
    return Box(event='lost', user=user)


def end(winner):
    return Box(event='end', winner=winner)
