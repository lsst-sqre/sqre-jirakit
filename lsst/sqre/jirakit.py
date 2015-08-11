
"""
Module for helper apps relating to the LSST-DM reporting cycle and LSST-SIMS work planning.
"""

SERVER = "https://jira.lsstcorp.org/"

def cycles(seasons=['W', 'S'], years=range(14, 22)):
    # S14 is a cycle but W14 is not
    return ("%s%d" % (s, y) for y in years for s in seasons if not (s == 'W' and y == 14))

def build_query(issue_types, wbs):
    return 'project = DLP AND issuetype in (%s) AND wbs ~ "%s" ORDER BY wbs ASC, fixVersion DESC' % \
        (", ".join(issue_types), wbs)

def basic_auth_from_file(auth_file_path=None):
    """Get basic auth from a two line file.
    """
    if auth_file_path is None:
        import os
        auth_file_path = os.path.join(os.path.expanduser("~/"), ".jira_auth")

    with open(auth_file_path, 'r') as fd:
        uname = fd.readline().strip()  # Can't hurt to be paranoid
        pwd = fd.readline().strip()

    return (uname, pwd)

def get_issue_links(issue, linkTypeName=None):
    """Get links from an issue.
    """
    links = issue.fields.issuelinks
    if linkTypeName is None:
        return links
    else:
        return [link for link in links if link.type.name in linkTypeName]
