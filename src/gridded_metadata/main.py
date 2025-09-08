import argparse
import json
import logging
import os.path
import pathlib
import sys
import tempfile

from netCDF4 import Dataset

import gridded_metadata.mapper as mapper
import gridded_metadata.model as model
import gridded_metadata.model.netcdf as netcdf
import gridded_metadata.model.zarr as zarr_model


def extract_model(file_type: str, file_path: str) -> model.Dataset:
    if file_type == 'nc':
        return _extract_from_nc(file_path)
    if file_type == 'cdl':
        tfile, tfilepath = tempfile.mkstemp('.nc')
        netcdf.cdl_to_ncd(file_path, tfilepath)
        dataset_model = _extract_from_nc(tfilepath)
        os.close(tfile)
        os.remove(tfilepath)
        return dataset_model
    if file_type == 'zarr':
        raise RuntimeError("ZARR file support is not yet implemented")
    if file_type == 'zarr-meta':
        return _extract_from_zarr_meta(file_path)
    raise ValueError(f"Unknown file type: {file_type}")

def _extract_from_nc(file_path: str) -> model.Dataset:
    dataset = Dataset(file_path)
    builder = netcdf.Builder(dataset)
    model = builder.build()
    return model

def _extract_from_zarr_meta(file_path: str) -> model.Dataset:
    with open(file_path, "r") as f:
        metadata = json.load(f)
    builder = zarr_model.Builder(metadata)
    model = builder.build()
    return model

def guess_file_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if (ext in ['.cdl', '.ncml']):
        return 'cdl'
    if (ext in ['.zarr', '.zip']):
        return 'zarr'
    if (ext in ['.json']):
        return 'zarr-meta'
    return 'nc'

def run_main() -> None:
    parser = argparse.ArgumentParser(description="Extract RDF from NetCDF files.")
    parser.add_argument("map", type=str, help="Path to the JSON mapping file.")
    parser.add_argument("file", type=str, help="Path to the NetCDF/CDL/ZARR file.")
    parser.add_argument("--type",
                        type=str,
                        help="Type of the file. nc: NetCDF, cdl: NetCDF CDL, zarr: ZARR, zarr-meta: ZARR Metadata JSON," \
                        " auto: Guess from file extension.",
                        default="auto",
                        choices=["nc", "cdl", "zarr", "zarr-meta", "auto"])
    parser.add_argument("--base-url", type=str, help="Base URL for the dataset.", default=None)
    parser.add_argument("--output", type=str, help="Path to the output RDF file.", default=None)
    args = parser.parse_args()

    _init_logging()
    file_type = args.type.lower()
    if file_type == 'auto':
        file_type = guess_file_type(args.file)

    mapping = mapper.read_mappings(args.map)

    dataset_model = extract_model(file_type, args.file)
    logging.info(f"Built model with {len(dataset_model.dimensions)} dimensions and {len(dataset_model.arrays)} arrays")
    base_url = args.base_url or pathlib.Path(os.path.abspath(args.file)).as_uri()
    g = mapper.build_graph(dataset_model, base_url, mapping)
    logging.info(f"Extracted {len(g)} RDF triples. Dataset node identifier is {base_url}")

    if args.output:
        with open(args.output, "wb") as f:
            g.serialize(f, format="turtle")
    else:
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
