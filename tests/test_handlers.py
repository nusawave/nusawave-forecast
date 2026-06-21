import importlib

import pytest

HANDLERS = [
    ("wind", "WindHandler"),
    ("swh", "SwhHandler"),
    ("swell", "SwellHandler"),
    ("seatemp", "SeatempHandler"),
    ("rainrate", "RainrateHandler"),
    ("seacurrent", "SeacurrentHandler"),
    ("temp", "TempHandler"),
    ("relhum", "RelhumHandler"),
    ("mslp", "MslpHandler"),
]


@pytest.mark.parametrize("param,class_name", HANDLERS)
def test_handler_class_exists(param, class_name):
    module = importlib.import_module(f"plotter.handlers.{param}")
    assert hasattr(module, class_name), (
        f"Expected {class_name} in plotter.handlers.{param}"
    )


def test_gfswave_variable_map():
    from plotter.modelparams.gfswave import VARIABLE_MAP

    assert "wind" in VARIABLE_MAP
    assert "swh" in VARIABLE_MAP
    assert "swell" in VARIABLE_MAP
    assert VARIABLE_MAP["source"]
