import random
from game.utils import Location
from typing import List, Callable


def connect_locations(locations: List[Location], connect: Callable[[Location, Location], None]):
    """
    You are given a list of locations that you must connect together using the `connect` function.
    To check whether connecting two locations requires building a bridge, use the `need_bridge_to_connect` function.
    Calling connect multiple times with the same locations is idempotent.
    """

    # Code to connect every point with each other.
    # This solution is not optimal at all because it uses too much resources.
    for loc_1 in locations:
        for loc_2 in locations:
            if loc_1 != loc_2 and random.randint(0, 9) == 1:
                connect(loc_1, loc_2)
