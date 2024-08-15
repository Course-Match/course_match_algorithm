"""
Course Match: A Large-Scale Implementation of Approximate Competitive Equilibrium from Equal Incomes for Combinatorial Allocation
Eric Budish, Gérard P. Cachon, Judd B. Kessler, Abraham Othman
June 2, 2016
https://pubsonline.informs.org/doi/epdf/10.1287/opre.2016.1544

Naama Shiponi and Ben Dabush
1/6/2024
"""
import cython
import logging
logger = logging.getLogger(__name__)
from fairpyx.algorithms.course_match.A_CEEI import (
    compute_surplus_demand_for_each_course,
    find_best_schedule,
    find_preference_order_for_each_student,
)
from fairpyx.instances import Instance
from fairpyx.allocations import AllocationBuilder

"""
Algorithm 3: The algorithm is designed to refill all the courses that, following Algorithm 2, have space in them.
"""

cdef tuple calculate_conflicts(allocation: AllocationBuilder):
    cdef dict item_conflicts = {
        item: allocation.instance.item_conflicts(item)
        for item in allocation.instance.items
    }
    cdef dict agent_conflicts = {
        agent: allocation.instance.agent_conflicts(agent)
        for agent in allocation.instance.agents
    }
    
    logger.debug('Calculated item conflicts: %s', item_conflicts)
    logger.debug('Calculated agent conflicts: %s', agent_conflicts)
    return item_conflicts, agent_conflicts


cdef dict create_dictionary_of_schedules(list student_schedule, list course, list students):
    cdef dict schedule_dict = {student: [course for j, course in enumerate(course) if student_schedule[i][j] == 1] for i, student in enumerate(students)}
    logger.debug('Created dictionary of schedules: %s', schedule_dict)
    return schedule_dict


cdef list calculate_remaining_budgets(dict price_vector, dict student_budgets, dict student_courses, list priorities_student_list, alloc: AllocationBuilder):
    cdef list remaining_budgets = []
    cdef str student
    cdef list courses
    cdef float total_cost, remaining_budget
    cdef dict priority_dict
    cdef int priority_index
    for student, courses in student_courses.items():
        total_cost = sum(price_vector[course] for course in courses)
        remaining_budget = student_budgets[student] - total_cost
        remaining_budgets.append((student, remaining_budget))
        logger.debug('Student %s, Courses: %s, Total Cost: %f, Remaining Budget: %f', student, courses, total_cost, remaining_budget)
    
    if len(priorities_student_list) == 0:
        priorities_student_list = [[agent for agent in alloc.remaining_agents()]]
    priority_dict = {}
    for priority_index, group in enumerate(priorities_student_list):
        for student in group:
            priority_dict[student] = priority_index
    
    remaining_budgets.sort(key=lambda x: (priority_dict[x[0]], x[1]))

    logger.debug('Calculated remaining budgets: %s', remaining_budgets)
    return remaining_budgets


cdef dict reoptimize_student_schedules(allocation: AllocationBuilder, dict price_vector, list student_list, dict student_budgets, dict student_schedule_dict, dict capacity_undersubscribed_courses):
    cdef bint not_done = True
    cdef str student
    cdef list current_bundle, new_bundle
    cdef dict student_budget
    while not_done and len(capacity_undersubscribed_courses) != 0:
        not_done = False
        for student in student_list:
            current_bundle = list(student_schedule_dict[student[0]])
            current_bundle.extend(x for x in list(capacity_undersubscribed_courses.keys()) if x not in current_bundle)
            current_bundle.sort()
            student_budget = {student[0]: 1.1 * student_budgets[student[0]]}
            new_bundle = allocation_function(allocation, student[0], current_bundle, price_vector, student_budget)
            if is_new_bundle_better(allocation, student[0], student_schedule_dict[student[0]], new_bundle.get(student[0], {})):
                not_done = True
                update_student_schedule_dict(student, student_schedule_dict, new_bundle, capacity_undersubscribed_courses)
                logger.debug('Updated student %s schedule: %s', student[0], student_schedule_dict[student[0]])
                break  # Only one student changes their allocation in each pass
    logger.info("Finished reoptimization of student schedules %s",student_schedule_dict)    
    return student_schedule_dict


cdef void update_student_schedule_dict(tuple student, dict student_schedule_dict, dict new_bundle, dict capacity_undersubscribed_courses):
    cdef list diff_in_bundle = list(set(new_bundle.get(student[0])).symmetric_difference(set(student_schedule_dict[student[0]])))
    cdef str course
    for course in diff_in_bundle:
        if course in student_schedule_dict[student[0]]:
            capacity_undersubscribed_courses[course] = capacity_undersubscribed_courses.get(course, 0) + 1
        else:
            capacity_undersubscribed_courses[course] -= 1
            if capacity_undersubscribed_courses[course] == 0:
                capacity_undersubscribed_courses.pop(course)
    student_schedule_dict.update({student[0]: new_bundle.get(student[0])})
    logger.debug('Updated undersubscribed course capacities: %s', capacity_undersubscribed_courses)


cdef dict allocation_function(allocation: AllocationBuilder, str student, dict student_allocation, dict price_vector, dict student_budget):
    cdef dict limited_student_valuations = filter_valuations_for_courses(allocation, student, student_allocation)
    cdef dict item_conflicts, agent_conflicts
    item_conflicts, agent_conflicts = calculate_conflicts(allocation)
    cdef dict agent_capacities = {student: allocation.instance._agent_capacities[student]}
    cdef dict preferred_schedule = find_preference_order_for_each_student(limited_student_valuations, agent_capacities, item_conflicts, agent_conflicts)
    cdef dict limited_price_vector = {course: price for course, price in price_vector.items() if course in student_allocation}
    cdef dict new_allocation = find_best_schedule(limited_price_vector, student_budget, preferred_schedule)
    cdef dict new_allocation_dict = create_dictionary_of_schedules(new_allocation, student_allocation, agent_capacities.keys())
    logger.debug('Reoptimized schedule for student %s: %s', student, new_allocation_dict)
    return new_allocation_dict


cdef dict filter_valuations_for_courses(allocation: AllocationBuilder, str student, dict student_allocation):
    cdef dict filtered_valuations = {
        student: {
            course: valuations
            for course, valuations in allocation.instance._valuations.get(
                student, {}
            ).items()
            if course in student_allocation
        }
    }
    logger.debug('Filtered valuations for student %s: %s', student, filtered_valuations)
    return filtered_valuations


cdef bint is_new_bundle_better(allocation: AllocationBuilder, str student, set current_bundle, set new_bundle):
    cdef float sum_valuations_cur = sum(valuations for course, valuations in allocation.instance._valuations.get(student, {}).items() if course in current_bundle)
    cdef float sum_valuations_new = sum(valuations for course, valuations in allocation.instance._valuations.get(student, {}).items() if course in new_bundle)
    
    logger.debug('Current bundle valuations for student %s: %g', student, sum_valuations_cur)
    logger.debug('New bundle valuations for student %s: %g', student, sum_valuations_new)

    if (sum_valuations_cur < sum_valuations_new) or (len(current_bundle) < len(new_bundle) and sum_valuations_cur <= sum_valuations_new):
        logger.info('New bundle is better for student %s.', student)
        return True
    logger.info('New bundle is not better for student %s.', student)
    return False


cdef reduce_undersubscription(allocation: AllocationBuilder, dict price_vector, dict student_budgets, list priorities_student_list):
    cdef dict item_conflicts, agent_conflicts
    item_conflicts, agent_conflicts = calculate_conflicts(allocation)

    cdef dict preferred_schedule = find_preference_order_for_each_student(allocation.instance._valuations, allocation.instance._agent_capacities, item_conflicts, agent_conflicts)
    logger.debug('Preferred schedule calculated: %s', preferred_schedule)

    cdef dict course_demands_dict = compute_surplus_demand_for_each_course(price_vector, allocation, student_budgets, preferred_schedule)  
    logger.debug('Course demands calculated: %s', course_demands_dict)

    cdef dict capacity_undersubscribed_courses = {course: -1 * course_demand for course, course_demand in course_demands_dict.items() if course_demand < 0}
    logger.debug('Undersubscribed courses identified: %s', capacity_undersubscribed_courses)

    cdef dict student_schedule = find_best_schedule(price_vector, student_budgets, preferred_schedule)
    cdef dict student_schedule_dict = create_dictionary_of_schedules(student_schedule, allocation.instance.items, allocation.instance.agents)
    logger.debug('Initial student schedules: %s', student_schedule_dict)

    cdef list student_list = calculate_remaining_budgets(price_vector, student_budgets, student_schedule_dict, priorities_student_list, allocation)
    logger.debug('Initial remaining budgets calculated: %s', student_list)

    student_schedule_dict = reoptimize_student_schedules(allocation, price_vector, student_list, student_budgets, student_schedule_dict, capacity_undersubscribed_courses)
    allocation.update_allocation(student_schedule_dict)

    logger.info('Finished reallocation process for undersubscribed courses.')
    return allocation
