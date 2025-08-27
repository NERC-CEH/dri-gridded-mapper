class WithAttrs:
    def __init__(self):
        self.attrs = {}

    def add_attr(self, key: str, value: str) -> None:
        self.attrs[key] = value

class DatasetElement(WithAttrs):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

class Dimension(DatasetElement):
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self.size = size

class Array(DatasetElement):
    def __init__(self, name: str, dimensions: list[int]):
        super().__init__(name)
        self.dimensions = dimensions
        self.references: list[DatasetElement] = []

    def add_reference(self, reference: DatasetElement) -> None:
        self.references.append(reference)

class Dataset(WithAttrs):
    def __init__(self):
        super().__init__()
        self.dimensions: dict[str, Dimension] = {}
        self.arrays: dict[str, Array] = {}

    def add_dimension(self, dimension: Dimension) -> None:
        self.dimensions[dimension.name] = dimension

    def add_array(self, array: Array) -> None:
        self.arrays[array.name] = array
