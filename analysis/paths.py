"""Where the scripts in this directory read and write.

Every script resolves its paths through this module, so a checkout can be pointed
at any working directory and nothing is written next to the code. The working
directory is chosen in this order:

  1. `--data-root PATH` on the command line
  2. the `AI4QOSS_DATA_ROOT` environment variable
  3. `./_workspace` beside this file, which `.gitignore` already excludes

Inside it the scripts expect, and create as needed:

  _repos/        clones of the projects under study, one per directory
  _tmp/          scratch space for exported release trees
  out/<name>/    the output of each script, named for its directory

Inputs we do not publish are looked up with `private()`, which fails with an
explanation rather than a traceback when the directory is absent. Those scripts
are here to document how a published number was computed, not to be run by a
reader who does not hold the input.
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE / "_workspace"


def data_root():
    """The working directory, from the flag, the environment, or the default."""
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return Path(argv[i + 1]).expanduser().resolve()
        if a.startswith("--data-root="):
            return Path(a.split("=", 1)[1]).expanduser().resolve()
    env = os.environ.get("AI4QOSS_DATA_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return DEFAULT_ROOT


def repos():
    """Clones of the projects under study. Must already exist.

    The clone commands are in the docstring of each script that reads them, and
    `api_survival` additionally needs full history and tags.
    """
    p = data_root() / "_repos"
    if not p.is_dir():
        sys.exit(f"no clones at {p}\n"
                 f"Create it and clone the projects named in this script's "
                 f"docstring, or point --data-root somewhere that has them.")
    return p


def tmp():
    p = data_root() / "_tmp"
    p.mkdir(parents=True, exist_ok=True)
    return p


def out(name):
    """Output directory for one script, created on first use."""
    p = data_root() / "out" / name
    p.mkdir(parents=True, exist_ok=True)
    return p


def private(name, what):
    """An input we do not publish.

    `what` is a sentence naming the input and saying where it comes from, printed
    when the directory is absent so that a reader understands this is expected
    rather than broken.
    """
    p = data_root() / name
    if not p.exists():
        sys.exit(
            f"{p} is not present.\n"
            f"{what}\n"
            f"This script is published so that the method behind a number in the "
            f"paper can be read and checked. It cannot be run without that input. "
            f"See ../README.md, section 'Inputs we do not publish'.")
    return p


def published():
    """The CSVs this repository publishes, which the figure scripts read."""
    return HERE.parent / "data" / "figures"
