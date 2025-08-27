from rdflib import URIRef
from rdflib.namespace import DCTERMS, RDFS, Namespace

FDRI = Namespace("http://fdri.ceh.ac.uk/vocab/metadata/")

ATTR_MAP = {
    "title": { 'type': 'literal', 'predicate': DCTERMS.title },
    "summary": { 'type': 'literal', 'predicate': DCTERMS.description },
    "standard_name": { 'type': 'literal', 'predicate': DCTERMS.identifier },
    "long_name": { 'type': 'literal', 'predicate': RDFS.comment },
    "comment": { 'type': 'literal', 'predicate': RDFS.comment },
    "EPSG_code": {
        'type': 'annotation',
        'property': URIRef('http://fdri.ceh.ac.uk/ref/common/cop/epsg-code')
    },
    "creator_name": {
        'type': 'agent',
        'predicate': DCTERMS.creator,
        'name': 'creator_name',
        'email': 'creator_email'
    }
}
