import logging

import model


class Builder:
    def __init__(self, metadata: dict):
        self.metadata = metadata

    def add_attributes(self, attrs: dict, ds: model.WithAttrs) -> None:
        for key, value in attrs.items():
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
            return ds
        except Exception as e:
            logging.error(f"Error building dataset model from ZARR metadata: {e}")
            raise RuntimeError(f"Failed to build dataset model: {e}")
