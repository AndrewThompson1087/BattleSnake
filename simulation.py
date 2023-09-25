import typing
from copy import deepcopy
import timeit

# Code for simulating a snake's move
# by Charles Raines

# Function to take a snake head and move it to a new coordinate
def move_snake_head(current_head: typing.Dict, move):
  new_head = deepcopy(current_head)

  if move == "up":
    new_head["y"] += 1
  elif move == "down":
    new_head["y"] -= 1
  elif move == "left":
    new_head["x"] -= 1
  elif move == "right":
    new_head["x"] += 1

  return new_head

# Function to take a snake's new head and body and adjust the values
def move_snake(new_head: typing.Dict, snake_body: typing.Dict, ate_food):
  new_body = deepcopy(snake_body)

  n = len(new_body) - 1
  while n > 0:
    new_body[n] = new_body[n - 1]
    n -= 1
  
  new_body[0] = new_head

  if ate_food:
    tail = snake_body[-1]
    new_body.append(tail)

  return new_body


# This function will take in a state and a move and return a new state
# for my snake
def simulate(state: typing.Dict, move):
  #sim_start = timeit.default_timer()
  # Variable Assignments
  new_state = deepcopy(state)
  my_body = state["you"]["body"]
  head = deepcopy(my_body[0])
  food_index = 0

  # Static Adjusted Values
  new_state["turn"] += 1
  new_state["you"]["health"] -= 1
  
  new_head = move_snake_head(deepcopy(head), move)

  # Boolean Objects
  ate_food = 0

  for i in range(len(new_state["board"]["food"])):
    if new_state["board"]["food"][i] == new_head:
      food_index = i
      ate_food = 1

  if ate_food:
    new_state["board"]["food"].pop(food_index)
    new_state["you"]["length"] += 1
    new_state["you"]["health"] = 100

  
  new_state["you"]["body"] = move_snake(deepcopy(new_head), deepcopy(my_body), ate_food)

  #sim_end = timeit.default_timer()
  #sim_time = (sim_end - sim_start) * 1000
  #print("simulation time: ", sim_time)
  return new_state

# This function is exactly identical to the simulate function, but this
# will be used to evaluate from the opponent's point of view
def simulate_opponent(state: typing.Dict, move):
  #en_sim_start = timeit.default_timer()
  # Variable Assignments
  new_state = deepcopy(state)
  
  snakeid = state["you"]["id"]

  # figure out the opponent's body (should be index 0, but sanity check)
  for i in range(len(new_state["board"]["snakes"])):
    if new_state["board"]["snakes"][i]["id"] != snakeid:
      snake_index = i
  
  # Continued Variable Assignments
  try:
    head = deepcopy(state["board"]["snakes"][snake_index]["body"][0])
  except:
    pass
  food_index = 0

  # Static Adjusted Values
  new_state["turn"] += 1
  try:
    new_state["board"]["snakes"][snake_index]["health"] -= 1
    new_head = move_snake_head(head, move)
  except:
    pass
  


  # Boolean Objects
  ate_food = 0
  try:
    for i in range(len(new_state["board"]["food"])):
      if new_state["board"]["food"][i] == new_head:
        food_index = i
        ate_food = 1
  
    if ate_food:
      new_state["board"]["food"].pop(food_index)
      new_state["board"]["snakes"][snake_index]["length"] += 1
      new_state["board"]["snakes"][snake_index]["health"] = 100
  
    new_state["board"]["snakes"][snake_index]["body"] = move_snake(deepcopy(new_head), deepcopy(state["board"]["snakes"][snake_index]["body"]), ate_food)
  
    #en_sim_end = timeit.default_timer()
    #en_sim_time = (en_sim_end - en_sim_start) * 1000
    #print("enemy simulation time: ", en_sim_time)
  except:
    pass
  return new_state
