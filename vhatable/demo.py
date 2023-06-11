"""TODO"""
import os
import sys
import json
import argparse
import logging
from datetime import datetime
import requests

from vhatable.cellv2 import ComplexCellBuilder
from vhatable.corev2 import Unit
from vhatable.corev2 import Time
from vhatable.filters import PartialOr
from vhatable.filtersv2 import EqualOr
from vhatable.filtersv2 import PartialAnd
from vhatable.processors import ProcessorBuilder
from vhatable.processors import ProcessorFactory
from vhatable.processors import API
from vhatable.processors import Processor
from vhatable.units import CellToJsonUnit


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
        self.data.pop(row_id)
        self._persist(self.data)

    def get(self, row_id):
        row_id = str(row_id)
        row = self.data.get(row_id)
        if row is None:
            raise ValueError("row id not found " + row_id)
        return row

    def update(self, row):
        row_id = str(row['ID'])
        old_row = self.data[row_id]
        if old_row != row:
            self.data[row_id] = row
            self._persist(self.data)
        return row


api = DemoAPI()


class UpdateUnit(Unit):
    """TODO"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notes = None
        self._attrs += ["notes"]

    def __call__(self, rows):
        for row in rows:
            if self.notes is not None:
                row['notes'] = self.notes
            yield row


class UpdateProcessor(Processor):
    """TODO"""

    def __init__(self, *args,  messages=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_transform_unit(
                'json', CellToJsonUnit, dump=False, raw=True)
        self.add_transform_unit('update', UpdateUnit)
        self.messages = {
            "nothing_to_update": "Nothing to update.",
            "updated": (
                "{_position}/{_count}: "
                "The ressource '{name}' ({uuid}) was updated. ({_time}s)"
            )
        }
        if messages:
            self.messages.update(messages)

    def post_init(self):
        """TODO"""
        super().post_init()
        self.units['json'].required_columns = self.column_names

    @Time('vhatable.update.run')
    def run(self):
        """TODO"""
        default_context = {
            "name": None,
            "uuid": None,
            "_time": 0,
            "_position": 0,
            "_count": len(self.get_raw())
        }
        position = 0
        if default_context['_count'] == 0:
            msg = self.messages['nothing_to_update']
            self.log.debug(msg)
            print(msg)
        for row in self.get_raw():
            position += 1
            before = datetime.now()
            self.api.update(row)
            after = datetime.now()
            context = {
                **default_context,
                **row,
                "_position": position,
                "_time": after - before
            }
            msg = self.messages['updated'].format(**context)
            self.log.debug(msg)
            print(msg)
        print()
        return True


def newfactory():
    """TODO"""
    messages = {
        "deleted": (
            "{_position}/{_count}: "
            "The episode '{title}' ({ID}) was deleted. ({_time}s)"
        ),
        "count_elt": "Episodes found: {count}",
        "nothing_to_update": "Nothing to update.",
        "updated": (
            "{_position}/{_count}: "
            "The episode '{title}' ({ID}) was updated. ({_time}s)"
        )
    }
    factory = ProcessorFactory()
    factory.set_default_processor_builder(
        ProcessorBuilder(
            api=api,
            messages=messages
        ).use_api(api)
    )
    factory.add_processor(
        "update",
        ProcessorBuilder(
            api=api,
            messages=messages
        ).use_api(api),
        UpdateProcessor)
    factory.set_custom_cell(
            "show", ComplexCellBuilder(
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
            help="sort row by column",
            default=False, action="store_true",
            dest="sort_reverse")


def add_list_command(main_subparsers):
    """TODO"""

    def command(args):
        """This command will remove an episode from the cache."""
        factory = newfactory()
        factory.add_filters(PartialAnd("title", args.titles))
        factory.add_filters(PartialOr("release_date", args.release_dates))
        factory.add_filters(PartialOr("season", args.seasons))
        factory.add_filters(PartialOr("number", args.episodes))
        factory.add_filters(EqualOr("ID", args.ids))
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
        factory.default_proc = "delete"
        factory.add_filters(EqualOr("ID", args.ids))
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
        factory.default_proc = "delete"
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
        factory.default_proc = "update"
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
