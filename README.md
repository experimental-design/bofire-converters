# Tools to convert objects between bofire and, eg, mopti.

These tools are to help with migration of legacy applications from other BO frameworks to BoFire, and improve quality-of-life.

# Quick start

Clone this repo, then change to the directory you just cloned (the one containing setup.py) and do 

`pip install .`

Here is an example of converting a `Problem` object from mopti to a BoFire `Domain`.

```python
from domainconverters.opti_to_domain import convert_problem
from opti import Continuous, Minimize, Objectives, Parameters, Problem
from opti.constraint import Constraints, NonlinearInequality

myproblem = Problem(inputs=Parameters([Continuous('x1', domain=[78.0, 102.0]), Continuous('x2', domain=[33.0, 45.0])]),
                    outputs=Parameters([Continuous('y0')]),
                    objectives=Objectives([Minimize('y0')]),
                    constraints=Constraints([NonlinearInequality('(85.334407 + 0.0056858 * x2 * x1 ) - 92.0')]))
mydomain = convert_problem(myproblem)
```
