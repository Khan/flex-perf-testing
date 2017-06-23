"""This module consists of a few convenience methods for parsing data.

The input data is a series of CSV files, which are used to determine the
percentiles of the latency for various data operations. Specifically, this
script operates on a CSV file comprised of a sequence of requests to the
Standard/Flex app that log the latency of a given request.

Each row in the CSV file should consist of the following columns:
- timestamp (when the request was made)
- type (the type of the app that received the request: Flex/Standard)
- request_url (the url of the request)
- params (the params that were sent with the request)
- correct (whether the app behaved properly in response to the request)
- del_time (the latency of delete in ms)
- get_time (the latency of get in ms)
- set_time (the latency of set/put in ms)

View test.py to see how the requests are made.
"""

import argparse
import csv

import numpy as np


# the percentiles we want to extract from the data
PERCENTILES = [10.0, 50.0, 90.0, 95.0, 99.0]
# the sets of params that we want to extract percentiles from
PARAM_SETS = ["{'bytes': 10000}", "{'bytes': 100000}"]
# the columns in the data that we want to extract percentiles from
DATA_COLUMNS = ['get_time (ms)', 'set_time (ms)', 'del_time (ms)']
# the columns to write to the output file
OUTPUT_COLUMNS = ['GAE', 'endpoint', 'timestamp', 'operation', 'params',
                  'percentile', 'value']


class DataFile(object):
    """An object for extracting data from CSV files."""

    def __init__(self, filename):
        """Parse the csv file into an array of data."""
        with open(filename, 'rb') as f:
            reader = csv.DictReader(f)
            self.rows = list(reader)

    def get_column(self, params, col_name):
        """Extract a given column from the data matching a given param set."""
        # Extract the column. Note that we take str(params) because
        # the params are stored as a string in the original data file.
        column = [float(r[col_name]) for r in self.rows if
                  r['params'] == str(params)]
        print('extracting column %s with %s samples\n' %
              (col_name, len(column)))
        return column


def get_percentiles(column, percentiles):
    """Get the desired percentiles of a given dataset."""
    return {p: np.percentile(column, p) for p in percentiles}


def output_results(output_file, data_files, param_sets):
    """Print the results."""
    with open(output_file, 'wb') as file:
        # set up the writer
        wr = csv.writer(file)
        wr.writerow(OUTPUT_COLUMNS)
        # iterate through the data files
        for file in data_files:
            # create a DataFile object from the file
            data = DataFile(file)
            # iterate through the param sets we seek
            for p in param_sets:
                # iterate through the columns we're looking for
                for col in DATA_COLUMNS:
                    # get the percentiles for this column
                    res = get_percentiles(data.get_column(p, col),
                                          PERCENTILES)
                    # write out the percentiles to analysis.csv
                    for x in PERCENTILES:
                        # get the type (all rows have the same type)
                        gae_type = data.rows[0]['type']
                        # get the endpoint (all rows have the same endpoint)
                        endpoint = data.rows[0]['request_url']
                        # get the timestamp (all rows have ~ the same time)
                        timestamp = data.rows[0]['timestamp']
                        # write the row
                        wr.writerow([gae_type, endpoint, timestamp,
                                    col, p, x, res[x]])

if __name__ == '__main__':
    PARAM_SETS = None  # no special parameter sets
    # By default, you can only extract columns by specific byte size.
    # If you want to extract more specific parameter sets, use PARAM_SETS.
    # For example, set PARAM_SETS = [{'bytes': 100, 'values': 10}] to
    # extract tests on a data size of 100 B with 10 values set at once.
    # For a full list of the parameters that can be set from the data,
    # see khan-cachetest.appspot.com or ka-testing-standard.appspot.com.

    parser = argparse.ArgumentParser(description='Parse data for percentiles.')

    # add an argument for the input data files
    parser.add_argument(dest='data_files', nargs='+',
                        help='The filenames of data to parse')

    # add an argument for the parameter sets to extract
    if not PARAM_SETS:
        # If we have no set any special PARAM_SETS to extract from
        # the data, then simply take this data from the command line
        # (which only allows us to specify byte sizes).

        # The idea here is that we only want to look at the percentiles
        # for a specific set of parameters, e.g. for data sizes of 10 B.
        parser.add_argument('--num-bytes', '-b', default=[10], type=int,
                            nargs='+', help='The byte sizes to extract')

    # add an argument for the file to output to
    parser.add_argument('--output-file', '-o', default='./percentiles.csv',
                        help='The file to write the output to')

    # take input args
    args = parser.parse_args()

    # Take the param sets that we want to extract. Note that there may
    # be more params than just 'bytes' (see above) but when running from
    # the command line, only bytes can be specified.
    if not PARAM_SETS:
        PARAM_SETS = [{'bytes': n} for n in args.num_bytes]

    output_results(args.output_file, args.data_files, PARAM_SETS)
