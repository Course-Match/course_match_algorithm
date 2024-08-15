# cython: language_level=3

import logging
from fairpyx import Instance
from fairpyx import AllocationBuilder
from fairpyx.algorithms.course_match.A_CEEI import (
    compute_surplus_demand_for_each_course,
    find_best_schedule,
    find_preference_order_for_each_student,
)

logger = logging.getLogger(__name__)


# Declare variable types
cdef float epsilon
cdef dict price_vector, student_budgets
cdef object compute_surplus_demand_for_each_course_ref = compute_surplus_demand_for_each_course

cdef dict remove_oversubscription(
    allocation,
    dict price_vector,
    dict student_budgets,
    float epsilon=0.1,
    object compute_surplus_demand_for_each_course=compute_surplus_demand_for_each_course_ref
):
    """
    Perform oversubscription elimination to adjust course prices.
    """
    cdef float max_budget, d_star, low_price, high_price, p_mid, current_demand, highest_demand
    cdef dict excess_demands, item_conflicts, agent_conflicts
    cdef str highest_demand_course

    max_budget = max(student_budgets.values()) + epsilon
    logger.debug('Max budget set to %g', max_budget)
    
    item_conflicts = {
        item: allocation.instance.item_conflicts(item)
        for item in allocation.instance.items
    }
    
    agent_conflicts = {
        agent: allocation.instance.agent_conflicts(agent)
        for agent in allocation.instance.agents
    }

    preferred_schedule = find_preference_order_for_each_student(
        allocation.instance._valuations,
        allocation.instance._agent_capacities,
        item_conflicts,
        agent_conflicts,
    )
    
    while True:
        excess_demands = compute_surplus_demand_for_each_course(price_vector, allocation, student_budgets, preferred_schedule)
        highest_demand_course = max(excess_demands, key=excess_demands.get)
        highest_demand = excess_demands[highest_demand_course]
        logger.debug('Highest demand course: %s with demand %g', highest_demand_course, highest_demand)
        
        if highest_demand <= 0:
            break

        d_star = highest_demand / 2
        low_price = price_vector[highest_demand_course]
        high_price = max_budget

        logger.info('Starting binary search for course %s', highest_demand_course)
        
        while high_price - low_price >= epsilon:
            p_mid = (low_price + high_price) / 2
            price_vector[highest_demand_course] = p_mid
            current_demand = compute_surplus_demand_for_each_course(price_vector, allocation, student_budgets, preferred_schedule)[highest_demand_course]
            logger.debug('Mid price set to %g, current demand %g', p_mid, current_demand)
            
            if current_demand > d_star:
                low_price = p_mid
                logger.debug('Current demand %g is greater than d_star %g, updating low_price to %g', current_demand, d_star, low_price)
            else:
                high_price = p_mid
                logger.debug('Current demand %g is less than or equal to d_star %g, updating high_price to %g', current_demand, d_star, high_price)

        price_vector[highest_demand_course] = high_price
        logger.info('Final price for course %s set to %g', highest_demand_course, high_price)
    
    logger.info('Final price vector after remove_oversubscription %s', price_vector)
    
    return price_vector

if __name__ == "__main__":
    import doctest
    print(doctest.testmod())

    instance = Instance(
        agent_capacities={"Alice": 2, "Bob": 2, "Tom": 2},
        item_capacities={"c1": 1, "c2": 1, "c3": 1},
        valuations={
            "Alice": {"c1": 50, "c2": 20, "c3": 80},
            "Bob": {"c1": 60, "c2": 40, "c3": 30},
            "Tom": {"c1": 70, "c2": 30, "c3": 70},
        },
    )
    allocation = AllocationBuilder(instance)
    price_vector = {"c1": 1.2, "c2": 0.9, "c3": 1}
    epsilon = 0.1
    student_budgets = {"Alice": 2.2, "Bob": 2.1, "Tom": 2.0}

    print(remove_oversubscription(allocation, price_vector, student_budgets, epsilon, compute_surplus_demand_for_each_course))
