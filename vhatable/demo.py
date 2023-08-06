"""TODO"""
import os
import sys
import json
import argparse
import logging
import requests

from vhatable.cellv2 import ComplexCellBuilder
from vhatable.filters import PartialOr
from vhatable.filtersv2 import EqualMultipleOr
from vhatable.filtersv2 import PartialMultipleAnd
from vhatable.processors import ProcessorBuilder
from vhatable.processors import ProcessorFactory
from vhatable.processors import API
from vhatable.processors import UpdateProcessor
from vhatable.units import UpdateRowsUnit


class DemoAPI(API):
    """TODO"""
    URL = "https://epguides.frecar.no/show/bigbangtheory/"
    cacheFileName = "/tmp/vhatable-demo--cache-big-bang.json"

    def __init__(self):
        super().__init__()
        self.data = self._load_json()

    def _persist(self, data):
        # pylint: disable=unspecified-encoding
        with open(self.cacheFileName, 'w') as json_file:
            json.dump(data, json_file)

    def reset(self):
        """remove cache file to reset the current state"""
        os.remove(self.cacheFileName)

    def _load_json(self):
        """TODO"""
        # pylint: disable=unspecified-encoding
        data = None
        if os.path.isfile(self.cacheFileName):
            with open(self.cacheFileName) as user_file:
                file_contents = user_file.read()
                data = json.loads(file_contents)
            return data

        data = requests.get(self.URL, timeout=60).json()
        res = {}
        cpt = 0
        for season in data:
            for episode in data[season]:
                cpt += 1
                episode['ID'] = cpt
                episode['notes'] = "TODO"
                res[cpt] = episode
        self._persist(res)
        return res

    def list(self):
        """TODO"""
        return self.data.values()

    def column_names(self):
        """TODO"""
        return ["ID", "season", "number", "title", "release_date", "show",
                "notes"]

    def delete(self, row):
        """TODO"""
        row_id = str(row['ID'])
        row = self.data.pop(row_id)
        self._persist(self.data)
        return True, row

    def get(self, row_id):
        row_id = str(row_id)
        row = self.data.get(row_id)
        if row is None:
            raise ValueError("row id not found " + row_id)
        return row

    def update(self, row):
        row_id = str(row['ID'])
        old_row = self.data.get(row_id)
        if old_row is None:
            raise ValueError("row id not found " + row_id)
        if old_row != row:
            self.data[row_id] = row
            self._persist(self.data)
        return True, row


api = DemoAPI()


def newfactory():
    """TODO"""
    messages = {}
    messages['delete'] = {
        "nothing_to_do": "Nothing to delete.",
        "done": (
            "{prefix}{_position}/{_count}: "
            "The episode '{title}' ({ID}) was deleted. ({_time}s)"
        ),
        "done_failure": (
            "{prefix}{_position}/{_count}: Failure "
            "The episode '{title}' ({ID}) was not deleted. ({_time}s)"
        )
    }
    messages['update'] = {
        "nothing_to_do": "Nothing to update.",
        "done": (
            "{prefix}{_position}/{_count}: "
            "The episode '{title}' ({ID}) was updated. ({_time}s)"
        ),
        "done_failure": (
            "{prefix}{_position}/{_count}: Failure "
            "The episode '{title}' ({ID}) was not updated. ({_time}s)"
        )
    }
    messages['count'] = {
        "count_elt": "Episodes found: {count}"
    }
    factory = ProcessorFactory()
    factory.set_default_processor_builder(
        ProcessorBuilder(
            api=api,
            autoload=True,
            messages=messages
        )
    )
    factory.add_processor(
        "update",
        UpdateProcessor,
        builder=ProcessorBuilder(
            api=api,
            autoload=True,
            # we override default updatable columns,
            # only notes is updatable
            units=[UpdateRowsUnit(["notes"])],
            messages=messages
        ))
    factory.add_custom_cell(
        ComplexCellBuilder(
            "show",
            fmt='{title} {imdb_id} {epguide_name}',
            fmtv='{title} {imdb_id} {epguide_name}'
        )
    )
    factory.set_align_cell("title", "l")
    factory.set_align_cell("show", "c")
    factory.set_header_cell("number", "episode")
    return factory


def add_list_cmd_options(parser):
    """Add all default option to the current parser."""
    parser.add_argument(
            "--count",
            default=False, action="store_true",
            help="Count the number of the displayed rows",
            dest="count")
    parser.add_argument(
            "--vertical",
            default=False, action="store_true",
            help="Use vertical display",
            dest="vertical")
    parser.add_argument(
            "--json",
            default=False, action="store_true",
            help="Display rows as json",
            dest="json")
    parser.add_argument(
            "--json-raw",
            default=False, action="store_true",
            help="Display raw json",
            dest="json_raw")
    parser.add_argument(
            "--csv",
            default=False, action="store_true",
            help="Display rows as csv",
            dest="csv")
    parser.add_argument(
            "--start",
            default=0, type=int,
            help="Only display the N first rows",
            dest="slice_start")
    parser.add_argument(
            "--end",
            default=0, type=int,
            help="Only display the N last rows",
            dest="slice_end")
    parser.add_argument(
            "--limit",
            default=0, type=int,
            help="limit the number of rows to display",
            dest="slice_limit")
    parser.add_argument(
            "--sort-by",
            help="sort row by column",
            dest="sort_sort_by")
    parser.add_argument(
            "--sort-reversed",
            help="Reverse order while sorting",
            default=False, action="store_true",
            dest="sort_reverse")


def add_list_command(main_subparsers):
    """TODO"""

    def command(args):
        """This command will remove an episode from the cache."""
        factory = newfactory()
        factory.add_filters(PartialMultipleAnd("title", args.titles))
        factory.add_filters(PartialOr("release_date", args.release_dates))
        factory.add_filters(PartialOr("season", args.seasons))
        factory.add_filters(PartialOr("number", args.episodes))
        factory.add_filters(EqualMultipleOr("ID", args.ids))
        processor = factory.create(args)
        print(processor)
        processor.run()
        print()

    parser = main_subparsers.add_parser('list')
    parser.set_defaults(func=command)
    add_list_cmd_options(parser)

    parser.add_argument(
            "titles",
            nargs='*',
            help="Filter by title")

    parser.add_argument(
            "--release-date", action="append",
            help="Filter by release date",
            dest="release_dates")

    parser.add_argument(
            "--season", action="append",
            help="Filter by season",
            dest="seasons")

    parser.add_argument(
            "--id",
            action="append", type=int,
            help="Filter by id",
            dest="ids")

    parser.add_argument(
            "--episode", action="append",
            help="Filter by episode",
            dest="episodes")

    parser.add_argument(
            "--delete", default=False, action="store_true",
            help="Delete selected rows",
            dest="delete")

    parser.add_argument(
            "--update", default=False, action="store_true",
            help="update selected rows",
            dest="update")

    parser.add_argument(
            "--notes", default=None, action="store",
            help="update notes column",
            dest="update_notes")
    parser.add_argument(
            "--update-title", default=None, action="store",
            help="update title column",
            dest="update_title")


def add_delete_command(main_subparsers):
    """TODO"""

    def command(args):
        """This command will remove some episode from the list.
        This implementation is not the best since we load the entire of
        episodes and we filter them.
        Another solution: We can use the list of IDs to retrieve episode one by
        one and then build a list of them. No more filtering.
        A more performant implementation.
        """
        factory = newfactory()
        factory.default_processor_identifier = "delete"
        factory.add_filters(EqualMultipleOr("ID", args.ids))
        processor = factory.create(args)
        print(processor)
        processor.run()
        print()

    parser = main_subparsers.add_parser('delete')
    parser.set_defaults(func=command)
    parser.add_argument(
            "ids",
            nargs='+', type=int,
            help="Delete episode by id")


def add_delete_commandv2(main_subparsers):
    """TODO"""

    def command(args):
        """This command will remove some episode from the list.
        We retrieve episode one by one and then build a list
        of them. No more filtering.
        A more performant implementation.
        """
        rows = []
        for row_id in args.ids:
            rows.append(api.get(row_id))

        factory = newfactory()
        factory.default_processor_identifier = "delete"
        processor = factory.create(args)
        processor.load(rows)
        print(processor)
        processor.run()
        print()

    parser = main_subparsers.add_parser('deletev2')
    parser.set_defaults(func=command)
    parser.add_argument(
            "ids",
            nargs='+', type=int,
            help="Delete episode by id")


def add_reset_command(main_subparsers):
    """TODO"""

    def command(args):
        """Reset the local cache"""
        # pylint: disable=unused-argument
        api.reset()

    parser = main_subparsers.add_parser('reset')
    parser.set_defaults(func=command)


def add_update_command(main_subparsers):
    """TODO"""

    def command(args):
        """This command will remove some episode from the list.
        We retrieve episode one by one and then build a list
        of them. No more filtering.
        A more performant implementation.
        """
        rows = []
        for row_id in args.ids:
            rows.append(api.get(row_id))

        factory = newfactory()
        factory.default_processor_identifier = "update"
        processor = factory.create(args)
        processor.load(rows)
        print(processor)
        processor.run()
        print()

    parser = main_subparsers.add_parser('update')
    parser.set_defaults(func=command)
    parser.add_argument(
            "ids",
            nargs='+', type=int,
            help="Update episode by id")
    parser.add_argument(
            "--notes", default=None, action="store",
            help="update notes column",
            dest="update_notes")
    parser.add_argument(
            "--title", default=None, action="store",
            help="update title column",
            dest="update_title")


def main():
    """ Main entrypoint of this sample program."""
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    stdout = logging.StreamHandler(sys.stdout)
    fmt = '%(asctime)s:%(name)s:%(funcName)s:%(levelname)s:%(message)s'
    formatter = logging.Formatter(fmt)
    stdout.setFormatter(formatter)
    log.addHandler(stdout)

    main_parser = argparse.ArgumentParser(description="Demo cli")
    main_parser.add_argument(
            "-d",
            "--debug", type=int,
            default=0,
            help="debug level",
            dest="debug")
    main_subparsers = main_parser.add_subparsers()

    add_list_command(main_subparsers)
    add_delete_command(main_subparsers)
    add_delete_commandv2(main_subparsers)
    add_reset_command(main_subparsers)
    add_update_command(main_subparsers)

    args = main_parser.parse_args()
    if args.debug >= 1:
        log.setLevel(logging.DEBUG)
    if "func" in args:
        print("Demo: ", args.func.__doc__ + "\n")
        sys.exit(args.func(args))
    else:
        print("ERROR: Missing command. see -h")
        sys.exit(2)
