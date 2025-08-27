import subprocess

import netCDF4 as nc

from gridded_metadata.model import Array, Dataset, Dimension


def cdl_to_ncd(cdl_file_path: str, ncd_file_path: str) -> int:
    return subprocess.check_call(['ncgen', '-o', ncd_file_path, cdl_file_path])

class Builder:
    def __init__(self, src: nc.Dataset):
        self.src = src
        self.dataset = Dataset()

    def build(self) -> Dataset:
        for attr in self.src.ncattrs():
            self.dataset.add_attr(attr, self.src.getncattr(attr))
        for dim_name, dim in self.src.dimensions.items():
            dim_model = self.build_dimension(dim_name, dim)
            self.dataset.add_dimension(dim_model)
        for var_name, var in self.src.variables.items():
            self.dataset.add_array(self.build_array(var_name, var))
        for var_name, var in self.src.variables.items():
            self.resolve_references(var_name, var)
        return self.dataset

    def build_dimension(self, name: str, dimension: nc.Dimension) -> Dimension:
        m = Dimension(name, dimension.size)
        return m

    def build_array(self, name: str, array: nc.Variable) -> Array:
        m = Array(name, list(array.shape))
        for attr in array.ncattrs():
            m.add_attr(attr, array.getncattr(attr))
        return m

    def resolve_references(self, var_name: str, array: nc.Variable) -> None:
        m = self.dataset.arrays[var_name]
        for dim_name in array.dimensions:
            if dim_name in self.dataset.arrays:
                m.add_reference(self.dataset.arrays[dim_name])
            elif dim_name in self.dataset.dimensions:
                m.add_reference(self.dataset.dimensions[dim_name])


