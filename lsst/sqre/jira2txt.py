from __future__ import print_function

import io
import sys
from csv import DictWriter
from collections import OrderedDict
from contextlib import contextmanager

try:
    # Python 3
    from urllib.parse import urljoin
except ImportError:
    # Python 2
    from urlparse import urljoin

from tabulate import tabulate
from jira import JIRA

from lsst.sqre.jirakit import cycles

def jira2txt(issues, csv=False, show_key=True, show_title=False, url_base=''):
    def makeRow(wbs, cycles, blank=None):
        row = OrderedDict()
        row['WBS'] = wbs
        for cycle in cycles():
            row[cycle] = blank
        return row

    table = []
    for issue in issues:
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
        elif show_key:
            row[cyc] = issue.key

        # In CSV mode we can include a URL to the actual issue
        if csv and url_base:
            row[cyc] = '=HYPERLINK("{}","{}")'.format(urljoin(url_base, issue.key), row[cyc])

        table.append(row)

    if csv:
        # In Python 2, DictWriter wants to write to a buffer of bytes. In
        # Python 3, it wants to write to a buffer of unicode.
        if sys.version_info[0] == 2:
            buf = io.BytesIO()
        else:
            buf = io.StringIO()
        writer = DictWriter(buf, fieldnames=table[0].keys())
        writer.writeheader()
        writer.writerows(table)
        return buf.getvalue()
    else:
        return tabulate(table, headers='keys', tablefmt='pipe')
