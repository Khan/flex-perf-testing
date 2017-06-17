"""Parse the data from the csv files."""

import csv
import numpy as np
import sys

PERCENTILES = [10.0, 50.0, 90.0, 95.0, 99.0]
DATA_FILES = ['data/flex2017-06-16 11:56:20.191473.csv',
              'data/std2017-06-16 11:56:08.581900.csv']
PARAM_SETS = ["{'bytes': 10}", "{'bytes': 1000}"]
COLUMNS = ['get_time (ms)', 'set_time (ms)', 'del_time (ms)']


class DataFile:
    """An object for managing data files."""

    def __init__(self, filename):
        """Parse the csv file into an array of data."""
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            rows = []
            for row in reader:
                rows.append(row)

        self.rows = rows[1:]
        self.header = {}
        input_header = rows[0]
        for col in range(len(input_header)):
            self.header[input_header[col]] = col
        self.type = rows[1][self.header['type']]

    def get_column(self, params, col_name):
        """Extract a given column from the data for a given param set."""
        column = []
        desired_col = self.get_col_number(col_name)
        params_col = self.get_col_number('params')
        for row in [r for r in self.rows if r[params_col] == params]:
            column.append(float(row[desired_col]))
        sys.stdout.write('extracting column with %s samples\n' % len(column))
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
    with open('./analysis/ndb2.csv', 'wb') as file:
        # set up the writer
        wr = csv.writer(file)
        wr.writerow(['GAE', 'operation', 'params', 'percentile', 'value'])
        # go through the data files
        for file in DATA_FILES:
            data = DataFile(file)
            for p in PARAM_SETS:
                for col in COLUMNS:
                    res = get_percentiles(data.get_column(p, col),
                                          PERCENTILES)
                    for x in PERCENTILES:
                        wr.writerow([data.type, col, p, x, res[x]])

output_results()
