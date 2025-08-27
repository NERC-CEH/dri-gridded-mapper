from model import Dataset, Dimension, Array
import netCDF4 as nc

class Builder:
    def __init__(self, src: nc.Dataset):
        self.src = src
        self.dataset = Dataset()

    def build(self) -> Dataset:
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
        m = Array(name, array.shape)
        for attr in array.ncattrs():
            m.add_attr(attr, array.getncattr(attr))
        return m
    
    def resolve_references(self, var_name: str, array: nc.Variable):
        m = self.dataset.arrays[var_name]
        for dim_name in array.dimensions:
            if dim_name in self.dataset.arrays:
                m.add_reference(self.dataset.arrays[dim_name])
            elif dim_name in self.dataset.dimensions:
                m.add_reference(self.dataset.dimensions[dim_name])


