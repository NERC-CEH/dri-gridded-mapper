import gridded_metadata.model as model


def assert_dimension(dim: model.Dimension, name: str, size: int, attrs: dict) -> None:
    assert dim.name == name
    assert dim.size == size
    assert dim.attrs == attrs

def assert_array(arr: model.Array, name: str, dimensions: list[int], attrs: dict, references: list[str]) -> None:
    assert arr.name == name
    assert arr.dimensions == dimensions
    assert arr.attrs == attrs
    assert sorted(ref.name for ref in arr.references) == sorted(references)

