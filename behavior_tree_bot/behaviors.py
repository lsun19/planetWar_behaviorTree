import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from math import ceil

def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def consolidate_ships(state):
    """
    This function consolidates ships from lower tier planets to higher tier planets within a player's own territory,
    while ensuring that each planet retains a base level of defense proportional to its tier.
    """

    # The base level of defense is determined as X times the planet's production capability
    modifier_planet_defense = 15
    # A threshold to determine if a planet has an excess of ships, set as X times the planet's production
    modifier_planet_spares = 20

    # Sort player's planets by their growth rate to prioritize lower tier planets
    player_planets = sorted(state.my_planets(), key=lambda t: t.growth_rate)

    # If there is only one or no planet, no consolidation is needed
    if len(player_planets) < 2:
        return False

    # The highest tier planet is considered the player's home planet
    player_home = player_planets[-1]
    # Exclude the home planet from the list of planets to evaluate for ship consolidation
    player_planets = player_planets[:-1]

    # Identify planets currently targeted by enemy fleets
    planets_under_attack = set([fleet.destination_planet for fleet in state.enemy_fleets()])

    # Iterate over all owned planets except the home planet, starting with the lowest tier
    for planet in player_planets:
        # Only consider planets not under attack and with a surplus of ships
        if planet.ID not in planets_under_attack and (planet.growth_rate * modifier_planet_spares) < planet.num_ships:
            # Calculate the number of ships to transfer, ensuring the planet retains its base level of defense
            transfer_size = planet.num_ships - (planet.growth_rate * modifier_planet_defense)

            # Issue the order to transfer ships from the current planet to the home planet
            return issue_order(state, planet.ID, player_home.ID, transfer_size)

    # If no planet has spare ships according to the criteria, do not issue any transfer orders
    return False



def capture_neighbors(state):
    """
    This function is designed to secure planets that are close to the player's strongest planet, emphasizing strategic
    expansion by prioritizing nearby planets based on various factors including productivity, defense, and enemy
    occupation.
    """

    # Sets the maximum distance to consider for neighboring planets
    modifier_neighbor_distance = 20
    # Determines how much more valuable more productive planets are compared to less productive ones
    modifier_neighbor_production = 2

    # Modifies the consideration of a planet's defense in planning to capture it, with higher values requiring a larger
    # numerical advantage
    modifier_neighbor_defense = 1.3

    # Increases the priority of targeting planets currently owned by an enemy
    modifier_neighbor_enemy = 1.3

    # Finds the player's strongest planet by number of ships to use as a base for operations
    home_planet = max(state.my_planets(), key=lambda t: t.num_ships)

    # Exits the function if the player does not control any planets
    if not home_planet:
        return False

    # Compiles a list of planets already being targeted by the player's and enemy's fleets
    targeted_planets = set([fleet.destination_planet for fleet in state.my_fleets()])
    enemy_targeted_planets = set([fleet.destination_planet for fleet in state.enemy_fleets()])
    if enemy_targeted_planets:
        targeted_planets = targeted_planets | enemy_targeted_planets

    # Defines a function to calculate the desirability of a planet based on various factors
    def planet_val(planet):
        # Excludes planets that cannot be captured with the current fleet
        if (modifier_neighbor_defense * planet.num_ships) > home_planet.num_ships:
            return -1

        # Calculates value based on distance, production, defense, and enemy presence
        dist_val = modifier_neighbor_distance / state.distance(home_planet.ID, planet.ID)
        prod_val = modifier_neighbor_production * planet.growth_rate
        defs_val = home_planet.num_ships / (expected_fleet(state, home_planet, planet) * modifier_neighbor_defense)
        enem_val = modifier_neighbor_enemy

        return (dist_val + prod_val + defs_val + enem_val)

    # Filters and sorts neighboring planets by their calculated value, ignoring those already targeted
    neighbor_planets = [planet for planet in state.not_my_planets() if planet.ID not in targeted_planets]
    neighbor_planets = sorted(neighbor_planets, key=lambda t: planet_val(t), reverse=True)

    # Attempts to capture the most valuable neighboring planet, considering the player's available resources
    for neighbor in neighbor_planets:
        garrison = 0
        required_fleet = (expected_fleet(state, home_planet, neighbor) +
                          ceil(state.distance(home_planet.ID, neighbor.ID)))

        if home_planet.ID in enemy_targeted_planets:
            garrison = sum([ fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet ==
                             home_planet.ID ])

        if home_planet.num_ships > required_fleet + garrison:
            return issue_order(state, home_planet.ID, neighbor.ID, required_fleet)
        else:
            return False

    return False

def finish_off(state):
    """
    This function aims to finish an enemy off when they are reduced to a single planet, coordinating an attack from
    nearby friendly planets.
    """

    # Checks if the enemy controls any planets
    enemy_planet = any(state.enemy_planets())

    if enemy_planet:
        # Sorts friendly planets by their proximity to the enemy planet
        local_friendlies = sorted(state.my_planets(), key=lambda t: state.distance(enemy_planet.ID, t.ID))
        for local in local_friendlies:
            # Calculates the number of ships to keep as a defensive garrison
            garrison = expected_fleet(state, enemy_planet, local) + 1
            if local.num_ships - garrison > expected_fleet(state, local, enemy_planet) + 1:
                # Issues an order to attack the enemy planet with the surplus ships
                return issue_order(state, local.ID, enemy_planet.ID, local.num_ships - garrison)

        # If no friendly planet can safely attack, no action is taken
        return False

    # If the enemy has no planets but still has fleets, prepares to reinforce planets under threat
    enemy_fleets = sorted(state.enemy_fleets(), key=lambda f: f.num_ships, reverse=True)
    if enemy_fleets:
        enemy_targets = set(f.destination_planets for f in enemy_fleets)

        for fleet in enemy_fleets:
            target_planet = state.planets[fleet.destination_planet]
            # Checks if the targeted planet can withstand the incoming attack
            target_defence = target_planet.num_ships + (target_planet.growth_rate * fleet.turns_remaining)
            if target_defence >= fleet.num_ships:
                continue  # The target can defend itself without reinforcement

            # If the target is likely to fall, sends reinforcement from the nearest friendly planet not already targeted
            local_friendlies = sorted(state.my_planets(),key=lambda f: state.distance(target_planet.ID, t.ID),reverse=True)
            local_friendlies = local_friendlies[1:]  # Excludes the target planet itself

            for local in local_friendlies:
                if local.ID not in enemy_targets:
                    return issue_order(state, local.ID, target_planet.ID, local.num_ships - 1)

    # If no friendly planets are under immediate threat, no action is taken
    return False

def expected_fleet(state, source, destination):
    """
    Calculates the expected number of ships that a friendly fleet will encounter upon arriving at a destination planet,
    taking into account the travel time and the growth rate of the destination planet, assuming it is owned and thus
    capable of producing additional ships during the fleet's transit.
    """

    # Initializes variable to track growth in ship numbers during fleet travel
    travel_growth = 0
    # If the destination planet is owned (not neutral), it will generate ships over time
    if destination.owner != 0:
        # Calculates the number of ships produced during travel based on the distance and growth rate
        travel_growth = state.distance(source.ID, destination.ID) * destination.growth_rate

    # Returns the total expected number of ships at the destination upon fleet arrival
    return destination.num_ships + travel_growth
