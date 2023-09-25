# main code for battlesnake by Andrew Thompson, Josh Waldbieser, and Charles Raines
import typing
import evaluation
import simulation
from math import inf
from timeit import default_timer
from sys import argv
from copy import deepcopy

move_start = default_timer()


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data

def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Andrew",  # TODO: Your Battlesnake Username
        "color": "#336699",  # TODO: Choose color
        "head": "tongue",  # TODO: Choose head
        "tail": "nr-booster",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    # inputing "down" does not affect minmax unless depth is zero. Ignore it
    global move_start
    move_start = default_timer()
    # print("Original Body: ", game_state['you']['body'])
    score, move = minimax(game_state, 4, "down", True, -inf, inf)
    if move == "None":
        #print("Panic Mode")
        move = panic_move(game_state)

    move_end = default_timer()
    move_time = (move_end - move_start)
    #print("Turn: ", game_state["turn"])
    #print("Total Calc Time: ", move_time)
    #print("Score of move: ", score)
    #print("Move: ", move, "\n")
    return {"move": move}


# maxer is a boolean representing if current player is the maximixing player
# Tweak based on the specifics of how evaluation is implemented
# Might need to add in Neighbors (as generated in the move function) as a parameter here.
# It might be ok though, since this function should only be called within the move function anyway,
# and the scope might be ok with that in Python.
def minimax(state: typing.Dict, depth, move, maxer, alpha, beta):
    # If the depth is 0 or this state is an end state (win or loss)
    move_time = measure_time(depth)

    # simulates and tests for death

    death = is_terminal(state, move)
    # tests if bottom reached, someone died, or running out of time
    if (depth == 0) or (death == True) or move_time > 0.2:

        try:
            return evaluation.evaluate(state, move), move
        except:
            return inf, move

    # try to give same depths equal time
    if depth == 1 and move_time > 0.3:
        print("Equal time stop, depth: ", depth)
        try:
            return evaluation.evaluate(state, move), move
        except:
            return inf, move

    if depth == 2 and move_time > 0.35:
        print("Equal time stop, depth: ", depth)
        try:
            return evaluation.evaluate(state, move), move
        except:
            return inf, move

    if depth == 3 and move_time > 0.45:
        print("Equal time stop, depth: ", depth)
        try:
            return evaluation.evaluate(state, move), move
        except:
            return inf, move

    # Max player
    elif maxer == True:
        maxer = False
        value = -inf
        best_move = "None"
        Neighbors = ["up", "down", "left", "right"]

        # Find best move
        for option in Neighbors:
            # update snakes
            new_state = simulation.simulate(deepcopy(state), option)
            test_val, test_move = minimax(deepcopy(new_state), (depth - 1), option, maxer, alpha, beta)

            #To see if eating is done on depth
            if new_state["you"]["health"] == 100:
                test_val += 107
                if len(new_state["board"]["food"]) == 0:
                    #print("Last food boost")
                    #print("Option: ", option, "value: ", test_val)
                    test_val += 80

                # sees if enemy snake head is right by this depth
                test_val += is_near(new_state)


            alpha = max(test_val, alpha)
            if test_val > value:
                # print(str(test_val) + " > " + str(value))
                value = test_val
                best_move = option
            # print("\n")
            if test_val > beta:
                #print("beta prune: ", test_val, " > ", beta)
                break

        #print("This is move chosen by max call: " + str(best_move))
        #print("value: ", value, "prev  enemy move: ", move, " depth: ", depth, "\n")

        return value, best_move



    # Min player
    elif maxer == False:
        maxer = True
        value = inf
        best_move = "None"
        Neighbors = ["up", "down", "left", "right"]

        for option in Neighbors:
            new_state = simulation.simulate_opponent(state, option)
            test_val, test_move = minimax(deepcopy(new_state), (depth - 1), option, maxer, alpha, beta)

            if test_val < value:
                # print(str(test_val) + " < " + str(value))
                value = test_val
                best_move = option

            if test_val < alpha:
                #print("alpha prune: ", test_val, " < ", alpha)
                break
            beta = min(test_val, beta)
        #print("This is move chosen by min call: " + str(best_move))
        #print("value", value, "prev my move: ", move, " depth: ", depth)

        return value, best_move

def is_near(state):
    try:
        my_body = state["you"]["body"]
        my_head = my_body[0]
        is_near = 0
        x = my_head["x"]
        y = my_head["y"]
        my_length = state["you"]["length"]
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

        if [x + 1, y] == [enemy_x, enemy_y]:
            is_near = 1
        elif [x - 1, y] == [enemy_x, enemy_y]:
            is_near = 1
        elif [x, y + 1] == [enemy_x, enemy_y]:
            is_near = 1
        elif [x, y - 1] == [enemy_x, enemy_y]:
            is_near = 1

        if my_length > enemy_length + 1:
            value = is_near * 220
        elif my_length < enemy_length + 1:
            value = is_near * -500
        else:
            value = 0
    except:
        return 0

    return value

def panic_move(old_state):
    all_moves = ["up", "down", "left", "right"]
    board_width = old_state["board"]["width"]
    board_height = old_state["board"]["height"]

    for option in all_moves:
        evaluationValue = 0
        state = simulation.simulate(deepcopy(old_state), option)
        new_move = "right"
        new_eval = -9999
        my_body = state["you"]["body"]
        my_health = state["you"]["health"]
        my_head = my_body[0]
        snakeid = state["you"]["id"]
        allsnakes = state['board']['snakes']
        obstacles = []
        my_length = state["you"]["length"]
        # designed for 1v1's only
        for snake in allsnakes:
            if snake["id"] != snakeid:
                opponent = snake
                opponent_body = opponent["body"]
                opponent_head = opponent_body[0]
                enemy_x = opponent_head["x"]
                enemy_y = opponent_head["y"]
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

            if (x >= board_width) or (x < 0):
                # print("eval snake out of x bounds")
                evaluationValue = -9999  # we lose

            elif (y >= board_height) or (y < 0):
                # print("eval snake out of y bounds")
                evaluationValue = -9999  # we lose

            elif (enemy_x >= board_width) or (enemy_x < 0):
                # print("eval enemy snake out of x bounds")
                evaluationValue = 9999  # we win

            elif (enemy_y >= board_height) or (enemy_y < 0):
                # print("eval enemy snake out of y bounds")
                evaluationValue = 9999  # we win

            elif ([enemy_x, enemy_y] in obstacles):
                # print("eval enemy snake in obstacles")
                # print("enemy head:", opponent_head)
                # print("enemy calc head: ", [enemy_x, enemy_y])
                evaluationValue = 9999

            elif ([x, y] in obstacles):
                # print("eval snake in obstacles")
                evaluationValue = -9999

            elif ([x, y] == [enemy_x, enemy_y]):

                if my_length > enemy_length:
                    print("eval head on win")
                    evaluationValue = 9999
                elif my_length < enemy_length:
                    print("eval head on lose")
                    # not -inf so that snake does not give up
                    # enemy could mess up
                    evaluationValue = -600
                elif my_length == enemy_length:
                    print("eval head on tie")
                    evaluationValue = 0

            elif (my_health == 0):
                evaluationValue = -999

            else:
                x = my_head["x"]
                y = my_head["y"]
                enemy_x = opponent_head["x"]
                enemy_y = opponent_head["y"]
                dist = abs(x - enemy_x) + abs(y - enemy_y)
                evaluationValue += dist
        except:
            return "right"

        if evaluationValue > new_eval:
            new_move = option
            new_eval = evaluationValue

    return new_move

def measure_time(depth):
    move_end = default_timer()
    global move_start
    move_time = move_end - move_start
    if move_time > 0.4:
        print("Time stop, depth of: ", depth)
    return move_time


def is_terminal(state: typing.Dict, move_choice):
    # terminal_start = default_timer()
    dead = False

    my_body = state["you"]["body"]
    my_head = my_body[0]
    my_health = state["you"]["health"]
    snakeid = state["you"]["id"]
    allsnakes = state['board']['snakes']
    board_width = state["board"]["width"]
    board_height = state["board"]["height"]
    obstacles = []

    for snake in allsnakes:
        if snake["id"] != snakeid:
            opponent = snake
            opponent_body = opponent["body"]
            opponent_head = opponent_body[0]

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

        enemy_x, enemy_y = opponent_head["x"], opponent_head["y"]
        x, y = my_head["x"], my_head["y"]

        # test for death of either snake
        if (x >= board_width) or (x <= -1):
            # print(my_head["x"])
            dead = True
            # print("snake out of x bounds")
        elif (y >= board_height) or (y <= -1):
            dead = True
            # print("snake out of y bounds")
        elif (enemy_x >= board_width) or (enemy_x <= -1):
            dead = True
            # print("enemy snake out of x bounds")
        elif (enemy_y >= board_height) or (enemy_y <= -1):
            dead = True
            # print("ememy snake out of y bounds")
        elif ([x, y] in obstacles):
            dead = True
            # print("head in obstacles")
        elif ([enemy_x, enemy_y] in obstacles):
            dead = True
            # print("enemy head in obstacles")
        elif [x, y] == [enemy_x, enemy_y]:
            dead = True
            # print("head on collision")
        elif (my_health == 0):
            dead = True
    except:
        pass

    # terminal_end = default_timer()
    # time = (terminal_end - terminal_start) * 1000
    # print("is terminal run time: ", time)
    return dead


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({
        "info": info,
        "start": start,
        "move": move,
        "end": end
    })

'''
from sys import argv
port = "8000"
for i in range(len(sys.argv) - 1):
    if sys.argv[i] == '--port':
        port = sys.argv[i + 1]
    elif sys.argv[i] == '--seed':
        random_seed = int(sys.argv[i + 1])
run_server({"info": info, "start": start, "move": move, "end":   end, "port": port})


'''
