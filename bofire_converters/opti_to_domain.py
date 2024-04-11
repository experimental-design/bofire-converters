from typing import Dict, List, Optional, cast
from warnings import warn

import opti
import opti.objective as opti_o
import opti.parameter as opti_p
from bofire.data_models.constraints.api import (
    AnyConstraint,
    LinearEqualityConstraint,
    LinearInequalityConstraint,
    NChooseKConstraint,
    NonlinearEqualityConstraint,
    NonlinearInequalityConstraint,
)
from bofire.data_models.domain.api import Domain
from bofire.data_models.features.api import (
    AnyOutput,
    CategoricalInput,
    CategoricalOutput,
    ContinuousInput,
    ContinuousOutput,
    DiscreteInput,
)
from bofire.data_models.objectives.api import (
    AnyCategoricalObjective,
    AnyObjective,
    CloseToTargetObjective,
    ConstrainedCategoricalObjective,
    MaximizeObjective,
    MinimizeObjective,
)


def convert_inputs(inputs: opti.Parameters) -> List:
    """Make the Bofire equivalent to an inputs objects from (m)opti

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

    d_inputs = []
    for key, value in inputs.parameters.items():
        kwargs = {"key": key, convert_types[value.type]["domain"]: value.domain}
        d_type = convert_types[value.type]["type"](**kwargs)
        d_inputs.append(d_type)
    return d_inputs


def _convert_obj_cont_disc(obj: opti_o.Objective) -> AnyObjective:
    if isinstance(obj, opti.CloseToTarget):
        return CloseToTargetObjective(target_value=obj.target, exponent=obj.exponent)
    elif isinstance(obj, opti.Maximize):
        return MaximizeObjective()
    elif isinstance(obj, opti.Minimize):
        return MinimizeObjective()
    elif isinstance(obj, opti.CloseToTarget):
        return CloseToTargetObjective(target_value=obj.target, exponent=obj.exponent)
    elif obj is not None:
        raise Exception("Unhandled objective type: {type(obj)}")


def _convert_obj_cat(
    parameter_domain: List[str], obj: opti_o.Objective
) -> AnyCategoricalObjective:
    if isinstance(obj, opti.CloseToTarget):
        domain = cast(List[str], parameter_domain)
        return ConstrainedCategoricalObjective(
            categories=domain, desirability=[d == obj.target for d in domain]
        )
    elif isinstance(obj, opti.Maximize):
        raise ValueError("cannot maximize categorical output")
    elif isinstance(obj, opti.Minimize):
        raise ValueError("cannot minimize categorical output")
    elif obj is not None:
        raise Exception("Unhandled objective type: {type(obj)}")


def convert_outputs_and_objectives(
    outputs: opti.Parameters,
    objectives: opti.Objectives,
    output_constraints: Optional[opti.Objectives] = None,
) -> List[AnyOutput]:
    """Make BoFire outputs from opti outputs and objectives

    opti specifies experimental outputs, which are quantities to be observed
    and (at least) predicted, and also objectives, which refer by name to the
    outputs. Bofire does it differently; objectives are specified within
    outputs so that a list of bofire outputs contains the same information as both
    outputs and objectives from opti. Furthermore, opti allows output constraints,
    which in this function are converted to objectives.

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
        objectives = opti.Objectives(
            objectives.objectives + output_constraints.objectives
        )

    # create a dict where each key is an output and the values are the objectives in which
    # that output appears
    outs_and_objs: Dict[str, List[opti_o.Objective]] = {
        opti_out.name: [obj for obj in objectives if obj.name == opti_out.name]
        for opti_out in outputs
    }

    output_list = []
    for out_name, objs in outs_and_objs.items():
        objs = [None] if len(objs) == 0 else objs
        for idx, obj in enumerate(objs):
            # if there are multiple objectives associated with a single input,
            # give the resulting outputs in the bofire domain different names
            if len(objs) > 1:
                suffix = f"_{idx}"
            else:
                suffix = ""

            output: opti_p.Parameter = outputs[out_name]

            if output.type == "continuous":
                bof_obj = obj and _convert_obj_cont_disc(obj)
                bof_out = ContinuousOutput(key=f"{out_name}{suffix}", objective=bof_obj)
            elif output.type == "discrete":
                warn(f"{out_name} has been converted to a continuous output.")
                bof_obj = obj and _convert_obj_cont_disc(obj)
                bof_out = ContinuousOutput(key=f"{out_name}{suffix}", objective=bof_obj)
            elif output.type == "categorical":
                domain = cast(List[str], output.domain)
                if obj is None:
                    bof_obj = ConstrainedCategoricalObjective(
                        categories=domain, desirability=[True] * len(domain)
                    )
                else:
                    bof_obj = _convert_obj_cat(domain, obj)
                bof_out = CategoricalOutput(
                    key=f"{out_name}{suffix}",
                    type="CategoricalOutput",
                    categories=domain,
                    objective=bof_obj,
                )
            else:
                raise Exception(f"Unhandled output type: {outputs[out_name].type}")

            output_list.append(bof_out)

    return output_list


def convert_constraints(opti_constraints: opti.Constraints) -> List[AnyConstraint]:
    """opti constraints to bofire constraints

    Parameters:
        opti_constraints: The constraints to be converted

    Returns:
        List of bofire constraints
    """
    domain_constraints = []
    for cnstr in opti_constraints.get(types=opti.LinearEquality):
        domain_constraints.append(
            LinearEqualityConstraint(
                features=cnstr.names, coefficients=cnstr.lhs.tolist(), rhs=cnstr.rhs
            )
        )
    for cnstr in opti_constraints.get(types=opti.LinearInequality):
        domain_constraints.append(
            LinearInequalityConstraint(
                features=cnstr.names, coefficients=cnstr.lhs.tolist(), rhs=cnstr.rhs
            )
        )
    for cnstr in opti_constraints.get(types=opti.NonlinearEquality):
        domain_constraints.append(
            NonlinearEqualityConstraint(expression=cnstr.expression)
        )
    for cnstr in opti_constraints.get(types=opti.NonlinearInequality):
        domain_constraints.append(
            NonlinearInequalityConstraint(expression=cnstr.expression)
        )
    for cnstr in opti_constraints.get(types=opti.NChooseK):
        domain_constraints.append(
            NChooseKConstraint(
                features=cnstr.names,
                min_count=0,
                max_count=cnstr.max_active,
                none_also_valid=True,
            )
        )

    return domain_constraints


def convert_problem(opti_problem: opti.Problem) -> Domain:
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
        outputs=list(domain_outputs),
        constraints=domain_constraints and list(domain_constraints),
    )

    return bofire_domain
