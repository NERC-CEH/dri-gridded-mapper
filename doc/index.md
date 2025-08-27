# FDRI Gridded Data Mapping Tool

The mapping tool reads metadata from netCDF and ZARR archives and creates RDF representing the input file as an `fdri:GriddedDataset` with metadata properties taken from any top-level attributes in the metadata (in the root group, in the case of ZARR), and with the dimensions and arrays defined in the metadata also included.

The mapping of structural metadata is fixed. For dimensions, the dimension name and its size are extracted. For arrays, the shape of the array, the dimensions and/or arrays it references, and additional metatdata properties are extracted.

## Metadata mapping

The mapping of metadata attributes for datasets and arrays is configured by updating the entries in the `ATTR_MAP` constant defined in the file `fdri_mappings.py` (in `src/gridded_metadata/`). For each entry in `ATTR_MAP` the entry key is the name of the attribute that will trigger the mapping. The value of the entry is a dictionary which has at least a `type` property.

Each of these mappings causes one or more triples to be added to the output graph. In the case of the dataset, the subject of the triple(s) will be the `fdri:GriddedDataset` resource for the dataset. In the case of arrays, the subject of the triple(s) will be the `fdri:Array` resource that represents the array.

The rest of this section lists the different types of mapping currently supported by the tool.

### Literal mapping (type='literal')

A literal mapping requires a `predicate` property whose value must be an rdflib `URIRef`. When triggered, the mapping generates a single triple for the mapping subject with the specified predicate and with the string value of the property as the string literal object of the triple.

### Annotation mapping (type='annotation')

An annotation mapping requires a `property` property whose value must be an rdflib `URIRef`.

When triggered, the mapping attaches an fdri:Annotation to the subject where the annotation property is the value provided by `property` and the annotation value is the string value of the mapped attribute.

### Agent mapping (type='agent')

An agent mapping requires a `predicate` property, and either a `name` or an `email` property (or both).

When triggered the mapping creates a new `fdri:Agent` resource. If a `name` property is present in the mapping, the `fdri:Agent` resource will be assigned a label using the value of the attribute referenced by the `name` property. If an `email` property is present, the `fdri:Agent` resource will be assigned a `foaf:mbox` using the value of the attribute referenced by the `email` property.

NOTE: When defining an `agent` mapping, the key in the ATTR_MAP should be either the property used for the agent name, or the property used for the agent email. It is not necesary to repeat the mapping for each property.