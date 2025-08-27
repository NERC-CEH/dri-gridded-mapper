import logging
import os.path
import pathlib
import sys
from netCDF4 import Dataset
import netcdf
import model
from fdri_mappings import ATTR_MAP


def _extract_from_nc(file_path: str) -> model.Dataset:
    dataset = Dataset(file_path)
    builder = netcdf.Builder(dataset)
    model = builder.build()
    return model

def run_main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract RDF from NetCDF files.")
    parser.add_argument("file", type=str, help="Path to the NetCDF file.")
    parser.add_argument("--base-url", type=str, help="Base URL for the dataset.", default=None)
    parser.add_argument("--output", type=str, help="Path to the output RDF file.", default=None)
    args = parser.parse_args()

    _init_logging()
    logging.info(f"Parsing model from NetCDF file {args.file}")
    dataset_model = _extract_from_nc(args.file)
    logging.info(f"Built model with {len(dataset_model.dimensions)} dimensions and {len(dataset_model.arrays)} arrays")
    base_url = args.base_url or pathlib.Path(os.path.abspath(args.file)).as_uri()
    g = model.build_graph(dataset_model, base_url, ATTR_MAP)
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
