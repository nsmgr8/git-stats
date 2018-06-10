import argparse
import logging

from .config import Config
from .gitstats import GitStats

log_format = '[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s'


def parse_command_args():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-f', '--force', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_format)

    return args


def main():
    args = parse_command_args()

    config = Config(**vars(args))
    stats = GitStats(config)
    stats.run()


main()
