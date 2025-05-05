from bot import bot1 as b1
from bot import bot2 as b2

def RobotGateway(ship, position: tuple, botType: int):
    if botType == 1:
        robot = b1.Bot1(ship, position)
    elif botType == 2:
        robot = b2.Bot2(ship, position)
    else:
        raise ValueError(f"Invalid botType: {botType}")
    return robot