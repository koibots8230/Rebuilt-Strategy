import numpy as np
import matplotlib.pyplot as plt
from rebuilt import *
import random
import copy
import sys
import seaborn as sns
capacity = 20
def simulate_game():

    redPointsLog = []
    bluePointsLog = []
    times = []
    middleBallsLog = []
    redBallsLog = []
    blueBallsLog = []

    robots = [
        Robot(
    [fullAutoActions["Shoot"], pickupAction],
    False,
    [fullTeleopActions["Shoot"], fullTeleopActions["ShootToSide"], pickupAction],
    [fullEndgameActions["Nothing"]],
    capacity,
    True,
    False,
    False,
    Alliance.BLUE,
    Position.SCORE
),
Robot(
    [fullAutoActions["Shoot"], pickupAction],
    False,
    [fullTeleopActions["Shoot"], fullTeleopActions["ShootToSide"], pickupAction],
    [fullEndgameActions["Nothing"]],
    capacity,
    True,
    False,
    False,
    Alliance.BLUE,
    Position.SCORE
),
Robot(
    [fullAutoActions["Shoot"], pickupAction],
    False,
    [fullTeleopActions["Shoot"], fullTeleopActions["ShootToSide"], pickupAction],
    [fullEndgameActions["Nothing"]],
    capacity,
    True,
    False,
    False,
    Alliance.BLUE,
    Position.SCORE
),
Robot(
    [fullAutoActions["Shoot"], pickupAction],
    False,
    [fullTeleopActions["Shoot"], fullTeleopActions["ShootToSide"], pickupAction],
    [fullEndgameActions["Nothing"]],
    capacity,
    True,
    False,
    False,
    Alliance.RED,
    Position.SCORE
),
Robot(
    [fullAutoActions["Shoot"], pickupAction],
    False,
    [fullTeleopActions["Shoot"], fullTeleopActions["ShootToSide"], pickupAction],
    [fullEndgameActions["Nothing"]],
    capacity,
    True,
    False,
    False,
    Alliance.RED,
    Position.SCORE
),
Robot(
    [fullAutoActions["Shoot"], pickupAction],
    False,
    [fullTeleopActions["Shoot"], fullTeleopActions["ShootToSide"], pickupAction],
    [fullEndgameActions["Nothing"]],
    capacity,
    True,
    False,
    False,
    Alliance.RED,
    Position.SCORE
)
    ]

    totalPreload = 0
    for robot in robots:
        totalPreload += robot.storage

    field = Field(408 - totalPreload)

    bluePoints = 0
    redPoints = 0
    
    while True:
        bot = None
        for robot in robots:
            if bot == None or robot.time < bot.time:
                bot = robot
        # if robots.index(bot) == 0:
        #     print(")))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))")
        # print(f"time: {bot.time}")
        # print(f"BOT: {robots.index(bot)}")

        if bot.time > 160:
            break

        if bot.time < 20:
            field.phase = Phase.AUTO
            # print(field.phase)
            # print(f"Current bot stores: {bot.storage}")
            action = bot.autoSample(field)

        else:
            if bot.time < 30:
                if field.phase == Phase.AUTO:
                    field.phase = Phase.TRANSITION
                    # blue always wins
                    # field.evenPhases = Alliance.BLUE
                    # field.oddPhases = Alliance.RED
                    
                    if bluePoints > redPoints:
                        field.evenPhases = Alliance.BLUE
                        field.oddPhases = Alliance.RED
                        # print("\n*********************************\n***BLUE WON AUTO***\n********************************************\n")

                    elif bluePoints < redPoints:
                        field.evenPhases = Alliance.RED
                        field.oddPhases = Alliance.BLUE
                        # print("\n********************************************\n***RED WON AUTO***\n********************************************\n")

                    else:
                        if random.random() > 0.5:
                            field.evenPhases = Alliance.BLUE
                            field.oddPhases = Alliance.RED
                            # print("\n********************************************\n***BLUE WON AUTO***\n*******************************************\n")
                        else:
                            field.evenPhases = Alliance.RED
                            field.oddPhases = Alliance.BLUE
                            # print("\n********************************************\n***RED WON AUTO***\n********************************************\n")
        
            elif bot.time < 130:
                if field.phase == Phase.TRANSITION:
                    field.phase = Phase.SHIFT1
                    if field.oddPhases == Alliance.BLUE:
                        field.blue_active = True
                        field.red_active = False
                    else:
                        field.blue_active = False
                        field.red_active = True
                elif field.phase == Phase.SHIFT1:
                    if bot.time >= 55:
                        field.phase = Phase.SHIFT2
                        if field.evenPhases == Alliance.BLUE:
                            field.blue_active = True
                            field.red_active = False
                        else:
                            field.blue_active = False
                            field.red_active = True
                elif field.phase == Phase.SHIFT2:
                    if bot.time >= 80:
                        field.phase = Phase.SHIFT3
                        if field.oddPhases == Alliance.BLUE:
                            field.blue_active = True
                            field.red_active = False
                        else:
                            field.blue_active = False
                            field.red_active = True
                elif field.phase == Phase.SHIFT3:
                    if bot.time >= 105:
                        field.phase = Phase.SHIFT4
                        if field.evenPhases == Alliance.BLUE:
                            field.blue_active = True
                            field.red_active = False
                        else:
                            field.blue_active = False
                            field.red_active = True
            
            else:
                if field.phase == Phase.SHIFT4:
                    field.phase = Phase.ENDGAME
                    field.blue_active = True
                    field.red_active = True    
            
            #print(field.phase)
            #print(f"Current bot stores: {bot.storage}")
            action = bot.teleopSample(field)

        times.append(bot.time)
        actionTime = action.get_time(bot.storage)
        if actionTime == -1:
            continue
        bot.time += actionTime

        if bot.alliance == Alliance.BLUE:
            bluePoints += action.points
        else:
            redPoints += action.points
        bluePointsLog.append(bluePoints)
        redPointsLog.append(redPoints)

        middleBallsLog.append(field.fuel_middle)
        redBallsLog.append(field.fuel_red)
        blueBallsLog.append(field.fuel_blue)
        
        #print(f"Field middle: {field.fuel_middle}, blue home: {field.fuel_blue}, red home: {field.fuel_red}")
        #print(f"blue: {bluePoints}, red: {redPoints}")
        #print("--------------------------------------")

    # for robot in robots:
    #     print ("\n\n NEW ROBOT \n\n")
    #     autoTime = 20

    #     while autoTime > 0:
    #         action = robot.autoSample(field)
    #         time = 0
    #         points = 0
    #         if action == pickupAction:
    #             time = action.get_time(robot.maxStorage - robot.storage)
    #             for a in range(robot.maxStorage - robot.storage):
    #                 do_pickup(field, robot, PickupLocation.MIDDLE)
    #             print("Picking up")
    #         elif action == fullAutoActions["Shoot"]:
    #             time = action.get_time(robot.storage)
    #             points = action.points * robot.storage
    #             robot.storage = 0
    #             print("Scoring")
    #         else:
    #             time = action.get_time()

    #             print("Other")

    #         if (autoTime > time):
    #             print(f"Subtracting time {time} remaining: {autoTime - time}")
    #             autoTime -= time
    #             match robot.alliance:
    #                 case Alliance.BLUE:
    #                     bluePoints += points
    #                 case Alliance.RED:
    #                     redPoints += points
    #         else:
    #             print("Not enough time to complete action!")
    #             break
    return (middleBallsLog, blueBallsLog, redBallsLog, times)
    #return (bluePoints, redPoints)

results = simulate_game()

plt.plot(results[3], results[0], color="purple")
plt.plot(results[3], results[1], color="blue")
plt.plot(results[3], results[2], color="red")

plt.xlabel("Time (s)")
plt.ylabel("# of Fuel in Zone")

plt.axvline(20)
plt.axvline(30)
plt.axvline(55)
plt.axvline(80)
plt.axvline(105)
plt.axvline(130)
plt.tight_layout()
plt.savefig("mostrecentrun.png")
plt.show()

# fig, axs = plt.subplots(1, 2, figsize=(15,5))
# print("Running...")
# results = [simulate_game() for _ in range(500)]

# totals = []

# for result in results:
#     totals.append(result[0])
#     totals.append(result[1])

# print(np.median(totals))

# blueWins = 0
# redWins = 0
# for data in results:
#     if data[0] > data[1]:
#         blueWins += 1
#     else:
#         redWins += 1

# print(blueWins)
# print(redWins)

# cats = ["Blue (wins auto)", "Red (loses auto)"]
# vals = [blueWins, redWins]

# plt.bar(cats, vals)

# plt.xlabel("Teams")
# plt.ylabel("# of Wins")
# plt.savefig("mostrecent.png")
# plt.show()
# a = 0
# for i, (data, ax) in enumerate(zip(list(map(list, zip(*results))), axs)):
#     sns.histplot(data = data, kde=True, ax=ax)
#     if a == 0:
#         ax.set_xlabel("Points - Can Climb L3")
#     else:
#         ax.set_xlabel("Points - Can Climb L1")
#     ax.set_ylabel("# of Games")
#     a += 1
# print("Done")

# plt.tight_layout()
# plt.savefig("mostrecent.png")
# plt.show()