# FDRI Gridded Data Mapping Tool

The mapping tool reads metadata from netCDF and ZARR archives and creates RDF representing the input file as an `fdri:GriddedDataset` with metadata properties taken from any top-level attributes in the metadata (in the root group, in the case of ZARR), and with the dimensions and arrays defined in the metadata also included.

The mapping of structural metadata is fixed. For dimensions, the dimension name and its size are extracted. For arrays, the shape of the array, the dimensions and/or arrays it references, and additional metatdata properties are extracted.

The mapping of attributes of the dataset and of each array in the dataset is configured using a mapping file passed as an argument to the mapping tool.

The mapping file syntax is the same as used in the [rdf-mapper](https://github.com/NERC-CEH/rdf-mapper) tool. The mapping can be used to assert additional RDF properties for the dataset, each group below the root group of the dataset, and for each array defined in the dataset. The mapper receives all of the extended attributes defined for the item being processed as a virtual "row". The column names are the attribute names and the values are the attribute values. In addition the following columns are added to the row:

  * `$base`: The Base URI for the metadata generator. This is also the URI that is assigned to the resource created for the top-level Dataset.
  * `$type`: one of `Dataset`, `Container` or `Array` indicating the type of element whose metadata is being processed.
  * `$dataset`: The URI assigned to the root gridded dataset resource

