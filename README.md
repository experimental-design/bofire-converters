# Mopti Problem to Bofire Domain Converter

These tools are to help with migration of legacy applications from [Mopti](https://github.com/basf/mopti) to [BoFire](https://github.com/experimental-design/bofire). Mopti is for defining optimization problems (inputs, outputs, constraints, ...) and has some sampling utilities. If you have a _problem_ defined in the Mopti format, `bofire_converters` can help you to create the corresponding BoFire object, which is called a _domain_.

## Quick start

Install via pip

`pip install bofire-converters`

Here is an example of converting a `Problem` object from [Mopti](https://github.com/basf/mopti) to a BoFire `Domain`.

```python
from bofire_converters.opti_to_domain import convert_problem
from opti.problems.multi import Daechert1

# Use one of the opti built-in problems as an example
my_opti_problem = Daechert1()                    
my_bofire_domain = convert_problem(my_opti_problem)
```
