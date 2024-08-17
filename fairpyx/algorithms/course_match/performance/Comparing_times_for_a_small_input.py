
import timeit  # Check performance of functions by running them many times
from fairpyx.instances import Instance
from fairpyx.allocations import AllocationBuilder

instance = Instance(
    agent_conflicts={"A": [], "B": [], "C": [], "D": [], "E": [], "F": [], "G": [], "H": [], "I": [], "J": []},
    item_conflicts={"c1": [], "c2": [], "c3": [], "c4": [], "c5": [], "c6": [], "c7": [], "c8": [], "c9": [], "c10": []},
    agent_capacities={"A": 2, "B": 2, "C": 2, "D": 2, "E": 2, "F": 2, "G": 2, "H": 2, "I": 2, "J": 2},
    item_capacities={"c1": 2, "c2": 2, "c3": 2, "c4": 2, "c5": 2, "c6": 2, "c7": 2, "c8": 2, "c9": 2, "c10": 2},
    valuations={"A": {"c1": 100, "c2": 100, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "B": {"c1": 100, "c2": 100, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "C": {"c1": 0, "c2": 0, "c3": 100, "c4": 100, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "D": {"c1": 0, "c2": 0, "c3": 100, "c4": 100, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "E": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 100, "c6": 100, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "F": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 100, "c6": 100, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "G": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 100, "c8": 100, "c9": 0, "c10": 0},
                "H": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 100, "c8": 100, "c9": 0, "c10": 0},
                "I": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 100, "c10": 100},
                "J": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 100, "c10": 100}})

budget = {"A": 100.1, "B": 100.2, "C": 100.3, "D": 100.4, "E": 100.5, "F": 100.6, "G": 100.7, "H": 100.8, "I": 100.9, "J": 100.11}
allocation = AllocationBuilder(instance)
import sys
sys.path.append('/home/naama/Studies/research-algo/Assig-4/course_match_algorithm/fairpyx/algorithms/course_match/')
cy = timeit.timeit('main_course_match_p.course_match_algorithm(allocation, budget)',
                   setup='import main_course_match_p',
                   number=1, globals=globals())


instance = Instance(
    agent_conflicts={"A": [], "B": [], "C": [], "D": [], "E": [], "F": [], "G": [], "H": [], "I": [], "J": []},
    item_conflicts={"c1": [], "c2": [], "c3": [], "c4": [], "c5": [], "c6": [], "c7": [], "c8": [], "c9": [], "c10": []},
    agent_capacities={"A": 2, "B": 2, "C": 2, "D": 2, "E": 2, "F": 2, "G": 2, "H": 2, "I": 2, "J": 2},
    item_capacities={"c1": 2, "c2": 2, "c3": 2, "c4": 2, "c5": 2, "c6": 2, "c7": 2, "c8": 2, "c9": 2, "c10": 2},
    valuations={"A": {"c1": 100, "c2": 100, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "B": {"c1": 100, "c2": 100, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "C": {"c1": 0, "c2": 0, "c3": 100, "c4": 100, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "D": {"c1": 0, "c2": 0, "c3": 100, "c4": 100, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "E": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 100, "c6": 100, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "F": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 100, "c6": 100, "c7": 0, "c8": 0, "c9": 0, "c10": 0},
                "G": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 100, "c8": 100, "c9": 0, "c10": 0},
                "H": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 100, "c8": 100, "c9": 0, "c10": 0},
                "I": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 100, "c10": 100},
                "J": {"c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 0, "c6": 0, "c7": 0, "c8": 0, "c9": 100, "c10": 100}})

budget = {"A": 100.1, "B": 100.2, "C": 100.3, "D": 100.4, "E": 100.5, "F": 100.6, "G": 100.7, "H": 100.8, "I": 100.9, "J": 100.11}
allocation = AllocationBuilder(instance)

py = timeit.timeit('main_course_match.course_match_algorithm(allocation, budget)',
                   setup='import main_course_match',
                   number=1, globals=globals())



print(f'cy = {cy}')
print(f'py = {py}')
print(f'Cython is {py/cy} times faster')