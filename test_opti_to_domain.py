
from opti.problems.cbo_benchmarks import (
    Gardner,
    Gramacy,
    G4,
    G6,
    G7,
    G8,
    G10,
    Sasena,
    TensionCompression,
    PressureVessel,
    WeldedBeam1,
    SpeedReducer,
)

from opti.problems.mixed import Discrete, DiscreteFuelInjector, DiscreteVLMOP2


def test_convert_benchmarks():
    # here 
    test_problem = Gardner()
    test_domain = domain_from_opti(test_problem)
    assert validity_of_test_domain
    