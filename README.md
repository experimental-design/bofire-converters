# Tools to convert objects between bofire and, eg, mopti.

These tools are to help with migration of legacy applications from other BO frameworks to BoFire, and improve quality-of-life.

## Quick start

Clone this repo, then change to the directory you just cloned (the one containing setup.py) and do 

`pip install .`

Here is an example of converting a `Problem` object from [mopti](https://github.com/basf/mopti) to a BoFire `Domain`.

```python
from domainconverters.opti_to_domain import convert_problem
from opti import Continuous, Minimize, Objectives, Parameters, Problem
from opti.constraint import Constraints, NonlinearInequality
from opti.problems.multi import Daechert1

# Use one of the opti built-in problems as an example
myproblem = Daechert1()                    
mydomain = convert_problem(myproblem)
```
