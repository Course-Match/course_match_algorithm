"""
Course Match: A Large-Scale Implementation ofApproximate Competitive Equilibrium fromEqual Incomes for Combinatorial Allocation,
by Eric Budish, Gérard P. Cachon, Judd B. Kessler, Abraham Othman
June 2, 2016
https://pubsonline.informs.org/doi/epdf/10.1287/opre.2016.1544

Programmer: Naama Shiponi and Ben Dabush
Date: 1/6/2024
"""
import logging
import random
import time
import numpy as np
from fairpyx import Instance, AllocationBuilder
from itertools import combinations


# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


"""
Algorithm 1: Approximate Competitive Equilibrium from Equal Incomes (A-CEEI), finds the best price vector that matches student preferences and course capacities.
"""
cpdef dict A_CEEI(alloc ,dict budget ,int time_limit  = 60, seed = None) :
    logger.info("Starting A_CEEI algorithm with budget=%s and time limit %d.",budget, time_limit)
   

    cdef float best_error = float('inf')
    cdef dict best_price_vector = dict()
    start_time = time.time()
    cdef list steps = [0.1, 0.2, 0.3, 0.4, 0.5]  # Example step sizes, can be adjusted
    cdef dict price_vector 
    cdef float search_error 
    cdef int c
    cdef list neighbors
    cdef dict next_price_vector
    cdef list tabu_list = []
    cdef dict next_demands 
    cdef float current_error 

    cdef dict preferred_schedule = find_preferred_schedule_adapter(alloc)
    logger.debug("Calling find_preference_order_for_each_student %s",preferred_schedule)
    while time.time() - start_time < time_limit :
        if seed:
            seed+=1        
            random.seed(seed)
        price_vector = {k: random.uniform(0, max(budget.values())) for k in alloc.instance.items}

        search_error = alpha(compute_surplus_demand_for_each_course(price_vector, alloc, budget, preferred_schedule))
        logger.debug("Initial search on _random_ price_ %s error: %f",price_vector, search_error)

        c = 0
        while c < 5:
            neighbors = find_neighbors(price_vector, alloc, budget, steps, preferred_schedule)
            logger.debug("Found %d neighbors : %s", len(neighbors), neighbors)
            
            while neighbors:
                next_price_vector = neighbors.pop(0)
                next_demands = compute_surplus_demand_for_each_course(next_price_vector, alloc, budget, preferred_schedule)

                if next_demands not in tabu_list:
                    break
 
            if not neighbors: #if there are neighbors is empty
                logger.debug("all the demand neighbors in tabu_list, break while c<5, tabu_list: %s", tabu_list)
                c = 5
            else:
                price_vector = next_price_vector
                tabu_list.append(next_demands)
                current_error = alpha(next_demands)
                logger.debug("fond neighber so the next price vector is: %s,demands = %s", next_price_vector,next_demands)
                if current_error < search_error:
                    logger.debug("Current error: %f, < Search error: %f soo c = 0", current_error, search_error)

                    search_error = current_error
                    c = 0
                else:
                    c += 1
                    logger.debug("Current error: %f, => Search error: %f soo c = %d", current_error, search_error,c)

                if current_error < best_error:
                    logger.info("New best_price_vector is %s, best error: %f ", price_vector, current_error)
                    best_error = current_error
                    best_price_vector = price_vector
                    if best_error == 0:
                        break
    logger.info("A-CEEI algorithm completed. Best price vector: %s with error: %f", best_price_vector, best_error)      
    return best_price_vector
cpdef is_valid_schedule(dict schedule,dict item_conflicts,dict agent_conflicts,str agent):
    # Check item conflicts
    for item, conflicts in item_conflicts.items():
        if schedule.get(item, 0) == 1:
            for conflicted_item in conflicts:
                if schedule.get(conflicted_item, 0) == 1:
                    return False
    # Check agent conflicts
    for conflicted_item in agent_conflicts.get(agent, []):
        if schedule.get(conflicted_item, 0) == 1:
            return False
    return True


cpdef list generate_all_schedules(list items,int capacity ,dict item_conflicts,dict agent_conflicts,str agent):
    cdef list all_schedules = []
    cdef dict schedule_dict 
    for num_courses_per_agent in range(1, capacity + 1):
        for schedule in combinations(items, num_courses_per_agent):
            schedule_dict = {item: 1 if item in schedule else 0 for item in items}
            if is_valid_schedule(schedule_dict, item_conflicts, agent_conflicts, agent):
                all_schedules.append(schedule_dict)
    return all_schedules


cpdef dict find_preference_order_for_each_student(dict valuations,dict agent_capacities,dict item_conflicts,dict agent_conflicts):   
    cdef dict preferred_schedules = dict()
    cdef list items 
    cdef int capacity
    cdef list all_schedules
    cdef dict schedule_valuations  = dict()
    cdef int total_valuation
    cdef list sorted_schedules

    for agent in agent_capacities.keys():
        items = list(valuations[agent].keys())
        capacity = int(agent_capacities[agent])
        all_schedules = generate_all_schedules(items, capacity, item_conflicts, agent_conflicts, agent)
        logger.debug("All schedules for agent %s: %s", agent, all_schedules)
        # Calculate valuations for valid schedules
        schedule_valuations = dict()
        for schedule in all_schedules:
            total_valuation = sum(valuations[agent][item] for item in schedule if schedule[item] == 1)
            schedule_valuations[total_valuation] = schedule_valuations.get(total_valuation, [])
            schedule_valuations[total_valuation].append([schedule[item] for item in items])
        # Sort the schedules by total valuation in descending order
        sorted_valuations = sorted(schedule_valuations.keys(), reverse=True)

        for val in sorted_valuations:
            if len(schedule_valuations.get(val)) > 1:
                schedule_valuations[val] = sorted(schedule_valuations.get(val), key=lambda x: sum(x), reverse=True)

        # Collect sorted schedules
        sorted_schedules = []

        for val in sorted_valuations:
            for schedule in schedule_valuations.get(val):
                sorted_schedules.append(schedule)

        preferred_schedules[agent] = sorted_schedules
    return preferred_schedules



cpdef dict compute_surplus_demand_for_each_course(dict price_vector ,alloc, dict budget,dict preferred_schedule):
    cdef list best_schedules = find_best_schedule(price_vector, budget, preferred_schedule)
    sol = np.sum(np.array(best_schedules), axis=0)
    # Convert item capacities to a list
    cdef list item_capacities_list = [alloc.instance.item_capacity(name_item) for name_item in alloc.instance.items]

    # Convert item capacities list to a numpy array
    item_capacities_array = np.array(item_capacities_list)

    # Perform the subtraction
    cdef dict result = {name_item: int(sol[i] - item_capacities_array[i]) for i, name_item in enumerate(alloc.instance.items)}
    return result
       

cpdef list find_best_schedule(dict price_vector,dict budget ,dict preferred_schedule):    
    cdef list best_schedule = []
    cdef int cuont = 0
    cdef list sum_of_courses 
    price_array = np.array([price_vector[key] for key in price_vector.keys()])
    for student, schedule in preferred_schedule.items():
        best_schedule.append(np.zeros(len(price_vector)))
        sum_of_courses = [i for i in np.sum(schedule * price_array[:, np.newaxis].T, axis=1)]
        for i in range(len(sum_of_courses)):
            if sum_of_courses[i] <= budget[student]:
                best_schedule[cuont] = schedule[i]
                break
        cuont += 1
    return best_schedule
               
        
cpdef float alpha(dict demands):
    result = np.sqrt(sum([v**2 for v in demands.values()]))
    return result


cpdef list find_neighbors(dict price_vector ,alloc, dict budget, list steps ,dict preferred_schedule):    
    cdef dict demands = compute_surplus_demand_for_each_course(price_vector, alloc, budget, preferred_schedule)
    cdef list list_of_neighbors = generate_gradient_neighbors(price_vector, demands, steps)
    list_of_neighbors.extend(generate_individual_adjustment_neighbors(price_vector, alloc, demands, budget, preferred_schedule))

    #sort list_of_neighbors dict values by alpha
    cdef list sorted_neighbors = sorted(list_of_neighbors, key=lambda neighbor: alpha(compute_surplus_demand_for_each_course(neighbor, alloc, budget, preferred_schedule)))
    return sorted_neighbors


cpdef list generate_individual_adjustment_neighbors(dict price_vector, alloc, dict demands, dict budget, dict preferred_schedule):
    cdef float step=0.1
    cdef list eighbors = []
    cdef dict new_price_vector
    cdef list neighbors  = []
    cdef dict new_demands 
    cdef int count=0
    for k in demands.keys():
        if demands[k] == 0:
            continue
        new_price_vector = price_vector.copy()
        new_demands = demands.copy()
        count=0
        if demands[k] > 0:
            while (demands == new_demands) :
                new_price_vector.update({k: new_price_vector[k] + step})
                new_demands = compute_surplus_demand_for_each_course(new_price_vector, alloc, budget, preferred_schedule)
                count+=1
        elif demands[k] < 0:
            new_price_vector.update({k: 0.0})
            new_demands = compute_surplus_demand_for_each_course(new_price_vector, alloc, budget, preferred_schedule)

        neighbors.append(new_price_vector.copy())  # Ensure to append a copy

    return neighbors

cpdef list generate_gradient_neighbors(dict price_vector,dict demands,list steps):
    cdef list neighbors = []
    cdef dict new_price_vector = dict()
    for step in steps:
        new_price_vector = dict()
        for k,p in price_vector.items():
            new_price_vector[k] = max(0.0, p + (step * demands[k]))

        neighbors.append(new_price_vector)
    return neighbors  

cpdef dict find_preferred_schedule_adapter(alloc):
    cdef dict item_conflicts={item:  alloc.instance.item_conflicts(item) for item in alloc.instance.items}
    cdef dict agent_conflicts={agent:  alloc.instance.agent_conflicts(agent) for agent in alloc.instance.agents}
    return find_preference_order_for_each_student(alloc.instance._valuations , alloc.instance._agent_capacities , item_conflicts , agent_conflicts)

if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
    # instance = Instance(
    # agent_conflicts = {"Alice": [], "Bob": [], "Tom": []},
    # item_conflicts = {"c1": [], "c2": [], "c3": []},
    # agent_capacities = {"Alice": 1, "Bob": 1, "Tom": 1}, 
    # item_capacities  = {"c1": 1, "c2": 1, "c3": 1},
    # valuations = {"Alice": {"c1": 100, "c2": 0, "c3": 0},
    #         "Bob": {"c1": 0, "c2": 100, "c3": 0},
    #         "Tom": {"c1": 0, "c2": 0, "c3": 100}
    # })
    # budget = {"Alice": 1.0, "Bob": 1.1, "Tom": 1.3}    
    # allocation = AllocationBuilder(instance)
    # print(A_CEEI(allocation, budget))


