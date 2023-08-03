from __future__ import print_function

import io
import sys
from collections import OrderedDict
from csv import DictWriter

try:
    # Python 3
    from urllib.parse import urljoin
except ImportError:
    # Python 2
    from urlparse import urljoin

from tabulate import tabulate

from lsst.sqre.jirakit import cycles, dm_to_dlp_cycle, get_issues_by_key


def jira2txt(issues, csv=False, show_key=True, show_title=False, url_base=None):
    def makeRow(wbs, cycles, blank=None):
        row = OrderedDict()
        row["WBS"] = wbs
        for cycle in cycles():
            row[cycle] = blank
        return row

    table = []
    for issue in issues:
        if not issue.fields.fixVersions:
            print("No release assigned to", issue.key, file=sys.stderr)
            continue
        cyc = issue.fields.fixVersions[0].name

        if (
            hasattr(issue.fields, "customfield_10500")
            and issue.fields.customfield_10500
        ):
            WBS = issue.fields.customfield_10500
        else:
            WBS = "None"

        row = makeRow(WBS, cycles, "" if csv else "-")

        if show_title and show_key:
            row[cyc] = issue.key + ": " + issue.fields.summary
        elif show_title:
            row[cyc] = issue.fields.summary
        elif show_key:
            row[cyc] = issue.key

        # In CSV mode we can include a URL to the actual issue
        if csv and url_base:
            row[cyc] = _make_csv_hyperlink_from_issue(url_base, issue, row[cyc])

        table.append(row)

    return _table2text(table, csv)


def jirakpm2txt(issues, server, csv=False, url_base=None):
    # JIRA fields lookup for DM/DLP project:
    #  customfield_10900: cycle
    #  customfield_11000: metric
    #  customfield_11001: units
    def make_row(kpm, blank=None):
        row = OrderedDict()
        row["KPM"] = kpm.key
        row["Title"] = kpm.fields.summary
        row["Target"] = "{} {}".format(
            kpm.fields.customfield_11000, kpm.fields.customfield_11001
        )
        for cycle in cycles():
            row[cycle] = blank
        return row

    # For each KPM we need to request the` "Relates to" issues.
    table = []
    for i in issues:
        relates = []
        metric_unit = str(i.fields.customfield_11001)

        duplicates = False
        for link in i.fields.issuelinks:
            if link.type.name == "Relates":
                if hasattr(link, "outwardIssue"):
                    relates.append(link.outwardIssue.key)
                elif hasattr(link, "inwardIssue"):
                    relates.append(link.inwardIssue.key)
            elif link.type.name == "Duplicate":
                # If this has a Duplicates link we should not be reporting the KPM
                duplicates = True
                break

        if duplicates:
            continue

        row = make_row(i)

        # Insert URL to DLP ticket if required
        if csv and url_base:
            row["KPM"] = _make_csv_hyperlink_from_issue(url_base, i, row["KPM"])

        if len(relates):
            related_issues = get_issues_by_key(server, relates)
            for dm in related_issues:
                if not hasattr(dm.fields, "customfield_10900"):
                    print("Cycle missing from {} via {}".format(dm, i), file=sys.stderr)
                    break
                cyc = dm.fields.customfield_10900
                if cyc is None:
                    print("Cycle missing from {} via {}".format(dm, i), file=sys.stderr)
                    break
                cyc = dm_to_dlp_cycle(cyc)
                row[cyc] = dm.fields.customfield_11000
                if str(dm.fields.customfield_11001) != metric_unit:
                    print(
                        "{}: Unit mismatch between DLP KPM and {} ({} != {})".format(
                            i, dm, metric_unit, dm.fields.customfield_11001
                        ),
                        file=sys.stderr,
                    )
                # In CSV mode we can include a URL to the actual issue
                if csv and url_base:
                    row[cyc] = _make_csv_hyperlink_from_issue(url_base, dm, row[cyc])

        table.append(row)

    return _table2text(table, csv)


def _make_csv_hyperlink_from_issue(url_base, issue, text):
    # Create a CSV-Excel hyperlink
    # Base URL is the JIRA server
    fragment = "browse/" + issue.key
    return '=HYPERLINK("{}","{}")'.format(urljoin(url_base, fragment), text)


def _table2text(table, csv=False):
    # Converts a dict of rows to either plain text table or CSV
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
        return tabulate(table, headers="keys", tablefmt="pipe")
