import netCDF4 as nc
import pytest

import gridded_metadata.model.netcdf as netcdf
from tests.helpers import assert_array, assert_dimension


@pytest.fixture
def dataset1() -> nc.Dataset:
    ds = nc.Dataset("test.nc", "w", format="NETCDF4", diskless=True, persist=False)
    ds.createDimension("time", None)
    ds.createDimension("lat", 180)
    ds.createDimension("lon", 360)
    ds.setncattr_string("title", "Test NetCDF dataset")
    var = ds.createVariable("temperature", float, ("time", "lat", "lon"))
    var.setncattr_string("units", "K")
    var.setncattr_string("long_name", "Surface temperature")
    return ds

class TestBuilder:
    def test_build_model(self, dataset1: nc.Dataset) -> None:
        model = netcdf.Builder(dataset1).build()
        assert len(model.dimensions) == 3
        assert_dimension(model.dimensions["time"], "time", 0, {})
        assert_dimension(model.dimensions["lat"], "lat", 180, {})
        assert_dimension(model.dimensions["lon"], "lon", 360, {})
        assert model.attrs == {"title": "Test NetCDF dataset"}
        assert len(model.arrays) == 1
        assert "temperature" in model.arrays
        assert_array(model.arrays["temperature"],
                     "temperature",
                     [0, 180, 360],
                     {"units": "K", "long_name": "Surface temperature"},
                     ["time", "lat", "lon"]
                    )
