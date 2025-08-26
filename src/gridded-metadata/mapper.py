import logging
import sys
from rdflib import FOAF, RDFS, BNode, Graph, Namespace, URIRef, Literal
from rdflib.collection import Collection
from rdflib.namespace import RDF, SDO
from netCDF4 import Dataset, Variable
import pathlib
import os.path
from fdri_mappings import FDRI, ATTR_MAP

def extract_from_nc(file_path: str, base_url: str|None = None) -> Graph:
    graph = Graph()
    graph.namespace_manager.bind("fdri", FDRI)
    dataset = Dataset(file_path)
    base_url = base_url or pathlib.Path(os.path.abspath(file_path)).as_uri()
    # Create fdri:GriddedDataset resources
    ds_node = URIRef(f"{base_url}")
    graph.add((ds_node, RDF.type, FDRI.GriddedDataset))

    # Extract dataset metadata from global attributes
    extract_attrs(dataset, graph, ds_node)

    # Extract variables
    extract_variables(dataset, graph, base_url, ds_node)
    return graph

def attr_value_as_node(value):
    if value is None:
        return None
    if isinstance(value, str):
        return URIRef(value) if value.startswith("http") else Literal(value)
    logging.warning(f'Failed to map value {value} as an RDF value node')
    return None

def apply_mapping(container: Dataset | Variable, graph: Graph, container_node: URIRef, attr: str, mapping: dict) -> None:
    if not 'type' in mapping:
        return
    predicate = mapping['predicate'] if 'predicate' in mapping else None
    if mapping['type'] == 'literal':
        if not predicate:
            logging.warning(f"No predicate for literal mapping of attribute {attr}")
            return
        value = container.getncattr(attr) if attr in container.ncattrs() else None
        value_node = attr_value_as_node(value)
        if value_node:
            graph.add((container_node, predicate, value_node))
    elif mapping['type'] == 'agent':
        if not predicate:
            logging.warning(f"No predicate for agent mapping of attribute {attr}")
            return
        email = container.getncattr(mapping['email']) if mapping['email'] in container.ncattrs() else None
        email_node = attr_value_as_node(email)
        name = container.getncattr(mapping['name']) if mapping['name'] in container.ncattrs() else None
        name_node = attr_value_as_node(name)
        if name_node:
            agent_node = BNode()
            graph.add((container_node, predicate, agent_node))
            graph.add((agent_node, RDF.type, FDRI.Agent))
            graph.add((agent_node, RDFS.label, name_node))
            if email_node:
                graph.add((agent_node, FOAF.mbox, email_node))
    elif mapping['type'] == 'annotation':
        property = mapping['property']
        if not property:
            logging.warning(f"No property for annotation mapping of attribute {attr}")
            return
        value = container.getncattr(attr) if attr in container.ncattrs() else None
        value_node = attr_value_as_node(value)
        if not value_node:
            logging.warning(f"Failed to map value of attribute {attr} as RDF node")
            return
        annotation_node = BNode()
        graph.add((annotation_node, RDF.type, FDRI.Annotation))
        graph.add((annotation_node, FDRI.property, property))
        annotation_value_node = BNode()
        graph.add((annotation_node, FDRI.hasValue, annotation_value_node))
        graph.add((annotation_value_node, RDF.type, SDO.PropertyValue))
        graph.add((annotation_value_node, SDO.value, value_node))
        graph.add((container_node, FDRI.hasAnnotation, annotation_node))

def extract_attrs(dataset: Dataset | Variable, graph: Graph, ds_node: URIRef) -> None:
    dataset_attrs = dataset.ncattrs()
    for attr, mapping in ATTR_MAP.items():
        if attr in dataset_attrs:
            apply_mapping(dataset, graph, ds_node, attr, mapping)

def extract_variables(dataset: Dataset, graph: Graph, base_url: str, ds_node: URIRef) -> None:
    for var_name, var in dataset.variables.items():
        var_node = URIRef(f"{base_url}#{var_name}")
        graph.add((var_node, RDF.type, FDRI.Array))
        graph.add((var_node, RDFS.label, Literal(var_name)))
        graph.add((ds_node, FDRI.contains, var_node))
        extract_attrs(var, graph, var_node)
        if var.ndim == 1 and dataset.dimensions.get(var_name) is not None:
            graph.add((var_node, FDRI.isCoordinate, Literal(True)))
            graph.add((var_node, FDRI.size, Literal(var.shape[0])))
        else:
            for dim in var.get_dims():
                dim_node = URIRef(f"{base_url}#{dim.name}")
                graph.add((var_node, FDRI.references, dim_node))
                if not (dim.name in dataset.variables):
                    # Reference to a dimension with no co-ordinate variable
                    graph.add((dim_node, RDF.type, FDRI.Dimension))
                    dim_size = dataset.dimensions[dim.name].size
                    graph.add((dim_node, FDRI.size, Literal(dim_size)))
            if var.ndim > 1:
                # Add a size collection for the dimension
                size_node = BNode()
                size_coll = Collection(graph, size_node)
                for s in var.shape:
                    size_coll.append(Literal(s))
                graph.add((var_node, FDRI.size, size_node))
                

def run_main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract RDF from NetCDF files.")
    parser.add_argument("file", type=str, help="Path to the NetCDF file.")
    parser.add_argument("--base-url", type=str, help="Base URL for the dataset.", default=None)
    args = parser.parse_args()
    
    g = extract_from_nc(args.file, args.base_url)
    print(g.serialize(format="turtle"))

def _init_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    h1 = logging.FileHandler("mapper.log")
    h1.setFormatter(formatter)
    h1.setLevel(logging.INFO)
    h2 = logging.StreamHandler(sys.stderr)
    h2.setFormatter(formatter)
    h2.addFilter(lambda record: record.levelno >= logging.ERROR)
    h2.setLevel(logging.ERROR)

    logger.addHandler(h1)
    logger.addHandler(h2)

if __name__ == "__main__":
    run_main()
