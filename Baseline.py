"""Deprecated compatibility shim — use `crewai run` or `python -m acquisition_helper.main`."""

import sys
import warnings

warnings.warn(
    "Baseline.py is deprecated. Use: crewai run  or  python -m acquisition_helper.main",
    DeprecationWarning,
    stacklevel=1,
)

from acquisition_helper.main import run

if __name__ == "__main__":
    sys.exit(run(["--skip-wizard", "--non-interactive"]))
