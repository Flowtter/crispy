import argparse

import logging

_parser = argparse.ArgumentParser()

_parser.add_argument("-d", "--debug", help="Debug mode", action="store_true")

_parser.add_argument("-v",
                     "--verbose",
                     help="increase output verbosity",
                     action="store_true")

args = _parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
elif args.verbose:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.WARNING)
