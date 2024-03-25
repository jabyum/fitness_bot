from enum import Enum


class States(Enum):
    START = 0
    ASK_QUESTION = 1
    WAITING_FOR_REPLY = 2
    REPLYING_QUESTION = 3
    IDLE = 4
    REPLIED = 5
