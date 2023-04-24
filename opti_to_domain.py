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
from opti import Categorical, Continuous, Discrete, Parameters

# Note: Parameter types are Continuous, Discrete Categorical from opti
# Domain input_features can be ?


def convert_inputs():

    # opti inputs example:
    inputs = Parameters(
        [
            Discrete("x1", domain=[0.0, 1.0, 2.0, 3.0]),
            Continuous("x2", domain=[-2.0, 2.0]),
            Continuous("x3", domain=[-2.0, 2.0]),
            Continuous("x4", domain=[-2.0, 2.0]),
        ]
    )

    convert_types = (
        {
            "discrete": DiscreteInput,
            "continuous": ContinuousInput,
            "categorical": CategoricalInput,
        },
    )
    # convert_types_bounds={'discrete': values,'continuous': bounds,'categorical':categories},

    d_inputs = []
    for key, value in inputs.parameters.items():
        if value.type == "categorical":
            d_type = convert_types[value.type](key=key, categories=value.domain)
        elif value.type == "continuous":
            d_type = "somthinig else"

    tmp = Categorical
    # d_input=ContinuousInput(key="x1", bounds=(0, 1))
    d_type
    tmp

    return d_inputs


def convert_intputs_and_objectives():
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
