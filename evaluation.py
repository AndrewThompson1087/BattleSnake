# Evaluation Function for Battlesnake by Andrew Thompson and Charles Raines
from math import inf
from timeit import default_timer
from copy import deepcopy


# evaluates current state
def evaluate(state, move_choice):  # move choice is a string
    # eval_start = default_timer()

    evaluationValue = 0  # this determines how likely we are to win positive is good
    my_body = state["you"]["body"]
    my_head = my_body[0].copy()
    x, y = my_head["x"], my_head["y"]  # this one
    obstacles = []
    snakeid = state["you"]["id"]

    allsnakes = state['board']['snakes']

    # designed for 1v1's only
    for snake in allsnakes:
        if snake["id"] != snakeid:
            opponent = snake
            opponent_body = opponent["body"]
            opponent_head = opponent_body[0]
            enemy_x, enemy_y = opponent_head["x"], opponent_head["y"]
            enemy_length = opponent["length"]

    count = 0
    for i in my_body:
        x = i["x"]
        y = i["y"]
        if (count != 0):  # tested in seperate case
            obstacles.append([x, y])
        count += 1

    try:
        count = 0
        for k in opponent_body:
            enemy_x = k["x"]
            enemy_y = k["y"]
            if (count != 0):
                obstacles.append([enemy_x, enemy_y])
            count += 1

    except:
        pass

    board_height = state["board"]["height"]
    board_width = state["board"]["width"]
    my_health = state["you"]["health"]

    my_length = state["you"]["length"]
    ate_food = 0  # Boolean to see if we ate food

    flood_obstacles = deepcopy(obstacles)
    flood_head = deepcopy(my_head)
    # Calculate availible space for both snakes
    #c_space is choice space
    #c_space = close_fill(board_width, board_height, flood_head, flood_obstacles)
    #enemy_c_space = close_fill(board_width, board_height, flood_head, flood_obstacles)

    freespace = flood_fill(board_width, board_height, flood_head, flood_obstacles)

    enemy_flood_obstacles = deepcopy(obstacles)

    enemy_flood_head = deepcopy(opponent_head)

    enemy_freespace = flood_fill(board_width, board_height, enemy_flood_head, enemy_flood_obstacles)
    #print("free space: ", freespace)

    enemy_x = opponent_head["x"]
    enemy_y = opponent_head["y"]

    x = my_head["x"]
    y = my_head["y"]

    # print("My head: ", my_head)
    # print("My body: ", my_body)
    # print("Obstacles: ", obstacles)
    # Giant series of tests
    if my_health == 100:
        ate_food = 1

    if freespace < (my_length * enemy_length) + 2:
        # we are trapped
        evaluationValue -= 750

    if enemy_freespace < (my_length * enemy_length) + 2:
        # enemy is trapped
        evaluationValue += 750
    if freespace <= 5:
        evaluationValue += -705

    if enemy_freespace <= 5:
        evaluationValue += 705

    if (freespace <= 10) and (freespace == enemy_freespace) and my_length > enemy_length + 1:
        evaluationValue += 507

    if my_health < 10:
        # need to eat
        evaluationValue += (ate_food * 201)
        food_dist = food_find(state, obstacles, my_head)
        evaluationValue += (25 - food_dist) * 5

    if my_length > enemy_length:
        x_dist = abs(x - enemy_x)
        y_dist = abs(y - enemy_y)
        evaluationValue += (25 - (x_dist + y_dist)) * 5

    else:
        x_dist = abs(x - enemy_x)
        y_dist = abs(y - enemy_y)
        if x_dist >= 2 or y_dist >= 2:
            evaluationValue += 8
        evaluationValue += (x_dist + y_dist) * 2
        if (x == board_width - 1) or (y == board_height - 1):
            evaluationValue += -50
        elif (x == 1) or (y == 1):
            evaluationValue += -50

    if my_length <= 15 and ((my_length - enemy_length) <= 2):
        if ate_food:
            evaluationValue += 106
        food_dist = food_find(state, obstacles, my_head)

        evaluationValue += (25 - food_dist) * 3

    if (x == board_width - 1) or (y == board_height - 1):
        x_dist = abs(x - enemy_x)
        y_dist = abs(y - enemy_y)
        evaluationValue += (x_dist + y_dist) * 2

    elif (x == 1) or (y == 1):
        x_dist = abs(x - enemy_x)
        y_dist = abs(y - enemy_y)
        evaluationValue += (x_dist + y_dist) * 2

    x_dist = x - 5
    y_dist = y - 5
    center_dist = (15 - abs(x_dist + y_dist)) * 2
    evaluationValue += center_dist

    #Worth more at longer lengths
    if (my_length >= 18) and (enemy_length >= 18):
        evaluationValue += ((freespace - enemy_freespace) * 6)

    # death testing
    if (x >= board_width) or (x < 0):
        # print("eval snake out of x bounds")
        evaluationValue = -(inf)  # we lose

    elif (y >= board_height) or (y < 0):
        # print("eval snake out of y bounds")
        evaluationValue = -(inf)  # we lose

    elif (enemy_x >= board_width) or (enemy_x < 0):
        # print("eval enemy snake out of x bounds")
        evaluationValue = inf  # we win

    elif (enemy_y >= board_height) or (enemy_y < 0):
        # print("eval enemy snake out of y bounds")
        evaluationValue = inf  # we win

    elif ([enemy_x, enemy_y] in obstacles):
        # print("eval enemy snake in obstacles")
        # print("enemy head:", opponent_head)
        # print("enemy calc head: ", [enemy_x, enemy_y])
        evaluationValue = inf

    elif ([x, y] in obstacles):
        # print("eval snake in obstacles")
        evaluationValue = -(inf)

    elif ([x, y] == [enemy_x, enemy_y]):

        if my_length > enemy_length:
            #print("eval head on win")
            evaluationValue = inf
        elif my_length < enemy_length:
            #print("eval head on lose")
            #not -inf so that snake does not give up
            #enemy could mess up
            evaluationValue = -999999
        elif my_length == enemy_length:
            #print("eval head on tie")
            evaluationValue = 0
    elif (my_health == 0):
        evaluationValue = -inf

    else:
        evaluationValue += (((freespace - enemy_freespace) * 12) + (ate_food * 50))


    #print("Evaluation value: " + str(evaluationValue))
    #print("Evaluation move: ", move_choice)
    # print("Enemy body: ", opponent_body)
    # eval_end = default_timer()
    # time = (eval_end - eval_start) * 1000
    # print("eval run time: ", time)
    return evaluationValue

def food_find(state, obstacles, my_head):
    food = state['board']['food']
    food_dist = 25
    head_x = my_head["x"]
    head_y = my_head["y"]

    for i in food:
        food_x = i["x"]
        food_y = i["y"]
        dist = (abs(head_x - food_x) + abs(head_y - food_y))
        if [food_x, food_y] not in obstacles:
            if dist < food_dist:
                food_dist = dist

    return food_dist


def flood_fill(board_width, board_height, my_head, obstacles):

    flood_obstacles = obstacles
    move_area = 0
    move_queue = []
    x = my_head["x"]
    y = my_head["y"]

    move_queue.append([x, y])  # starting point

    while move_queue:  # while it's not empty
        n = move_queue[-1]
        move_queue.pop()
        x = n[0]
        y = n[1]
        if board_width > x >= 0:
            if board_height > y >= 0:
                if [x, y] not in flood_obstacles:
                    flood_obstacles.append([x, y])  # makes sure not counting it twice

                    move_area += 1  # counting total number of free spaces

                    move_queue.append([x + 1, y])  # adding possible free spaces
                    move_queue.append([x, y + 1])
                    move_queue.append([x - 1, y])
                    move_queue.append([x, y - 1])

    return move_area
