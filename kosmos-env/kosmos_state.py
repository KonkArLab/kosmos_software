from enum import Enum, unique

@unique
class KState(Enum):
    """Etats du kosmos"""
    STARTING = 0
    STANDBY = 1
    WORKING = 2
    STOPPING = 3
    SHUTDOWN = 4
