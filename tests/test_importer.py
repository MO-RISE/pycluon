from pycluon.importer import import_odvd

from pathlib import Path
from tempfile import TemporaryDirectory


def test_odvd_importer():
    odvd_spec = """
message first.second.Third [id = 38437] {
  float first [id = 1];
  string second [id = 2];
  int32 third [id = 3];
}"""

    with TemporaryDirectory() as tmp:
        odvd_spec_path = Path(tmp) / "my_definitions.odvd"
        odvd_spec_path.write_text(odvd_spec)

        module = import_odvd(odvd_spec_path)

        assert "first_second_Third" in dir(module)

        object = module.first_second_Third()

        assert type(object.first) == float
        assert type(object.second) == str
        assert type(object.third) == int
