from typing import List, Optional
from warnings import warn

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
    """Make the Bofire equivalent to a Parameters objects from (m)opti

    Parameters:
        inputs: The inputs from an opti problem generated using
        Parameters

    Returns:
        List of BoFire parameters, eg, ContinuousInput

    Examples:
        # Parameters, Discrete, Continuous and Categorical are from mopti
        inputs = Parameters(
            [
                Discrete("x1", domain=[0.0, 1.0, 2.0, 3.0]),
                Continuous("x2", domain=[-2.0, 2.0]),
                Continuous("x3", domain=[-2.0, 2.0]),
                Continuous("x4", domain=[-2.0, 2.0]),
                Categorical("x5", domain=["cat", "dog", "monkey"]),
            ]
        )
        convert_inputs(inputs)
    """
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


def convert_outputs_and_objectives(
    outputs: Parameters,
    objectives: Objectives,
    output_constraints: Optional[Objectives] = None,
) -> List:
    """Make BoFire outputs from opti outputs and objectives

    opti specifies experimental outputs, which are quantities to be observed
    and (at least) predicted, and also objectives, which refer by name to the
    outputs. Bofire does it differently; objectives are specified within
    outputs so that a list of bofire outputs contains the same information as both
    outputs and objectives from opti.

    Questions about parameters and tolerances:
    https://github.com/experimental-design/bofire/issues/77#issuecomment-1521418422

    Parameters:
        outputs: outputs from opti. These are quantities that get modelled and are
            usually generated using the Parameters function from opti.
        objectives: objectives from opti. These refer to the names of the
            outputs to determine what is to be optimized

    Returns:
        List of BoFire outputs
    """
    # Treat output constraints from opti problems like objectives
    if output_constraints is not None:
        objectives = Objectives(objectives.objectives + output_constraints.objectives)

    # create a dict where each key is an output and the values are the objectives in which
    # that output appears
    outs_and_objs = {
        opti_out.name: [obj for obj in objectives if obj.name == opti_out.name]
        for opti_out in outputs
    }

    output_list = []
    for out, objs in outs_and_objs.items():
        objs = [None] if len(objs) == 0 else objs
        for idx, obj in enumerate(objs):
            bof_obj = None
            if isinstance(obj, CloseToTarget):
                bof_obj = CloseToTargetObjective(
                    target_value=obj.target, exponent=obj.exponent
                )
            elif isinstance(obj, Maximize):
                bof_obj = MaximizeObjective()
            elif isinstance(obj, Minimize):
                bof_obj = MinimizeObjective()
            elif obj is not None:
                raise Exception("Unhandled objective type: {type(obj)}")

            # if there are multiple objectives associated with a single input,
            # give the resulting outputs in the bofire domain different names
            if len(objs) > 1:
                suffix = f"_{idx}"
            else:
                suffix = ""

            if outputs[out].type != "continuous":
                warn(f"{out} has been converted to a continuous output.")
            bof_out = ContinuousOutput(key=f"{out}{suffix}", objective=bof_obj)
            output_list.append(bof_out)

    return output_list


def convert_constraints(opti_constraints: Constraints) -> List:
    """opti constraints to bofire constraints

    Just straightforward renaming here.

    Parameters:
        opti_constraints: The constraints to be converted

    Returns:
        List of bofire constraints
    """
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


def convert_problem(opti_problem: Problem) -> Domain:
    """Turn an opti problem into the equivalent bofire domain

    Parameters:
        opti_problem: Problem object from opti for conversion

    Returns:
        Domain, able to be used as a problem definition by bofire.

    Examples:
    myproblem = Problem(
                    inputs=Parameters(
                        [Continuous('x1', domain=[78.0, 102.0]),
                         Continuous('x2', domain=[33.0, 45.0])]
                    ),
                    outputs=Parameters(
                        [Continuous('y0')]
                    ),
                    objectives=Objectives(
                    [Minimize('y0')]
                    ),
                    constraints=Constraints(
                        [NonlinearInequality('(85.334407 + 0.0056858 * x2 * x1 ) - 92.0')]
                    ),
                )
    mydomain = convert_problem(myproblem)
    """

    domain_inputs = convert_inputs(opti_problem.inputs)
    if opti_problem.constraints is not None:
        domain_constraints = convert_constraints(opti_problem.constraints)
    else:
        domain_constraints = None

    domain_outputs = convert_outputs_and_objectives(
        opti_problem.outputs, opti_problem.objectives, opti_problem.output_constraints
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
