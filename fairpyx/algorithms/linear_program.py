from mip import *
import sys
import logging
from contextlib import redirect_stdout
import os

from fairpyx import Instance

# from fairpyx.algorithms.ACEEI import EFTBStatus

# TODO - delete this enum from here


# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()


# a = {'Alice': {3.5: ('x', 'y'), 3: ('x', 'z')}, 'Bob': {3.5: ('x', 'y'), 2: ('y', 'z')}}
# a = {'Alice': {3.5: (1, 1, 0), 3: (1, 0, 1)}
# initial_budgets = {"Alice": 5, "Bob": 4}
def check_envy(instance, student, other_student, a, t, prices):
    """
        The function accepts a pair of students, and returns pairs of courses for which envy exists.

        :param instance: a fair-course-allocation instance
        :param student: The student with the highest initial budget
        :param other_student: The student with the lowest initial budget
        :param a: dict that says for each budget what is the bundle with the maximum utility that a student can take
        :param t: type 𝑡 of the EF-TB constraint,
              0 for no EF-TB constraint,
              1 for EF-TB constraint,
              2 for contested EF-TB
        :param prices: courses prices

        Example run 6 iteration 5
        >>> from fairpyx import Instance
        >>> from fairpyx.algorithms import ACEEI
        >>> instance = Instance(
        ...     valuations={"Alice":{"x":5, "y":4, "z":1}, "Bob":{"x":4, "y":6, "z":3}},
        ...     agent_capacities=2,
        ...     item_capacities={"x":1, "y":1, "z":2})
        >>> student = "Alice"
        >>> other_student = "Bob"
        >>> a = {'Alice': {3.5: ('x', 'y'), 3: ('x', 'z')}, 'Bob': {3.5: ('x', 'y'), 2: ('y', 'z')}}
        >>> t = ACEEI.EFTBStatus.EF_TB
        >>> prices = {"x": 1.5, "y": 2, "z": 0}
        >>> check_envy(instance, student, other_student, a, t, prices)
        [(('x', 'z'), ('x', 'y'))]

        >>> instance = Instance(
        ...     valuations={"Alice":{"x":10, "y":20}, "Bob":{"x":10, "y":20}},
        ...     agent_capacities=1,
        ...     item_capacities={"x":1, "y":1})
        >>> student = "Alice"
        >>> other_student = "Bob"
        >>> a = {'Alice': {0: (), 1.1: ('y')}, 'Bob': {1.1: ('y'), 1: ('x')}}
        >>> t = ACEEI.EFTBStatus.EF_TB
        >>> prices = {"x": 1, "y": 1.1}
        >>> check_envy(instance, student, other_student, a, t, prices)
        [((), 'y'), ((), 'x')]
    """
    result = []
    # check if student envies in other_student
    for bundle_i in a[student].values():
        for bundle_j in a[other_student].values():
            if t == EFTBStatus.CONTESTED_EF_TB:
                # Iterate through keys in prices
                for key, value in prices.items():
                    # Check if value is 0 and key is not already in bundle_j
                    if value == 0 and key not in bundle_j:
                        # Add key to bundle_j
                        bundle_j += (key,)

                logger.info("----------CONTESTED_EF_TB---------")
                logger.info(f"bundle_j of {student} = {bundle_j}")

                sorted_bundle_j = sorted(bundle_j, key=lambda course: instance._valuations[student][course],
                                         reverse=True)
                logger.info(f"sorted_bundle_j of {student} = {sorted_bundle_j}")

                sorted_bundle_j = sorted_bundle_j[:instance.agent_capacity(student)]
                logger.info(f"instance.agent_capacity = {instance.agent_capacity(student)}")
                logger.info(f"sorted_bundle_j of {student} = {sorted_bundle_j}")

                bundle_j = tuple(sorted_bundle_j)
                logger.info(f"finish update bundle_j of {student} = {bundle_j}")

            if instance.agent_bundle_value(student, bundle_j) > instance.agent_bundle_value(student, bundle_i):
                result.append((bundle_i, bundle_j))
    return result


def get_envy_constraints(instance, initial_budgets, a, t, prices):
    """
        This function checks for every two students if there is envy between them,
        in case there is a constraint required for the model.

        :param instance: a fair-course-allocation instance
        :param initial_budgets:  the initial budgets of the students
        :param a: dict that says for each budget what is the bundle with the maximum utility that a student can take
        :param t: type 𝑡 of the EF-TB constraint,
              0 for no EF-TB constraint,
              1 for EF-TB constraint,
              2 for contested EF-TB
        :param prices: courses prices


        Example run 6 iteration 5
        >>> from fairpyx import Instance
        >>> from fairpyx.algorithms import ACEEI
        >>> instance = Instance(
        ...     valuations={"Alice":{"x":5, "y":4, "z":1}, "Bob":{"x":4, "y":6, "z":3}},
        ...     agent_capacities=2,
        ...     item_capacities={"x":1, "y":1, "z":2})
        >>> initial_budgets = {"Alice": 5, "Bob": 4}
        >>> a = {'Alice': {3.5: ('x', 'y'), 3: ('x', 'z')}, 'Bob': {3.5: ('x', 'y'), 2: ('y', 'z')}}
        >>> t = ACEEI.EFTBStatus.EF_TB
        >>> prices = {"x": 1, "y": 1.1}
        >>> get_envy_constraints(instance, initial_budgets, a, t, prices)
        [(('Alice', ('x', 'z')), ('Bob', ('x', 'y')))]

        >>> instance = Instance(
        ...     valuations={"Alice":{"x":10, "y":20}, "Bob":{"x":10, "y":20}},
        ...     agent_capacities=1,
        ...     item_capacities={"x":1, "y":1})
        >>> initial_budgets = {"Alice": 1.1, "Bob": 1}
        >>> a = {'Alice': {0: (), 1.1: ('y')}, 'Bob': {1.1: ('y'), 1: ('x')}}
        >>> t = ACEEI.EFTBStatus.EF_TB
        >>> prices = {"x": 1, "y": 1.1}
        >>> get_envy_constraints(instance, initial_budgets, a, t, prices)
        [(('Alice', ()), ('Bob', 'y')), (('Alice', ()), ('Bob', 'x'))]
    """

    students_names = instance.agents
    envy_constraints = []

    for student in students_names:
        for other_student in students_names:
            if student is not other_student:
                if initial_budgets[student] > initial_budgets[other_student]:  # check envy
                    # result contain the index of the bundles that student envious other_student
                    result = check_envy(instance, student, other_student, a, t, prices)

                    if result:
                        for pair in result:
                            i, j = pair
                            logger.info(f"bundle {i} , bundle {j}")
                            # envy_constraints.append((x[student, i], x[other_student, j]))
                            envy_constraints.append(((student, i), (other_student, j)))
                            logger.info(f"student {student} bundle {i} envy student {other_student} bundle {j}")
    return envy_constraints


def optimize_model(a: dict, instance: Instance, prices: dict, t: Enum, initial_budgets: dict):
    """
        Example run 6 iteration 5
        >>> from fairpyx import Instance
        >>> from fairpyx.algorithms import ACEEI
        >>> instance = Instance(
        ...     valuations={"Alice":{"x":5, "y":4, "z":1}, "Bob":{"x":4, "y":6, "z":3}},
        ...     agent_capacities=2,
        ...     item_capacities={"x":1, "y":1, "z":2})
        >>> a = {'Alice': {3.5: ('x', 'y'), 3: ('x', 'z')}, 'Bob': {3.5: ('x', 'y'), 2: ('y', 'z')}}
        >>> initial_budgets = {"Alice": 5, "Bob": 4}
        >>> prices = {"x": 1.5, "y": 2, "z": 0}
        >>> t = ACEEI.EFTBStatus.EF_TB
        >>> optimize_model(a,instance,prices,t,initial_budgets)
        [[('x', 'z'), ('x', 'y')], [('y', 'z'), ('x', 'y')]]
    """

    logger.info(f"a {a}")
    model = Model("allocations")
    courses_names = list(instance.items)
    students_names = list(instance.agents)

    # Decision variables
    x = {(student, bundle): model.add_var(var_type=BINARY) for student in students_names for bundle in
         a[student].values()}

    z = {course: model.add_var(var_type=CONTINUOUS, lb=-instance.item_capacity(course)) for course in courses_names}
    y = {course: model.add_var(var_type=CONTINUOUS) for course in courses_names}

    # Objective function
    objective_expr = xsum(y[course] for course in courses_names)
    model.objective = minimize(objective_expr)

    # Add constraints for absolute value of excess demand
    for course in courses_names:
        model += y[course] >= z[course]
        model += y[course] >= -z[course]

    # Course allocation constraints
    for course in courses_names:
        # constraint 1: ∑  ∑(𝑥_𝑖ℓ · 𝑎_𝑖ℓ𝑗) = 𝑐_𝑗 + 𝑧_𝑗  ∀𝑗 ∈ [𝑚], 𝑝_𝑗 > 0
        #            𝑖∈[𝑛] ℓ ∈ [𝑘_𝑖]
        if prices[course] > 0:
            model += xsum(
                x[student, bundle] * (1 if course in bundle else 0) for student in students_names for bundle in
                a[student].values()) == instance.item_capacity(course) + z[course]

        # constraint 2: ∑     ∑(𝑥_𝑖ℓ · 𝑎_𝑖ℓ𝑗) ≤ 𝑐𝑗 + 𝑧𝑗 ∀𝑗 ∈ [𝑚], 𝑝𝑗 = 0
        #  𝑖∈[𝑛] ℓ∈[𝑘_𝑖]
        else:
            model += xsum(
                x[student, bundle] * (1 if course in bundle else 0) for student in students_names for bundle in
                a[student].values()) <= instance.item_capacity(course) + z[course]

    # constraint 3: ∑𝑥_𝑖ℓ = 1  ∀𝑖 ∈ [𝑛]
    #               ℓ∈[𝑘_𝑖]
    for student in students_names:
        model += xsum(x[student, bundle] for bundle in a[student].values()) == 1

    # Add EF-TB constraints based on parameter t
    if t == EFTBStatus.NO_EF_TB:
        pass  # No EF-TB constraints, no need to anything

    elif t == EFTBStatus.EF_TB or t == EFTBStatus.CONTESTED_EF_TB:
        # Add EF-TB constraints here
        envy_constraints = get_envy_constraints(instance, initial_budgets, a, t, prices)
        for constraint in envy_constraints:
            model += x[constraint[0]] + x[constraint[1]] <= 1

    # Redirect solver output to null device
    model.verbose = 0

    # Optimize the model
    with open(os.devnull, 'w') as devnull:
        with redirect_stdout(devnull):
            model.optimize()

    if model.num_solutions:
        excess_demand_per_course = {course: y[course].x for course in courses_names}
    else:
        excess_demand_per_course = model.status

    new_budgets = {}
    for (student, bundle), var in x.items():
        if var.x == 1:  # Check if the decision variable is set to 1
            price = list(a[student].keys())[
                list(a[student].values()).index(bundle)]  # Extract the price from dictionary a
            new_budgets[student] = (price, bundle)

    # print("New budgets:", new_budgets)
    # print("Objective Value:", model.objective_value)
    # print("Excess Demand:", excess_demand)
    logging.info("New budgets: %s\nObjective Value: %s\nExcess Demand: %s", new_budgets, model.objective_value,
                 excess_demand_per_course)


    # # Process and print results todo: loogger
    # if model.num_solutions:
    #     print("Objective Value:", model.objective_value)
    #     for student in students_names:
    #         for l in a[student].values():
    #             print(f"x_{student}{l} =", x[student, l].x)
    #     for course in courses_names:
    #         print(f"|z_{course}|=y_{course} =", y[course].x)
    # else:
    #     print("Optimization was not successful. Status:", model.status)

    return new_budgets, model.objective_value, excess_demand_per_course


class EFTBStatus(Enum):
    NO_EF_TB = 0
    EF_TB = 1
    CONTESTED_EF_TB = 2


if __name__ == "__main__":
    instance = Instance(
        valuations={"Alice": {"x": 5, "y": 4, "z": 1}, "Bob": {"x": 4, "y": 6, "z": 3}},
        agent_capacities=2,
        item_capacities={"x": 1, "y": 1, "z": 2}
    )
    # alice: (9, (x,y), p=1.1), (6, (x,z), p=1), (5, (y,z), p=0.1)
    # bob: (10, (x,y), p=1.1), (9, (y,z), p=0.1), (7, (x,y), p=1)
    # epsilon =
    a = {'Alice': {3.5: ('x', 'y'), 3: ('x', 'z')}, 'Bob': {3.5: ('x', 'y'), 2: ('y', 'z')}}
    initial_budgets = {"Alice": 1.1, "Bob": 1}
    prices = {"x": 1, "y": 0.1, "z": 0}
    t = EFTBStatus.CONTESTED_EF_TB

    optimize_model(a, instance, prices, t, initial_budgets)
