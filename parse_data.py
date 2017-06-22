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
DATA_FILES = ['data/flex2017-06-16 11:56:20.191473.csv',
              'data/std2017-06-16 11:56:08.581900.csv']
# the sets of params that we want to extract percentiles from
PARAM_SETS = ["{'bytes': 10}", "{'bytes': 1000}"]
# the columns in the data that we want to extract percentiles from
COLUMNS = ['get_time (ms)', 'set_time (ms)', 'del_time (ms)']


class DataFile(object):
    """An object for extracting data from CSV files."""

    def __init__(self, filename):
        """Parse the csv file into an array of data."""
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # set self.rows to all data except the header row
        self.rows = rows[1:]

        # dictionary storing the column at which each attribute resides
        self.header = {}
        # the attributes in the data file
        input_header = rows[0]
        # iterate through the attributes, put their column into self.header
        for col in range(len(input_header)):
            self.header[input_header[col]] = col
        # set the type (Flex/Standard) of the data
        # all the rows in a single file should have the same type,
        # so we just extract the type from the first row
        self.type = self.rows[0][self.header['type']]

    def get_column(self, params, col_name):
        """Extract a given column from the data matching a given param set."""
        column = []
        # the column we seek to extract
        desired_col = self.get_col_number(col_name)
        # the column that contains the params of the request
        params_col = self.get_col_number('params')
        # extract the given column from all rows matching the param set
        for row in [r for r in self.rows if r[params_col] == params]:
            column.append(float(row[desired_col]))
        print('extracting column with %s samples\n' % len(column))
        return column

    def get_col_number(self, col_name):
        """Get the number of the column from the column name."""
        return self.header[col_name]


def get_percentiles(column, percentiles):
    """Get the desired percentiles of a given dataset."""
    res = {}
    for p in percentiles:
        res[p] = np.percentile(column, p)
    return res


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
                    # write out the percentiles to analysis.csv
                    for x in PERCENTILES:
                        wr.writerow([data.type, col, p, x, res[x]])

if __name__ == '__main__':
    output_results()
