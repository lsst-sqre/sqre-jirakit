
"""
Module for helper apps relating to the LSST-DM reporting cycle
"""

import itertools

SERVER="https://jira.lsstcorp.org/"

def cycles(seasons=['W', 'S'], years=range(15,21)):
    return ["%s%d" % (s, y) for y in years for s in seasons]
