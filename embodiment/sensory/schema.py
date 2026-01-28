from enum import Enum


class SensoryChannel(str, Enum):
    TOUCH = "touch"
    PAIN = "pain"
    PROPRIOCEPTION = "proprioception"
    TEMPERATURE = "temperature"
    BALANCE = "balance"