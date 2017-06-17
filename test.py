"""Run tests on flex and standard."""

import requests
import csv
import sys
import datetime

# constants related to the data analysis
TEST_STD = False  # True = standard, False = flex
NUM_SAMPLES = 25000  # number of samples to take for each set of params
PARAMS = [{'bytes': 10}, {'bytes': 1000}, {'bytes': 1000000}]

# previous tests: bytes = 10, 1000, 1000000

# constants related to the specific request
REQUEST_URL = 'profile_ndb'  # the request url
# the data columns
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
    with open('./data/%s%s.csv' % (test_type, datetime.datetime.now()),
              'wb') as file:
        # set up the writer, write the header
        wr = csv.writer(file)
        wr.writerow(HEADER_ROW)

        # run tests
        for i in range(len(params_list)):
            # log status
            params = params_list[i]
            params_left = len(params_list) - (i + 1)
            sys.stdout.write('Testing %s: params %s (%s param sets left)\n' %
                             (test_type, params, params_left))

            # take required number of samples
            for sample in range(1, num_samples + 1):
                # output a status to console
                sys.stdout.write('\r- sample %s of %s' %
                                 (sample, num_samples))
                sys.stdout.flush()
                # make a request and log the data
                try:
                    result = requests.get(test_url + request,
                                          params=params).json()
                    correct = (result['correct'] if 'correct' in result
                               else None)
                    del_time = (result['del_time'] if 'del_time' in result
                                else 0)
                    get_time = (result['get_time'] if 'get_time' in result
                                else 0)
                    set_time = (result['set_time'] if 'set_time' in result
                                else 0)
                    wr.writerow([datetime.datetime.now(),  # timestamp
                                 test_type,  # type (std or flex)
                                 request,  # url
                                 params,  # number of bytes
                                 correct,  # correctness
                                 del_time * 1000,  # API gives ms
                                 get_time * 1000,
                                 set_time * 1000])
                except ValueError as err:
                    sys.stdout.write('Unexpected error: %s\n' % err)
            sys.stdout.write('\nFinished param set %s.\n' % (i + 1))

test_request(REQUEST_URL, PARAMS, NUM_SAMPLES, TEST_STD)
