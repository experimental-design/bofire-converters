import pytest
from bofire.data_models.domain.api import Domain
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

from opti_to_domain import domain_from_opti

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
