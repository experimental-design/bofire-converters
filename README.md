# Tools to convert objects between bofire and, eg, mopti.

These tools are to help with migration of legacy applications from other BO frameworks to BoFire, and improve quality-of-life.

## Quick start

Clone this repo, then change to the directory you just cloned (the one containing setup.py) and do 

`pip install .`

Here is an example of converting a `Problem` object from [mopti](https://github.com/basf/mopti) to a BoFire `Domain`.

```python
from domainconverters.opti_to_domain import convert_problem
from opti.problems.multi import Daechert1

# Use one of the opti built-in problems as an example
my_opti_problem = Daechert1()                    
my_bofire_domain = convert_problem(my_opti_problem)
```
