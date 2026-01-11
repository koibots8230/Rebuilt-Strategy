import numpy as np
from enum import Enum
import random

class Position(Enum):
    SCORE = 0
    CLIMB = 1
    MIDDLE = 2
    DEPOT = 3

class Action:
    def __init__(self, points: int, average_time: float, time_spread: float, required_position: Position,
                 proportion_of_success: float = 1, quantity_variable: bool = False, constant_time: float = 0):
        self.points = points
        self.average_time = average_time
        self.time_spread = time_spread
        self.success_proportion = proportion_of_success
        self.quantity_variable = quantity_variable
        self.constant_time = constant_time
        self.required_position = required_position

    def get_time(self, quantity: int = 0):
        if (random.random() > self.success_proportion):
            return -1.0
        if self.quantity_variable:
            return np.random.normal((self.average_time * quantity) + self.constant_time, self.time_spread)
        else:
            return np.random.normal(self.average_time, self.time_spread)

class PickupLocation(Enum):
    MIDDLE = 0
    HOME = 1
    DEPOT = 2

def do_pickup(field, robot, location: PickupLocation):
    match location:
        case PickupLocation.MIDDLE:
            if (field.fuel_middle > 0):
                field.fuel_middle -= 1
            else:
                return False
        case PickupLocation.HOME:
            if robot.alliance == Alliance.BLUE and field.fuel_blue > 0:
                field.fuel_blue -= 1
            elif robot.alliance == Alliance.RED and field.fuel_red > 0:
                field.fuel_red -= 1
            else:
                return False
        case PickupLocation.DEPOT:
            if robot.alliance == Alliance.BLUE and field.fuel_bdepot > 0:
                field.fuel_bdepot -= 1
            elif robot.alliance == Alliance.RED and field.fuel_rdepot > 0:
                field.fuel_rdepot -= 1
            else:
                return False

    if (robot.storage >= robot.maxStorage):
        #print("Why are you even trying to pick shit up, storage is full")
        return False
    robot.storage += 1
    return True


class Field:
    def __init__(self, fuel_middle: int):
        self.fuel_middle = fuel_middle
        self.fuel_blue = 0
        self.fuel_red = 0
        self.fuel_routpost = 24
        self.fuel_boutpost = 24
        self.fuel_rdepot = 24
        self.fuel_bdepot = 24
        self.phase = Phase.PREMATCH
        self.oddPhases = None
        self.evenPhases = None
        self.blue_active = True
        self.red_active = True

def findBestAction(actionsList):
    highestPointsForTime = -1
    bestAction = None
    for action in actionsList:
        if action.points / action.average_time >= highestPointsForTime:
            highestPointsForTime = action.points / action.average_time
            bestAction = action
    return bestAction

class Alliance(Enum):
    BLUE = 0
    RED = 1

class Phase(Enum):
    PREMATCH = 0
    AUTO = 1
    TRANSITION = 2
    SHIFT1 = 3
    SHIFT2 = 4
    SHIFT3 = 5
    SHIFT4 = 6
    ENDGAME = 7

class Robot:
    def __init__(self, autoActions, canAutoClimb, teleopActions, endgameActions, maxStorage, canBump, canTrench, canDepot, alliance, position):
        self.autoActions = autoActions
        self.canAutoClimb = canAutoClimb
        self.teleopActions = teleopActions
        self.endgameActions = endgameActions
        self.maxStorage = maxStorage
        self.canBump = canBump
        self.canTrench = canTrench
        self.canDepot = canDepot
        self.storage = 8 if maxStorage >= 8 else maxStorage
        self.alliance = alliance
        self.position = position
        self.time = 0
        self.intaking = False
        self.shooting = False
        self.hasEndgamed = False

    def pathToPosition(self, position):
        match self.position:
            case Position.MIDDLE:
                if position == Position.CLIMB:
                    self.position = Position.CLIMB
                    return driveTimes["MiddleToClimbBump"] if self.canBump else driveTimes["MiddleToClimbTrench"]
                elif position == Position.SCORE:
                    self.position = Position.SCORE
                    return driveTimes["ScoreToMiddleBump"] if self.canBump else driveTimes["ScoreToMiddleTrench"]
            case Position.SCORE:
                if position == Position.MIDDLE:
                    self.position = Position.MIDDLE
                    return driveTimes["ScoreToMiddleBump"] if self.canBump else driveTimes["ScoreToMiddleTrench"]
                elif position == Position.CLIMB:
                    self.position = Position.CLIMB
                    return driveTimes["ScoreToClimb"]
            case Position.CLIMB:
                if position == Position.MIDDLE:
                    self.position = Position.MIDDLE
                    return driveTimes["MiddleToClimbBump"] if self.canBump else driveTimes["MiddleToClimbTrench"]
                elif position == Position.SCORE:
                    self.position = Position.SCORE
                    return driveTimes["ScoreToClimb"]

    def autoSample(self, field):
        
        if self.position == Position.CLIMB:
            return fullAutoActions["Climb"]
        if self.storage == 0:
            #print("Intaking")
            self.intaking = True
        elif self.intaking and self.storage == self.maxStorage:
            #print("Stop intake")
            self.intaking = False
        
        if self.intaking and self.canDepot:
            #print("Pickup from depot")
            if self.position == pickupDepot.required_position:
                if do_pickup(field, self, PickupLocation.DEPOT):
                    return pickupDepot
                else:
                    return Action(0, 1, 0, None)
            else:
                if self.canAutoClimb and 20 - self.time < 8:
                    return self.pathToPosition(Position.DEPOT)
                else:
                    return self.pathToPosition(pickupAction.required_position)
        if self.intaking:
            #print("Picking up from middle")
            if self.position == pickupAction.required_position:
                if do_pickup(field, self, PickupLocation.MIDDLE):
                    return pickupAction
                else:
                    return Action(0, 1, 0, None)
            else:
                if self.canAutoClimb and 20 - self.time < 12:
                    return self.pathToPosition(Position.CLIMB)
                else:
                    return self.pathToPosition(pickupAction.required_position)
        else:
            if not self.shooting:
                self.shooting = True
                return startupShooter
            if self.position == fullAutoActions["Shoot"].required_position:
                self.storage -= 1
                field.fuel_middle += 1
                return fullAutoActions["Shoot"]
            else:
                return self.pathToPosition(fullAutoActions["Shoot"].required_position)

        # if self.storage > 0:
        #     if self.position == fullAutoActions["Shoot"].required_position:
        #         return fullAutoActions["Shoot"]
        #     else:
        #         return self.pathToPosition(fullAutoActions["Shoot"].required_position)
        # else:
        #     if self.position == pickupAction.required_position:
        #         return pickupAction
        #     else:
        #         #print("Pathing to pickup")
        #         return self.pathToPosition(pickupAction.required_position)
            
    def teleopSample(self, field):
        hub_active = ((self.alliance == Alliance.BLUE and field.blue_active) or (self.alliance == Alliance.RED and field.red_active))
        if self.storage == 0:
            #print("Starting to intake")
            self.intaking = True
            self.shooting = False
        elif self.intaking and self.storage == self.maxStorage:
            self.intaking = False
            #print("Stopping intake")

        if self.time > 160 - 8 - findBestAction(self.endgameActions).average_time:
            #print("Doing Endgame")
            if self.position != findBestAction(self.endgameActions).required_position:
                return self.pathToPosition(findBestAction(self.endgameActions).required_position)
            elif not self.hasEndgamed:
                self.hasEndgamed = True
                return findBestAction(self.endgameActions)
            else:
                return Action(0, 1, 0, None)
        
        if self.intaking:

            shouldHomePickup = (self.alliance == Alliance.BLUE and field.fuel_blue >= self.maxStorage / 1.5) or (self.alliance == Alliance.RED and field.fuel_red >= self.maxStorage / 1.5)
            if shouldHomePickup and self.position != Position.MIDDLE:
                #print("Doing Home pickup")
                if do_pickup(field, self, PickupLocation.HOME):
                    return pickupAction
                else:
                    self.intaking = False
                    return Action(0, 0, 0, None)
            
            #print("Doing Middle Pickup")
            if self.position == pickupAction.required_position:
                
                if do_pickup(field, self, PickupLocation.MIDDLE):
                    return pickupAction
                else:
                    return Action(0, 1, 0, None)
            else:
                return self.pathToPosition(pickupAction.required_position)
        elif not hub_active:
            #print("Funneling to own side")
            if not self.shooting:
                self.shooting = True
                return startupShooter
            if self.position == fullTeleopActions["ShootToSide"].required_position:
                self.storage -= 1
                if self.alliance == Alliance.BLUE:
                    field.fuel_blue += 1
                else:
                    field.fuel_red += 1
                return fullTeleopActions["ShootToSide"]
            else:
                return self.pathToPosition(fullTeleopActions["ShootToSide"].required_position)
        elif hub_active:
            #print("Shooting")
            if not self.shooting:
                self.shooting = True
                return startupShooter
            if self.position == fullTeleopActions["Shoot"].required_position:
                self.storage -= 1
                field.fuel_middle += 1
                return fullTeleopActions["Shoot"]
            else:
                return self.pathToPosition(fullTeleopActions["Shoot"].required_position)
        else:
            #print("Doing fuckall in teleop")
            return Action(0, 1, 0, None)


driveTimes = {
    "ScoreToClimb": Action(0, 1.75, 0.25, None),
    "ScoreToMiddleBump": Action(0, 3.4, 0.25, None),
    "ScoreToMiddleTrench": Action(0, 3.9, 0.25, None),
    "MiddleToClimbBump": Action(0, 4, 0.25, None),
    "MiddleToClimb": Action(0, 4.5, 0.25, None)
}


pickupAction = Action(0, 0.5, 0.1, Position.MIDDLE)

pickupDepot = Action(0, 0.2, 0.05, Position.DEPOT)

startupShooter = Action(0, 1.5, 0.2, None)

fullAutoActions = {
    "Shoot": Action(1, 0.425, 0.05, Position.SCORE),
    "Climb": Action(15, 5, 0.5, Position.CLIMB)
}

fullTeleopActions = {
    "Shoot": Action(1, 0.425, 0.1, Position.SCORE),
    "ShootToSide": Action(0, 0.425, 0.2, Position.MIDDLE)
}

fullEndgameActions = {
    "Nothing": Action(0, 5, 0, Position.CLIMB),
    "Climb L1": Action(10, 5, 2, Position.CLIMB),
    "Climb L2": Action(20, 10, 2, Position.CLIMB),
    "Climb L3": Action(30, 15, 2, Position.CLIMB),
}