import json

from gridded_metadata.model.zarr import Builder
from tests.helpers import assert_array


def test_build_model() -> None:
    with open("tests/data/zarr_meta_1.json") as f:
        dataset1 = json.load(f)
    model = Builder(dataset1).build()
    assert model.attrs == {"title": "Test ZARR dataset"}
    assert len(model.arrays) == 4
    assert "time" in model.arrays
    assert_array(model.arrays["time"],
                 "time",
                 [300],
                 {"units": "days since 2000-01-01", "long_name": "Time"},
                 []
                )
    assert "lat" in model.arrays
    assert_array(model.arrays["lat"],
                 "lat",
                 [180],
                 {"units": "degrees_north", "long_name": "Latitude"},
                 []
                )
    assert "lon" in model.arrays
    assert_array(model.arrays["lon"],
                 "lon",
                 [360],
                 {"units": "degrees_east", "long_name": "Longitude"},
                 []
                )
    assert "tas" in model.arrays
    assert_array(model.arrays["tas"],
                 "tas",
                 [21549, 1057, 656],
                 {"units": "K", "long_name": "Near-surface air temperature"},
                 ["time", "lat", "lon"]
                )
