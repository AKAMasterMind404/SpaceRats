from robot import robot as r
from robot import bot1 as b1
from robot import bot2 as b2
from robot import bot3 as b3

def RobotGateway(ship, position: tuple, botType: int) -> r.Robot:
    if botType == 1:
        robot = b1.Bot1(ship, position)
    elif botType == 2:
        robot = b2.Bot2(ship, position)
    elif botType == 3:
        robot = b3.Bot3(ship, position)
    else:
        raise ValueError(f"Invalid botType: {botType}")
    return robot