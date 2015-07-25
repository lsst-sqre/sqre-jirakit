from __future__ import print_function

import sys
from csv import DictWriter
from collections import OrderedDict

from tabulate import tabulate
from jira import JIRA

from lsst.sqre.jirakit import cycles


def jira2txt(server, query, output=sys.stdout, csv=False, show_key=True, show_title=False, show_url=True):
    def makeRow(wbs, cycles, blank=None):
        row = OrderedDict()
        row['WBS'] = wbs
        for cycle in cycles():
            row[cycle] = blank
        return row

    jira = JIRA(dict(server=server))

    table = []
    for issue in jira.search_issues(query, maxResults=1000):
        if not issue.fields.fixVersions:
            print('No release assigned to', issue.key, file=sys.stderr)
            continue
        cyc = issue.fields.fixVersions[0].name

        if issue.fields.customfield_10500:
            WBS = issue.fields.customfield_10500
        else:
            WBS = 'None'

        row = makeRow(WBS, cycles, "" if csv else "-")

        if show_title and show_key:
            row[cyc] = issue.key + ': ' + issue.fields.summary
        elif show_title:
            row[cyc] = issue.fields.summary
        else:
            row[cyc] = issue.key

        # In CSV mode we can include a URL to the actual issue
        if csv and show_url:
            row[cyc] = '=HYPERLINK("{}","{}")'.format(server + "/browse/" + issue.key, row[cyc])

        table.append(row)

    if csv:
        writer = DictWriter(output, fieldnames=table[0].keys())
        writer.writeheader()
        writer.writerows(table)
    else:
        print(tabulate(table, headers='keys', tablefmt='pipe'), file=output)
