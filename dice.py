import random
from mushyutils import colorfy

class DiceException(Exception):
    __slots__ = ("msg")
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def resolve(token):
    bits = token.split("d")
    r = 0
    msg = ""
    try:
        if len(bits) != 2:
            r = int(token)
            return int(token), token
        num = int(bits[0])
        sides = int(bits[1])
        if sides > 100 or sides < 2 or num < 1 or num > 20:
            raise DiceException(str(token))
        dice = []
        for i in range(num):
            d = random.randint(1, sides)
            r += d
            dice.append(str(d))
        msg = colorfy("(" + " + ".join(dice) + ")", "green")
    except:
        raise DiceException(str(token))
    return r, msg


def fudge():
    results = [random.randint(-1, 1) for _ in range(4)]
    chars = {-1: '-', 0: '=', 1: '+'}
    tones = {-1: 'bred', 0: 'default', 1: 'bgreen'}
    result = sum(results)
    if result > 0:
        result = colorfy(str(result), "bgreen")
    elif result == 0:
        result = colorfy(str(result), "default")
    else:
        result = colorfy(str(result), "bred")
    return result, " ".join([colorfy(chars[x], tones[x]) for x in results])


def parse(text):
    tokens = format(text)
    result, msg = resolve(tokens[0])
    i = 1
    while(i < len(tokens) - 1):
        peek, peek_msg = resolve(tokens[i + 1])
        if tokens[i] == "+":
            result += peek
            msg += " + " + peek_msg
        elif tokens[i] == "-":
            result -= peek
            msg += " - " + peek_msg
        i += 2
    return result, msg


def format(text):
    text = text.replace("+", " + ")
    text = text.replace("-", " - ")
    bits = text.split()
    return bits
