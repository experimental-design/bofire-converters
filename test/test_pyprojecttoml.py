def find_min_bofire_version(pkg: str, filepath: str):
    with open(filepath) as f:
        for line in f:
            if f"{pkg}==" in line:
                raise Exception(
                    "bofire version is pinned to a specific version. please specify the minimal version with >="
                )
            if f"{pkg}>=" in line:
                return line.split("=")[1].split('"')[0].strip()


def find_all_deps_inreqstxt(filepath: str):
    with open(filepath) as f:
        for line in f:
            if line.strip() != "" and line.strip()[0] != "#":
                if ">=" in line:
                    yield line.split(">=")[0].strip()
                else:
                    raise ValueError(
                        f"Please specify the minimal version with >= in {filepath}"
                    )


def test():
    for dep in find_all_deps_inreqstxt("requirements.txt"):
        min_v_req = find_min_bofire_version(dep, "requirements.txt")
        min_v_pyprtoml = find_min_bofire_version(dep, "pyproject.toml")
        assert min_v_req == min_v_pyprtoml
