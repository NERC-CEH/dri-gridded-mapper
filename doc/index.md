# FDRI Gridded Data Mapping Tool

The mapping tool reads metadata from netCDF and ZARR archives and creates RDF representing the input file as an `fdri:GriddedDataset` with metadata properties taken from any top-level attributes in the metadata (in the root group, in the case of ZARR), and with the dimensions and arrays defined in the metadata also included.

The mapping of structural metadata is fixed. For dimensions, the dimension name and its size are extracted. For arrays, the shape of the array, the dimensions and/or arrays it references, and additional metatdata properties are extracted.

The mapping of attributes of the dataset and of each array in the dataset is configured using a mapping file passed as an argument to the mapping tool.

## Metadata mapping file

The metadata mapping file is a JSON file containing a single JSON object with two properties.

The `namespaces` property has a value which is a JSON object mapping prefixes to their full URI expansion.

The `mappings` property has a value which is a JSON object mapping gridded metadata attribute names to the mapping to apply when that attribute is encountered. Each mapping is defined by an object which has a required `type` property and some additional properties depending on the type of mapping.

Each of these mappings causes one or more triples to be added to the output graph. In the case of the dataset, the subject of the triple(s) will be the `fdri:GriddedDataset` resource for the dataset. In the case of arrays, the subject of the triple(s) will be the `fdri:Array` resource that represents the array.

The rest of this section lists the different types of mapping currently supported by the tool.

### Literal mapping (type='literal')

A literal mapping requires a `predicate` property whose value must be URI or a CURIE (which will be expanded using the prefix mappings declared in `namespaces`).

When triggered, the mapping generates a single triple for the mapping subject with the specified predicate and with the string value of the property as the string literal object of the triple.

### Annotation mapping (type='annotation')

An annotation mapping requires a `property` property whose value must be a URI or CURIE (expanded using the prefix mappings in `namespaces`).

When triggered, the mapping attaches an `fdri:Annotation` resources to the subject (using the `fdri:hasAnnotation` predicate). The annotation property is the value provided by `property` and the annotation value is the string value of the mapped attribute.

### Agent mapping (type='agent')

An agent mapping requires a `predicate` property, and either a `name` or an `email` property (or both). The `predicate` property must be a URI or a CURIE. The `name` and `email` properties should be the names of metadata attributes.

When triggered the mapping creates a new `fdri:Agent` resource. If a `name` property is present in the mapping, the `fdri:Agent` resource will be assigned a label using the value of the attribute referenced by the `name` property. If an `email` property is present, the `fdri:Agent` resource will be assigned a `foaf:mbox` using the value of the attribute referenced by the `email` property.

NOTE: When defining an `agent` mapping, the key in `mappings` should be either the name of the attribute used for the agent name, or the name of the attribute used for the agent email. It is not necesary to repeat the mapping for each of these attributes.

An example mapping is shown below.

```json
{
    "namespaces": {
        "dcterms": "http://purl.org/dc/terms/",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
    },
    "mappings": {
        "title": {
            "type": "literal",
            "predicate": "dcterms:title"
        },
        "summary": {
            "type": "literal",
            "predicate": "dcterms:description"
        },
        "standard_name": {
            "type": "literal",
            "predicate": "dcterms:identifier"
        },
        "long_name": {
            "type": "literal",
            "predicate": "dcterms:title"
        },
        "comment": {
            "type": "literal",
            "predicate": "rdfs:comment"
        },
        "EPSG_code": {
            "type": "annotation",
            "property": "http://fdri.ceh.ac.uk/ref/common/cop/epsg-code"
        },
        "creator_name": {
            "type": "agent",
            "predicate": "dcterms:creator",
            "name": "creator_name",
            "email": "creator_email"
        }
    }
}
```