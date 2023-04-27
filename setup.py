from setuptools import setup

setup(
    name="bofire-converters",
    version="0.1",
    description="Convert objects from other BO frameworks to BoFire objects",
    url="https://github.com/experimental-design/bofire-converters",
    packages=["domainconverters"],
    install_requires=[
        "mopti",
        "bofire",
    ],
    tests_require=["pytest"],
    python_requires=">=3.6",
)
