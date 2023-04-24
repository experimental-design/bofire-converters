import pytest
from bofire.data_models.domain.api import Domain
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

from opti_to_domain import convert_constraints, domain_from_opti

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
    assert isinstance(bofire_constraints, list)
