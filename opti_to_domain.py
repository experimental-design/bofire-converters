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
    for opti_out in outputs:
        if opti_out.name in objectives.names:
            obj = [obj for obj in objectives if obj.name == opti_out.name]
            if len(obj) > 1:
                raise NotImplementedError(
                    "Outputs appearing in multiple constraints is not yet supported in the converter."
                )
            else:
                obj = obj[0]
        else:
            obj = None

        if isinstance(obj, CloseToTarget):
            # then build a CloseToTargetObjective
            obj = CloseToTargetObjective(target_value=obj.target, exponent=obj.exponent)
            # Problem: what do I do with the tolerance? Should this be TargetObjective?
        elif isinstance(obj, Maximize):
            obj = MaximizeObjective()
        elif isinstance(obj, Minimize):
            obj = MinimizeObjective()
        elif obj is not None:  # throw an unhandled exception
            print(obj)
            raise Exception("Unhandled objective type")

        if opti_out.type == "continuous":
            out = ContinuousOutput(key=opti_out.name, objective=obj)
        else:
            out = Output(key=opti_out.name, objective=obj, type=opti_out.type)
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
