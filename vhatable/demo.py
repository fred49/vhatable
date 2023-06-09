"""TODO"""
import os
import json
import argparse
import logging
import requests

from vhatable.processors import Processor
from vhatable.units import CellToJsonUnit
from vhatable.corev2 import Time
from vhatable.processors import ProcessorBuilder
from vhatable.processors import ProcessorFactory


class API:
    """TODO"""
    URL = "https://epguides.frecar.no/show/bigbangtheory/"
    cacheFileName = "/tmp/vhatable-cache-big-bang.json"

    def __init__(self):
        self.data = self._load_json()

    def _load_json(self):
        """TODO"""
        # pylint: disable=unspecified-encoding
        data = None
        if os.path.isfile(self.cacheFileName):
            with open(self.cacheFileName) as user_file:
                file_contents = user_file.read()
                data = json.loads(file_contents)
        else:
            data = requests.get(self.URL, timeout=60).json()
            with open(self.cacheFileName, 'w') as json_file:
                json.dump(data, json_file)
        res = {}
        cpt = 0
        for season in data:
            for episode in data[season]:
                cpt += 1
                episode['ID'] = cpt
                res[cpt] = episode
        return res

    def list(self):
        """TODO"""
        return self.data.values()

    def column_names(self):
        """TODO"""
        return ["ID", "season", "number", "title", "release_date", "show"]

    def delete(self, row):
        """TODO"""
        self.data.pop(row['ID'])


class DeleteProcessor(Processor):
    """TODO"""

    def __init__(self, *args, endpoint=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = endpoint
        self.add_transform_unit(
                'json', CellToJsonUnit, dump=False, raw=True)

    def post_init(self):
        """TODO"""
        super().post_init()
        self.units['json'].required_columns = self.column_names

    @Time('vhatable.corev2.run')
    def run(self):
        """TODO"""
        print("len:", len(self.endpoint.list()))
        for row in self.get_raw():
            print(" - ", row)
        for row in self.get_raw():
            self.endpoint.delete(row)
        print()
        print("len:", len(self.endpoint.list()))
        print(
            "Only the 2 selected lines by the processor were removed :)")
        print()
        return True


class ApiProcessorBuilder(ProcessorBuilder):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, *args, endpoint=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = endpoint

    def _post_create_hook(self, processor):
        processor.endpoint = self.endpoint
        return processor


def newfactory():
    """TODO"""
    api = API()
    factory = ProcessorFactory()
    factory.set_default_processor_builder(
        ProcessorBuilder().use_api(api)
    )
    factory.add_processor(
            "delete",
            ApiProcessorBuilder(endpoint=api).use_api(api),
            DeleteProcessor)
    return factory


def add_default_options(parser):
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
            "-d",
            "--debug", type=int,
            help="debug level",
            dest="debug")
    parser.add_argument(
            "--sort-by",
            help="sort row by column",
            dest="sort_sort_by")
    parser.add_argument(
            "--sort-reversed",
            help="sort row by column",
            default=False, action="store_true",
            dest="sort_reverse")


def command_list(args):
    """This command will list all seasons and episodes stored in the cache."""
    factory = newfactory()
    processor = factory.create(args)
    print(processor)
    processor.run()
    print()


def main():
    """ Main entrypoint of this sample program."""
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Demo cli")
    add_default_options(parser)

    parser.add_argument(
        'command', choices=["list", "delete", "update"],
        help="Choose the command you want to trigger")
    args = parser.parse_args()
    command = globals()["command_" + args.command]
    print("Demo: ", args.command, ":", command.__doc__)
    command(args)
