from typing import List

from bofire.data_models.constraints.api import (
    LinearEqualityConstraint,
    LinearInequalityConstraint,
)
from bofire.data_models.domain.api import Domain
from bofire.data_models.features.api import (
    CategoricalInput,
    ContinuousInput,
    ContinuousOutput,
    DiscreteInput,
)
from opti import Categorical, Continuous, Discrete, Parameters, Objectives, Minimize, Maximize, CloseToTarget
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


def convert_outputs_and_objectives():
    pass


def convert_constraints(opti_constraints: Constraints) -> List:
    
    for cnstr in opti_constraints.get(types=LinearEquality):
        print(cnstr.lhs)
        print(cnstr.rhs)
        print(cnstr.names)
    for cnstr in opti_constraints.get(types=LinearInequality):
        print(cnstr.lhs)
        print(cnstr.rhs)
        print(cnstr.names)
    for cnstr in opti_constraints.get(types=NonlinearEquality):
        print(cnstr.expression)
    for cnstr in opti_constraints.get(types=NonlinearInequality):
        print(cnstr.expression)
    for cnstr in opti_constraints.get(types=NChooseK):
        print(cnstr.max_active)
        print(cnstr.names)

    return []


def convert_constraints(opti_constraints: Constraints) -> List:

    for cnstr in opti_constraints.get(types=LinearEquality):
        print(cnstr.lhs)
        print(cnstr.rhs)
        print(cnstr.names)
    for cnstr in opti_constraints.get(types=LinearInequality):
        print(cnstr.lhs)
        print(cnstr.rhs)
        print(cnstr.names)
    for cnstr in opti_constraints.get(types=NonlinearEquality):
        print(cnstr.expression)
    for cnstr in opti_constraints.get(types=NonlinearInequality):
        print(cnstr.expression)
    for cnstr in opti_constraints.get(types=NChooseK):
        print(cnstr.max_active)
        print(cnstr.names)

    return []


def domain_from_opti(opti_problem):
    # new_domain = domain(conv_input_features,)

    bofire_domain = Domain.from_lists(
        inputs=[
            ContinuousInput(key="x1", bounds=(0, 1)),
            ContinuousInput(key="x2", bounds=(0.1, 1)),
            ContinuousInput(key="x3", bounds=(0, 0.6)),
        ],
        outputs=[ContinuousOutput(key="y")],
        constraints=[
            LinearEqualityConstraint(
                features=["x1", "x2", "x3"], coefficients=[1, 1, 1], rhs=1
            ),
            LinearInequalityConstraint(
                features=["x1", "x2"], coefficients=[5, 4], rhs=3.9
            ),
            LinearInequalityConstraint(
                features=["x1", "x2"], coefficients=[-20, 5], rhs=-3
            ),
        ],
    )

    return bofire_domain


if __name__ == "__main__":
    inputs = Parameters(
        [
            Discrete("x1", domain=[0.0, 1.0, 2.0, 3.0]),
            Continuous("x2", domain=[-2.0, 2.0]),
            Continuous("x3", domain=[-2.0, 2.0]),
            Continuous("x4", domain=[-2.0, 2.0]),
            Categorical("x5", domain=["cat", "dog", "monkey"]),
        ]
    )

    print(convert_inputs(inputs))
