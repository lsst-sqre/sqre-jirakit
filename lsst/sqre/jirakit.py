
"""
Module for helper apps relating to the LSST-DM reporting cycle
"""

from __future__ import print_function

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

def compare(a, b, ordering=cycles()):
    # Returns negative if a appears before b in ordering, zero if a
    # and b are at the same position, positive if a is after b.
    return cmp(ordering.index(a), ordering.index(b))

def get_cycle(issue):
    # Return the name of the first entry in the fixVersions field of issue.
    return issue.fields.fixVersions[0].name

def good_block(blocker, blocked, compare_fn=compare):
    # Return True for a well ordered block, False for reversed
    return True if compare_fn(get_cycle(blocker), get_cycle(blocked)) <= 0 else False

def get_dependents(key, issues, visited=None):
    # Return the set of keys of all milestones which are blocked by the given key. We use
    # visited to avoid getting stuck in cycles in the graph; note that we don't report such
    # cycles explicitly, but they should usually be apparent from the bad blocks report.
    dependents = set()
    if not visited:
        visited = []
    if key not in visited:
        visited.append(key)
        for link in issues[key].fields.issuelinks:
            if (link.type.name == "Blocks" and hasattr(link, "outwardIssue")
                and link.outwardIssue.key in issues):
                if link.outwardIssue.fields.issuetype.name == "Milestone":
                    dependents.add(link.outwardIssue.key)
                dependents = dependents.union(get_dependents(link.outwardIssue.key, issues, visited))
    return dependents

def get_bad_blocks(issues, compare_fn=compare):
    # Return a list of (blocker_key, blocked_key) tuples for all bad blocks in
    # the set of issues, where a "bad block" is defined as the blocked issue
    # being scheduled for a cycle earlier than its blocker.
    return [(blocker_key, blocked_key)
            for blocker_key, blocker in issues.iteritems()
            for blocked_key in get_dependents(blocker_key, issues)
            if blocker.fields.issuetype.name == "Milestone"
            and not good_block(blocker, issues[blocked_key], compare_fn)]

def get_unscheduled_milestones(issues):
    # Return a list of keys of all Milestones which do not have a fixVersion defined.
    return [key for key, issue in issues.iteritems()
            if issue.fields.issuetype.name == "Milestone"
            and (not hasattr(issue.fields, "fixVersions")
                 or not issue.fields.fixVersions)]

def check_sanity(issues):
    errors = False
    issues = {issue.key: issue for issue in issues}

    # Check for unscheduled milestones
    unscheduled = get_unscheduled_milestones(issues)
    for key in unscheduled:
        errors=True
        del issues[key] # Trim the issue so it doesn't break the bad blocks check
        print("%s is not scheduled in any cycle." % (key,))

    # Check for bad blocks
    bad_blocks = get_bad_blocks(issues)
    for blocker, blocked in bad_blocks:
        errors = True
        print("%s (%s) blocks %s (%s)." % (blocker, get_cycle(issues[blocker]),
                                          blocked, get_cycle(issues[blocked])))

    return errors
