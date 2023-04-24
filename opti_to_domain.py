from bofire.data_models.constraints.api import (
    LinearEqualityConstraint,
    LinearInequalityConstraint,
)
from bofire.data_models.domain.api import Domain
from bofire.data_models.features.api import ContinuousInput, ContinuousOutput


def convert_inputs():
    pass


def convert_iutputs_and_objectives():
    pass


def convert_constraints():
    pass


def domain_from_opti(opti_problem):
    # new_domain = domain(conv_input_features,)

    bofire_domain = Domain(
        input_features=[
            ContinuousInput(key="x1", bounds=(0, 1)),
            ContinuousInput(key="x2", bounds=(0.1, 1)),
            ContinuousInput(key="x3", bounds=(0, 0.6)),
        ],
        output_features=[ContinuousOutput(key="y")],
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
