import logging

import gridded_metadata.model as model


class Builder:
    SPECIAL_ATTRS = {"_ARRAY_DIMENSIONS"}

    def __init__(self, metadata: dict):
        self.metadata = metadata

    def add_attributes(self, attrs: dict, ds: model.WithAttrs) -> None:
        for key, value in attrs.items():
            if key in self.SPECIAL_ATTRS:
                continue
            ds.add_attr(key, str(value))

    def get_array_names(self, metadata: dict) -> list[str]:
        array_names = []
        for key in metadata.keys():
            if key.endswith('/.zarray'):
                array_names.append(key[:-8])  # Remove the '/.zarray' suffix
        return array_names

    def build_array(self, array_name: str, metadata: dict) -> model.Array:
        zarry = metadata.get(f"{array_name}/.zarray", {})
        zattrs = metadata.get(f"{array_name}/.zattrs", {})
        dimensions = zarry.get('shape', [])
        array = model.Array(array_name, dimensions)
        self.add_attributes(zattrs, array)
        return array

    def resolve_references(self, metadata: dict, array_name: str, ds: model.Dataset) -> None:
        array = ds.arrays[array_name]
        dim_names = metadata.get(f"{array_name}/.zattrs", {}).get("_ARRAY_DIMENSIONS", [])
        for dim_name in dim_names:
            if dim_name in ds.arrays:
                array.add_reference(ds.arrays[dim_name])
            if dim_name in ds.dimensions:
                array.add_reference(ds.dimensions[dim_name])

    def build(self) -> model.Dataset:
        try:
            ds = model.Dataset()
            if 'metadata' not in self.metadata:
                raise ValueError("Missing 'metadata' key in ZARR metadata")
            metadata = self.metadata['metadata']
            zattrs = metadata.get('.zattrs', {})
            self.add_attributes(zattrs, ds)
            for array_name in self.get_array_names(metadata):
                ds.add_array(self.build_array(array_name, metadata))
            for array_name in self.get_array_names(metadata):
                self.resolve_references(metadata, array_name, ds)
            return ds
        except Exception as e:
            logging.error(f"Error building dataset model from ZARR metadata: {e}")
            raise RuntimeError(f"Failed to build dataset model: {e}")
