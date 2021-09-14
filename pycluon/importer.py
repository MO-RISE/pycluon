"""Custom importing functionality"""
from pathlib import Path
import importlib.util
from tempfile import TemporaryDirectory

from pycluon.scripts import run_script

# pylint: disable=fixme


def import_odvd(odvd_path: Path):
    """Importing a odvd specification and returning a loaded python module ready for use

    Args:
        odvd_path (Path): A path to the odvd specification

    Returns:
        module: A loaded, ready to use python module
    """
    odvd_path = Path(odvd_path).absolute()

    with TemporaryDirectory() as tmp:
        proto_defs = Path(tmp) / odvd_path.stem

        run_script(["cluon-msc", "--proto", f"--out={proto_defs}", str(odvd_path)])

        python_output = Path(tmp) / "python"
        python_output.mkdir()

        run_script(
            [
                "protoc",
                f"--proto_path={tmp}",
                f"--python_out={python_output.absolute()}",
                str(proto_defs),
            ]
        )

        # TODO: The final python module name should be constructed from all
        # necessary rules. Consider the below a quick fix...
        module_name = f"{odvd_path.stem.replace('-','_')}_pb2"
        module_path = python_output / f"{module_name}.py"

        # Load the new module dynamically
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module
