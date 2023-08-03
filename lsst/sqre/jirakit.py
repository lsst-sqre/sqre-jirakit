"""
Module for helper apps relating to the LSST-DM reporting cycle and LSST-SIMS work planning.
"""

from __future__ import print_function

import re
from io import StringIO

from jira import JIRA

SERVER = "https://jira.lsstcorp.org/"
MAX_RESULTS = None  # Fetch all results


def cycles():
    return [
        "S14",
        "W15",
        "S15",
        "W16",
        "X16",
        "F16",
        "S17",
        "F17",
        "S18",
        "F18",
        "S19",
        "F19",
        "S20",
        "F20",
        "S21",
        "F21",
        "W21",  # At time of writing, W21 is defined in JIRA.
        "S22",
        "F22",
        "W22",
    ]


def build_query(issue_types, wbs):
    if wbs is None:
        return (
            "project = DLP AND issuetype in (%s) "
            "ORDER BY key ASC, fixVersion DESC" % (", ".join(issue_types))
        )
    else:
        return (
            'project = DLP AND issuetype in (%s) AND wbs ~ "%s"'
            "ORDER BY wbs ASC, fixVersion DESC" % (", ".join(issue_types), wbs)
        )


def basic_auth_from_file(auth_file_path=None):
    """Get basic auth from a two line file."""
    if auth_file_path is None:
        import os

        auth_file_path = os.path.join(os.path.expanduser("~/"), ".jira_auth")

    with open(auth_file_path, "r") as fd:
        uname = fd.readline().strip()  # Can't hurt to be paranoid
        pwd = fd.readline().strip()

    return (uname, pwd)


def get_issue_links(issue, linkTypeName=None):
    """Get links from an issue."""
    links = issue.fields.issuelinks
    if linkTypeName is None:
        return links
    else:
        return [link for link in links if link.type.name in linkTypeName]


def get_issues(server, query, max_results=MAX_RESULTS):
    return JIRA(dict(server=server)).search_issues(query, maxResults=max_results)


def get_issues_by_key(server, keys):
    # Given an iterable of issue keys (DM-1234, DLP-543)
    # return all in a list. Currently there may be issues if the key list
    # is extremely long.
    # convert the list to an "in" query
    query = "issuekey in (" + " ,".join(keys) + ")"
    return get_issues(server, query, max_results=None)


def compare(a, b, ordering=list(cycles())):
    # Returns negative if a appears before b in ordering, zero if a
    # and b are at the same position, positive if a is after b.
    if ordering.index(a) < ordering.index(b):
        return -1
    elif ordering.index(a) == ordering.index(b):
        return 0
    else:
        return 1


def get_cycle(issue):
    # Return the name of the first entry in the fixVersions field of issue.
    return issue.fields.fixVersions[0].name


def good_block(blocker, blocked, compare_fn=compare):
    # Return True for a well ordered block, False for reversed
    return True if compare_fn(get_cycle(blocker), get_cycle(blocked)) <= 0 else False


def get_dependents(key, issues, visited=None):
    # Return the set of keys of all milestones which are blocked by the given
    # key. We use visited to avoid getting stuck in cycles in the graph; note
    # that we don't report such cycles explicitly, but they should usually be
    # apparent from the bad blocks report.
    dependents = set()
    if not visited:
        visited = []
    if key not in visited:
        visited.append(key)
        for link in issues[key].fields.issuelinks:
            if (
                link.type.name == "Blocks"
                and hasattr(link, "outwardIssue")
                and link.outwardIssue.key in issues
            ):
                if link.outwardIssue.fields.issuetype.name == "Milestone":
                    dependents.add(link.outwardIssue.key)
                dependents = dependents.union(
                    get_dependents(link.outwardIssue.key, issues, visited)
                )
    return dependents


def get_bad_blocks(issues, compare_fn=compare):
    # Return a list of (blocker_key, blocked_key) tuples for all bad blocks in
    # the set of issues, where a "bad block" is defined as the blocked issue
    # being scheduled for a cycle earlier than its blocker.
    return [
        (blocker_key, blocked_key)
        for blocker_key, blocker in issues.items()
        for blocked_key in get_dependents(blocker_key, issues)
        if blocker.fields.issuetype.name == "Milestone"
        and not good_block(blocker, issues[blocked_key], compare_fn)
    ]


def get_unscheduled_milestones(issues):
    # Return a list of keys of all Milestones which do not have a fixVersion
    # defined.
    return [
        key
        for key, issue in issues.items()
        if issue.fields.issuetype.name == "Milestone"
        and (not hasattr(issue.fields, "fixVersions") or not issue.fields.fixVersions)
    ]


def get_multiply_scheduled_milestones(issues):
    # Return a list of keys of all Milestones which have more than one
    # fixVersion defined.
    return [
        key
        for key, issue in issues.items()
        if issue.fields.issuetype.name == "Milestone"
        and hasattr(issue.fields, "fixVersions")
        and len(issue.fields.fixVersions) > 2
    ]


def get_scheduled_issues(issues, issuetype):
    # Return a list of keys of all issues of type issuetype which have a
    # fixVersion defined.
    return [
        key
        for key, issue in issues.items()
        if issue.fields.issuetype.name == issuetype
        and hasattr(issue.fields, "fixVersions")
        and len(issue.fields.fixVersions) > 0
    ]


def check_sanity(issues):
    output = StringIO()
    issues = {issue.key: issue for issue in issues}

    # Check for unscheduled milestones
    for key in sorted(get_unscheduled_milestones(issues)):
        output.write(
            "Milestone %s [%s] is not scheduled in any cycle.\n"
            % (key, issues[key].fields.customfield_10500)
        )
        del issues[key]  # Trim the issue so it doesn't break the bad blocks check

    # Check for milestones which are scheduled in more than one cycle
    for key in sorted(get_multiply_scheduled_milestones(issues)):
        output.write(
            "Milestone %s [%s] scheduled in multiple cycles: %s.\n"
            % (
                key,
                issues[key].fields.customfield_10500,
                ", ".join(v.name for v in issues[key].fields.fixVersions),
            )
        )

    # Check for meta-epics which are schedule (they shouldn't be)
    for key in sorted(get_scheduled_issues(issues, "Meta-epic")):
        issue = issues[key]
        output.write(
            "%s %s [%s] has been scheduled: %s.\n"
            % (
                issue.fields.issuetype.name,
                key,
                issue.fields.customfield_10500,
                ", ".join(v.name for v in issues[key].fields.fixVersions),
            )
        )

    # Check for bad blocks
    bad_blocks = get_bad_blocks(issues)
    for blocker, blocked in bad_blocks:
        output.write(
            "%s (%s) [%s] blocks %s (%s) [%s].\n"
            % (
                blocker,
                get_cycle(issues[blocker]),
                issues[blocker].fields.customfield_10500,
                blocked,
                get_cycle(issues[blocked]),
                issues[blocked].fields.customfield_10500,
            )
        )

    return output.getvalue()


def dm_to_dlp_cycle(dmcycle):
    # DM Project  | DLP Project
    #
    # Spring 1234 | S34
    # Summer 1234 | S34
    # Extra 1234  | X34
    # Fall 1234   | F34
    # Winter 1234 | W34
    # [There is no year with both spring & summer]
    matcher = re.compile(r"\w?([SWxF])\w+\s\d*(\d\d)$")
    matched = matcher.search(str(dmcycle))
    if matched:
        parts = matched.groups()
        return "{0}{1}".format(*(s.upper() for s in parts))
    else:
        raise ValueError("Supplied cycle {} is non-standard".format(dmcycle))
