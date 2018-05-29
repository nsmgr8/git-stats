import argparse
import logging

from .config import Config
from .gitstats import GitStats


def parse_command_args():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)


def main():
    parse_command_args()

    config = Config()
    stats = GitStats(config)
    stats.run()


main()
