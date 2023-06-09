"""TODO"""
import os
import sys
import json
import argparse
import inspect
import logging
import requests

from vhatable.corev2 import Processor
from vhatable.corev2 import CellToJsonUnit
from vhatable.corev2 import Time
from vhatable.factory import ProcessorBuilder
from vhatable.factory import ProcessorFactory


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


class ActionProcessor(Processor):
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


class ActionBuilder(ProcessorBuilder):
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
    builder = ProcessorBuilder().use_api(api)
    factory = ProcessorFactory(builder=builder)

    builder = ActionBuilder(endpoint=api).use_api(api)
    factory.set_action("an_action", builder, ActionProcessor)
    return factory


def helper_print_header(extra=None):
    """Just a tiny helper to display a header between each rendering."""
    print("")
    print("=========================================")
    if extra:
        print(extra)
    print("")


def sample1():
    """Just a sample"""

    # simulate user input using, for example cli with argparse
    args = argparse.Namespace(
            debug=0,
            sort_reverse=False,
            sort_sort_by="season",
            release_dates=[],
            slice_end=2,
            slice_limit=20,
            # Flag that will trigger our processor.
            an_action=True,
            vertical=False)

    factory = newfactory()
    processor = factory.build(args)

    print(processor)
    helper_print_header("    >>>> Default  <<<<")
    processor.run()
    print()


def main():
    """ Main entrypoint of this sample program."""
    logging.basicConfig(level=logging.INFO)
    map_sample = {}
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj) and name.startswith('sample'):
            map_sample[name] = obj

    parser = argparse.ArgumentParser(description='Display some samples')
    parser.add_argument(
        'sample', choices=map_sample.keys(),
        help='Choose the sample to display.')
    args = parser.parse_args()

    obj = map_sample[args.sample]
    print("Sample : ", args.sample, " :", obj.__doc__)
    obj()
