"""Custom scripting machinery for binary command line applications bundled with pycluon"""
import sys
import subprocess
from pathlib import Path

# pylint: disable=fixme

BIN_DIR = Path(__file__).parent / "bin"

SCRIPTS = {
    "protoc": "protoc",
    "cluon-msc": str(BIN_DIR / "cluon-msc"),
    "cluon-OD4toStdout": str(BIN_DIR / "cluon-OD4toStdout"),
    "cluon-OD4toJSON": str(BIN_DIR / "cluon-OD4toJSON"),
    "cluon-LCMtoJSON": str(BIN_DIR / "cluon-LCMtoJSON"),
    "cluon-filter": str(BIN_DIR / "cluon-filter"),
    "cluon-livefeed": str(BIN_DIR / "cluon-livefeed"),
    "cluon-rec2csv": str(BIN_DIR / "cluon-rec2csv"),
    "cluon-replay": str(BIN_DIR / "cluon-replay"),
}

# TODO: Handling of exceptions and output is not as it should be. We should
# NOT swallow all CalledProcessErrors by default...


def _run_in_subprocess(*args):
    """Run a set of arguments in a subprocess, continuously printing output"""
    with subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
    ) as process:
        for line in process.stdout:
            print(line, end="")


def run_script(argv):
    """Run an argv input as a script, first substituting the path to the binary"""
    # Fetch correct path for script
    argv[0] = SCRIPTS[Path(argv[0]).name]
    _run_in_subprocess(*argv)


def script_entrypoint():
    """A common entrypoint for all scripts part of pycluon"""
    run_script(sys.argv)
