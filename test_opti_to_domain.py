import pytest
from bofire.data_models.domain.api import Domain
from opti import Categorical, Continuous, Discrete, Parameters
from opti.constraint import (
    Constraints,
    LinearEquality,
    LinearInequality,
    NChooseK,
    NonlinearEquality,
    NonlinearInequality,
)
from opti.problems.cbo_benchmarks import (
    G4,
    G6,
    G7,
    G8,
    G10,
    Gardner,
    Gramacy,
    PressureVessel,
    Sasena,
    SpeedReducer,
    TensionCompression,
    WeldedBeam1,
)
from opti.problems.mixed import DiscreteFuelInjector, DiscreteVLMOP2

from opti_to_domain import convert_constraints, convert_inputs, domain_from_opti

test_problems = [
    G4(),
    G6(),
    G7(),
    G8(),
    G10(),
    Gardner(),
    Gramacy(),
    PressureVessel(),
    Sasena(),
    SpeedReducer(),
    TensionCompression(),
    WeldedBeam1(),
    DiscreteFuelInjector(),
    DiscreteVLMOP2(),
]


@pytest.mark.parametrize("test_problem", test_problems)
def test_convert_benchmarks(test_problem):
    bofire_domain = domain_from_opti(test_problem)
    assert isinstance(bofire_domain, Domain)
    assert len(test_problem.inputs) == len(bofire_domain.inputs)
    if test_problem.constraints is not None:
        assert len(test_problem.constraints) == len(bofire_domain.constraints)


def test_convert_constraints():
    cnstrs = Constraints(
        [
            LinearEquality(["x1", "x2", "x3"], lhs=[1, 1, 1], rhs=1),
            LinearInequality(["x1", "x2"], lhs=[1, 1], rhs=0.5),
            NonlinearEquality("x1 + x2 + x3 - 1"),
            NonlinearInequality("x1**2 + x3**2 - 1"),
            NChooseK(["x1", "x2"], max_active=2),
        ]
    )
    bofire_constraints = convert_constraints(cnstrs)
    print(bofire_constraints)
    assert isinstance(bofire_constraints, list)
    assert len(bofire_constraints) == 5


def test_convert_inputs():
    inputs = Parameters(
        [
            Discrete("x1", domain=[0.0, 1.0, 2.0, 3.0]),
            Continuous("x2", domain=[-2.0, 2.0]),
            Continuous("x3", domain=[-2.0, 2.0]),
            Continuous("x4", domain=[-2.0, 2.0]),
            Categorical("x5", domain=["cat", "dog", "monkey"]),
        ]
    )

    bofire_inputs = convert_inputs(inputs)
    assert isinstance(bofire_inputs, list)
    assert len(bofire_inputs) == 5

def test_convert_outputs_and_objectives():
    outputs = Parameters(
        [
            Discrete("meetings", domain=[0.0, 1.0, 2.0, 3.0]),
            Continuous("coffee", domain=[0, 20.0]),
            Continuous("seriousness", domain=[0, 10.0]),
            Categorical("animal", domain=["cat", "dog", "monkey"])
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
    
    
    assert out_list[0].type == 'MinimizeObjective'
    assert out_list[-1].type == 'categorical'