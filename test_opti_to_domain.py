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
    DiscreteFuelInjector,
    DiscreteVLMOP2,
]


def test_convert_benchmarks():
    # here
    for test_problem_class in test_problems:
        test_problem = test_problem_class()
        test_domain = domain_from_opti(test_problem)
        assert isinstance(test_domain, Domain)
