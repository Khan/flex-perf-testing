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

import csv

import numpy as np


# the percentiles we want to extract from the data
PERCENTILES = [10.0, 50.0, 90.0, 95.0, 99.0]
# the files where the raw data resides
DATA_FILES = ['data/perm/flex2017-06-21 12:48:07.647530.csv']
# the sets of params that we want to extract percentiles from
PARAM_SETS = ["{'bytes': 10}", "{'bytes': 1000}"]
# the columns in the data that we want to extract percentiles from
COLUMNS = ['get_time (ms)', 'set_time (ms)', 'del_time (ms)']


class DataFile(object):
    """An object for extracting data from CSV files."""

    def __init__(self, filename):
        """Parse the csv file into an array of data."""
        with open(filename, 'rb') as f:
            reader = csv.DictReader(f)
            self.rows = list(reader)

    def get_column(self, params, col_name):
        """Extract a given column from the data matching a given param set."""
        column = [float(r[col_name]) for r in self.rows if (r['params'] ==
                                                            params)]
        print('extracting column %s with %s samples\n' % (col_name,
                                                          len(column)))
        return column


def get_percentiles(column, percentiles):
    """Get the desired percentiles of a given dataset."""
    return {p: np.percentile(column, p) for p in percentiles}


def output_results():
    """Print the results."""
    with open('./analysis/analysis.csv', 'wb') as file:
        # set up the writer
        wr = csv.writer(file)
        wr.writerow(['GAE', 'operation', 'params', 'percentile', 'value'])
        # iterate through the data files
        for file in DATA_FILES:
            # create a DataFile object from the file
            data = DataFile(file)
            # iterate through the param sets we seek
            for p in PARAM_SETS:
                # iterate through the columns we're looking for
                for col in COLUMNS:
                    # get the percentiles for this column
                    res = get_percentiles(data.get_column(p, col),
                                          PERCENTILES)
                    print(res)
                    # write out the percentiles to analysis.csv
                    for x in PERCENTILES:
                        # get the type (all rows have the same type)
                        gae_type = data.rows[0]['type']
                        # write the row
                        wr.writerow([gae_type, col, p, x, res[x]])

if __name__ == '__main__':
    output_results()
