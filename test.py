"""Run tests on flex and standard.

In this file we make a series of requests to the Flex/Standard app.
Each request runs a test on memcache, datastore, ndb, or some other data
storage service on app engine. We run a certain number of requests with
certain specific parameters (e.g. data sizes, number of entities to set,
and others - see
https://paper.dropbox.com/doc/Flex-vs-Standard-Testing-Implementation-Fxt0ipr8Og0PS8kShE8zP

The result from each request is written to a CSV file, which is then used
by parse_data.py to extract percentiles for the latencies.
"""

import argparse
import csv
import datetime
import logging
import sys

import requests
try:
    import tqdm
    progress_bar = tqdm.tqdm
except ImportError:  # No module named "tqdm"
    logging.info("To get nice progress bars, `pip install tqdm`.")

    def progress_bar(x):
        """Placeholder progress bar."""
        return x

# the data columns we expect from the server
HEADER_ROW = ['timestamp', 'type', 'request_url', 'params', 'correct',
              'del_time (ms)', 'get_time (ms)', 'set_time (ms)']


def test_request(request, params_list, num_samples, test_std):
    """Run a test on the [/profile_memcache&bytes=] endpoint."""
    # set the url
    test_url = ('https://ka-testing-standard.appspot.com/' if test_std
                else 'http://khan-cachetest.appspot.com/')
    # set the test type (for logging)
    test_type = 'std' if test_std else 'flex'

    # open the file
    with open('./data/%s%s.csv' %
              (test_type, datetime.datetime.now().strftime("%Y%m%d_%H%M%S")),
              'wb') as file:
        # set up the writer, write the header
        wr = csv.writer(file)
        wr.writerow(HEADER_ROW)

        # run tests
        for (i, params) in enumerate(params_list):
            # log status
            print('Testing %s/%s: %s (%s/%s param sets)' %
                  (test_type, request, params, i + 1, len(params_list)))

            # take required number of samples
            for sample in progress_bar(range(1, num_samples + 1)):
                # make a request and log the data
                try:
                    result = requests.get(test_url + request,
                                          params=params).json()
                    correct = result.get('correct', None)
                    del_time = result.get('del_time', 0)
                    get_time = result.get('get_time', 0)
                    set_time = result.get('set_time', 0)
                    wr.writerow([datetime.datetime.now(),  # timestamp
                                 test_type,  # type (std or flex)
                                 request,  # url
                                 params,  # number of bytes
                                 correct,  # correctness
                                 del_time * 1000,  # API gives ms
                                 get_time * 1000,
                                 set_time * 1000])
                except Exception:
                    # catch an error if the server returns something unexpected
                    logging.exception('Unexpected error (url %s): %s' %
                                      (sys.exc_info()[0], test_url + request))
            print('Finished param set %s.' % (i + 1))

if __name__ == '__main__':
    PARAM_SETS = None  # no special parameter sets
    # By default, you can specify the byte size parameter.
    # If you want to set more specific parameter sets, use PARAM_SETS.
    # For example, set PARAM_SETS = [{'bytes': 100, 'values': 10}] to
    # run a test on a data size of 100 B with 10 values set at once.
    # For a full list of the parameters that can be set from the data,
    # see khan-cachetest.appspot.com or ka-testing-standard.appspot.com.

    parser = argparse.ArgumentParser(description='Run tests on GAE.')
    parser.add_argument('--type', '-t', default='s', choices=['f', 's'],
                        help='The type of the test (f - Flex, s - Standard)')
    parser.add_argument('--num-samples', '-n', default=100, type=int,
                        help='The number of samples to run')
    parser.add_argument('--test-url', '-u', default='profile_memcache',
                        help='The endpoint to make the request to')
    if not PARAM_SETS:
        # If special param sets are not specified, set this as
        # a command line option.
        parser.add_argument('--num-bytes', '-b', default=[10], type=int,
                            nargs='+', help='The byte sizes to run tests on')

    args = parser.parse_args()

    if not PARAM_SETS:
        # PARAM_SETS has not been set, so set it equal to the
        # command line input.
        PARAM_SETS = [{'bytes': n} for n in args.num_bytes]

    test_request(args.test_url, PARAM_SETS, args.num_samples,
                 test_std=(args.type == 's'))
