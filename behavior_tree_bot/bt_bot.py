#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn

"""
Basic theory: More ships = good
More planets controlled = more ships
Define an early strategy, and then maybe pivot to a mid/late game strategy 
EARLY:
Find the lowest cost neutral planets (that aren't too far away)
Capture the planet with ships when possible, move on to another planet
Once we have enough neutral planets, (maybe like 10, or a percentage of the total #) initiate MidGame
MID:
Redistribution - If one planet has more resources than the next biggest planet, redistribute to either
A: a planet with not many resources
B: a planet that is closer to an enemy planet
Send in small increments (frequently)
Might also want to maintain a minimum for when this behavior starts(maybe like 100+)
Attack - Overwhelm or Siege
Overwhelm: Send one big group to a planet
"""

# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')

    offensive_plan = Sequence(name='Offensive Strategy')
    largest_fleet_check = Check(have_largest_fleet)
    attack = Action(attack_weakest_enemy_planet)
    offensive_plan.child_nodes = [largest_fleet_check, attack]

    spread_sequence = Sequence(name='Spread Strategy')
    neutral_planet_check = Check(if_neutral_planet_available)
    spread_action = Action(spread_to_weakest_neutral_planet)
    spread_sequence.child_nodes = [neutral_planet_check, spread_action]

    build_economy = Selector(name='Colonizaition Strategy')
    marshal_forces = Action(consolidate_ships)
    deploy_forces = Action(capture_neighbors)
    build_economy.child_nodes = [deploy_forces, marshal_forces]

    destroy_enemy = Sequence(name='Finisher Strategy')
    last_enemy_check = Check(is_final_enemy_base)
    kill_action = Action(finish_off)
    destroy_enemy.child_nodes = [last_enemy_check, kill_action]

    root.child_nodes = [destroy_enemy, offensive_plan, build_economy]

    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
