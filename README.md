# Gridded Metadata Mapping Tool

## Usage

```
gridded-mapper [--type {nc,cdl,zarr,zarr-meta,auto}] [--output OUTPUT] [--base BASE_URL] file
```

The `--type` argument specifies the type of input file to read. Supported values for this argument are:

* `auto` - attempt to automatically determine the file type using the file extension
* `nc` - a netCDF file
* `cdl` - netCDF metadata in CDL format
* `zarr` - a ZARR archive or directory **NOT YET IMPLEMENTED**
* `zarr-meta` - a JSON metadata file extracted from a ZARR archive

Output is always generated as Turtle and will be written to the standard output unless an output file is specified with the `--output` argument.

The URI identifier of the dataset resource in the generated RDF will be the full path of the input file converted to a file:// URL *unless* the `--base` option is provided. If `--base` is provided, that value is used for the URI identifier of the dataset resource.

## Dev Setup

Requires Python 3.12 or greater.

Create venv and install dependencies:

```
python3 -m venv .venv
. .venv/bin/activate
pip install .[dev]
pip install -e .
```

Linting:
```
ruff check [--fix]
```

Testing:

```
pytest
```