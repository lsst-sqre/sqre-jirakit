
"""
Module for helper apps relating to the LSST-DM reporting cycle
"""

import itertools
from jira import JIRA

SERVER="https://jira.lsstcorp.org/"
MAX_RESULTS=None # Fetch all results

def cycles(seasons=['W', 'S'], years=range(14,22)):
    # S14 is a cycle but W14 is not
    return ["%s%d" % (s, y) for y in years for s in seasons if not (s == 'W' and y == 14)]

def build_query(issue_types, wbs):
    return 'project = DLP AND issuetype in (%s) AND wbs ~ "%s" ORDER BY wbs ASC, fixVersion DESC' % (", ".join(issue_types), wbs)

def get_issues(server, query, max_results=MAX_RESULTS):
    return JIRA(dict(server=server)).search_issues(query, maxResults=max_results)
