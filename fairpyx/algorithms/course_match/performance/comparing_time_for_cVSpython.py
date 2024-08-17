
import timeit  # Check performance of functions by running them many times
from fairpyx.instances import Instance
from fairpyx.allocations import AllocationBuilder
import sys
import numpy as np


# Function to make a budget
def make_budget(num_of_agents: int = 30, low: int = 2, high: int = 2.1, agent_name_template: str = "s{index}"):
    budget_list = np.random.uniform(low=low, high=high, size=num_of_agents)
    agents = [agent_name_template.format(index=i + 1) for i in range(num_of_agents)]
    budget = {agent: agent_budget for agent, agent_budget in zip(agents, budget_list)}
    return budget

# Function to make as allocation
def create_allocation(num_agents,item_capacity):
    random_instance = Instance.random_uniform(
        num_of_agents=num_agents,
        num_of_items=15,
        agent_capacity_bounds=[2, 3],
        item_capacity_bounds=[item_capacity, item_capacity],
        item_base_value_bounds=[1, 100],
        item_subjective_ratio_bounds=[0.5, 1.5],
        normalized_sum_of_values=100,
        random_seed=1)
    allocation = AllocationBuilder(random_instance)
    return allocation


num_agents =180
item_capacity =37
allocation1= create_allocation(num_agents=num_agents,item_capacity=item_capacity)
budget1 = make_budget(num_of_agents=num_agents)
allocation2= create_allocation(num_agents=num_agents,item_capacity=item_capacity)
budget2 = budget1.copy()

print(f"allocation1 {allocation1}")


cy = timeit.timeit('main_course_match_p.course_match_algorithm(allocation1, budget1)',
                   setup='import main_course_match_p',
                   number=1, globals=globals())
print(f'cy = {cy}')

sys.path.append('/home/naama/Studies/research-algo/Assig-4/course_match_algorithm/fairpyx/algorithms/course_match/')
py = timeit.timeit('main_course_match.course_match_algorithm(allocation2, budget2)',
                   setup='import main_course_match',
                   number=1, globals=globals())

print(f'py = {py}')





print(f'Cython is {py/cy} times faster')