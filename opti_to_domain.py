from typing import List

from bofire.data_models.constraints.api import (
    LinearEqualityConstraint,
    LinearInequalityConstraint,
    NChooseKConstraint,
    NonlinearEqualityConstraint,
    NonlinearInequalityConstraint,
)
from bofire.data_models.domain.api import Domain
from bofire.data_models.features.api import (
    CategoricalInput,
    ContinuousInput,
    ContinuousOutput,
    DiscreteInput,
    Output,
)
from bofire.data_models.objectives.api import (
    CloseToTargetObjective,
    MaximizeObjective,
    MinimizeObjective,
)
from opti import (
    Categorical,
    CloseToTarget,
    Continuous,
    Discrete,
    Maximize,
    Minimize,
    Objectives,
    Parameters,
    Problem,
)
from opti.constraint import (
    Constraints,
    LinearEquality,
    LinearInequality,
    NChooseK,
    NonlinearEquality,
    NonlinearInequality,
)

# Note: Parameter types are Continuous, Discrete Categorical from opti
# Domain input_features can be ?


def convert_inputs(inputs: Parameters) -> List:

    # opti inputs example:

    convert_types = {
        "discrete": {"type": DiscreteInput, "domain": "values"},
        "continuous": {"type": ContinuousInput, "domain": "bounds"},
        "categorical": {"type": CategoricalInput, "domain": "categories"},
    }

    # convert_types_bounds={'discrete': values,'continuous': bounds,'categorical':categories},

    d_inputs = []
    for key, value in inputs.parameters.items():
        kwargs = {"key": key, convert_types[value.type]["domain"]: value.domain}
        d_type = convert_types[value.type]["type"](**kwargs)
        d_inputs.append(d_type)
    return d_inputs


def convert_outputs_and_objectives(outputs: Parameters, objectives: Objectives) -> List:
    # in domain, outputs have an optional objective embedded, whereas in opti, separate
    # Questions: https://github.com/experimental-design/bofire/issues/77#issuecomment-1521418422

    # Can build domain from a bunch of lists, so need to build a list
    # For outputs with no objects, add None objective

    output_list = []
    # Step 1: build outputs from objectives
    for o in objectives:
        if isinstance(o, CloseToTarget):
            # then build a CloseToTargetObjective
            obj = CloseToTargetObjective(
                key=o.name, target_value=o.target, exponent=o.exponent
            )
            # Problem: what do I do with the tolerance? Should this be TargetObjective?
        elif isinstance(o, Maximize):
            obj = MaximizeObjective(key=o.name)
        elif isinstance(o, Minimize):
            obj = MinimizeObjective(key=o.name)
        else:  # throw an unhandled exception
            raise Exception("Unhandled objective type")
        output_list.append(obj)
    # Use set difference to fetch remaining outputs from outputs
    non_objectives = set(outputs.names).difference(set(objectives.names))

    # Step 2: build outputs from remaining outputs
    for o in non_objectives:
        if outputs.parameters[o].type == "continuous":
            out = ContinuousOutput(key=o, objective=None)
        else:  # is this how to handle non-continuous (categorical and discrete) outputs?
            out = Output(key=o, objective=None, type=outputs.parameters[o].type)
        output_list.append(out)

    return output_list


def convert_constraints(opti_constraints: Constraints) -> List:
    domain_constraints = []
    for cnstr in opti_constraints.get(types=LinearEquality):
        domain_constraints.append(
            LinearEqualityConstraint(
                features=cnstr.names, coefficients=cnstr.lhs.tolist(), rhs=cnstr.rhs
            )
        )
    for cnstr in opti_constraints.get(types=LinearInequality):
        domain_constraints.append(
            LinearInequalityConstraint(
                features=cnstr.names, coefficients=cnstr.lhs.tolist(), rhs=cnstr.rhs
            )
        )
    for cnstr in opti_constraints.get(types=NonlinearEquality):
        domain_constraints.append(
            NonlinearEqualityConstraint(expression=cnstr.expression)
        )
    for cnstr in opti_constraints.get(types=NonlinearInequality):
        domain_constraints.append(
            NonlinearInequalityConstraint(expression=cnstr.expression)
        )
    for cnstr in opti_constraints.get(types=NChooseK):
        domain_constraints.append(
            NChooseKConstraint(
                features=cnstr.names,
                min_count=0,
                max_count=cnstr.max_active,
                none_also_valid=True,
            )
        )

    return domain_constraints


def domain_from_opti(opti_problem: Problem) -> Domain:
    # new_domain = domain(conv_input_features,)

    domain_inputs = convert_inputs(opti_problem.inputs)
    if opti_problem.constraints is not None:
        domain_constraints = convert_constraints(opti_problem.constraints)
    else:
        domain_constraints = None

    domain_outputs = convert_outputs_and_objectives(
        opti_problem.outputs, opti_problem.objectives
    )

    bofire_domain = Domain.from_lists(
        inputs=domain_inputs,
        outputs=domain_outputs,
        constraints=domain_constraints,
    )

    return bofire_domain


if __name__ == "__main__":
    # inputs = Parameters(
    #     [
    #         Discrete("x1", domain=[0.0, 1.0, 2.0, 3.0]),
    #         Continuous("x2", domain=[-2.0, 2.0]),
    #         Continuous("x3", domain=[-2.0, 2.0]),
    #         Continuous("x4", domain=[-2.0, 2.0]),
    #         Categorical("x5", domain=["cat", "dog", "monkey"]),
    #     ]
    # )

    # print(convert_inputs(inputs))
    outputs = Parameters(
        [
            Discrete("meetings", domain=[0.0, 1.0, 2.0, 3.0]),
            Continuous("coffee", domain=[0, 20.0]),
            Continuous("seriousness", domain=[0, 10.0]),
            Categorical("animal", domain=["cat", "dog", "monkey"]),
        ]
    )

    objectives = Objectives(
        [
            Minimize("meetings", target=2),
            Maximize("coffee", target=4),
            CloseToTarget("seriousness", target=5, exponent=2, tolerance=1.1),
        ]
    )

    out_list = convert_outputs_and_objectives(outputs, objectives)
