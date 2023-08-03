#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys

import src.lsst.sqre.jirakit as jirakit
from src.lsst.sqre.jira2dot import attr_func, jira2dot, rank_func
from src.lsst.sqre.jira2txt import jira2txt
from src.lsst.sqre.jiraserver import build_server

DEFAULT_WBS = "02*"

# JIRA issue descriptions or other text may include unicode. Printing that
# "just works" in Python 3, and it's fine in Python 2 when sys.stdout.encoding
# == "UTF-8". However, when redirecting stdout to a file that's not the case,
# and Python 2 will raise. This is a rather ugly workaround -- better ideas?
if sys.version_info.major == 2:
    import __builtin__

    def print(value, *args, **kwargs):
        return __builtin__.print(value.encode("utf-8"), *args, **kwargs)


def generate_txt(opts):
    issues = jirakit.get_issues(
        opts.server, jirakit.build_query(("Milestone",), opts.wbs)
    )
    if not hasattr(opts, "no_url"):
        opts.no_url = True
    print(
        jira2txt(
            issues,
            csv=True if opts.mode == "csv" else False,
            show_key=not opts.no_key,
            show_title=opts.title,
            url_base=(None if opts.no_url else opts.server),
        )
    )


def generate_dot(opts):
    issues = jirakit.get_issues(
        opts.server, jirakit.build_query(("Milestone", "Meta-epic"), opts.wbs)
    )
    print(
        jira2dot(
            issues,
            attr_func=attr_func,
            diag_name="DLP Roadmap",
            rank_func=rank_func,
            ranks=jirakit.cycles(),
        )
    )


def check_sanity(opts):
    issues = jirakit.get_issues(
        opts.server, jirakit.build_query(("Milestone", "Meta-epic"), opts.wbs)
    )
    result = jirakit.check_sanity(issues)
    print(result)
    if result:
        sys.exit(1)


def run_server(opts):
    app = build_server(opts.server)
    app.config["DEBUG"] = opts.debug
    app.run(host=opts.host, port=opts.port)


parser = argparse.ArgumentParser(
    epilog="LSST jirakit: https://github.com/lsst-sqre/sqre-jirakit",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Front-end to JIRA-DLP database.  Choose a "
    "command from the list below; add '-h' for help.",
)

parser.add_argument("-s", "--server", default=jirakit.SERVER)
parser.add_argument(
    "-v", "--version", action="version", version="%(prog)s 0.5"
)

subparsers = parser.add_subparsers(dest="mode")
# http://stackoverflow.com/questions/23349349/argparse-with-required-subparser
subparsers.required = True

parser_csv = subparsers.add_parser(
    "csv",
    help="Generate CSV output",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser_csv.add_argument(
    "-t",
    "--title",
    action="store_true",
    help="Show the JIRA issue title in the table cell (can combine with -k)",
)
parser_csv.add_argument(
    "--no-key",
    action="store_true",
    help="Do not show the JIRA issue key in the table cell",
)
parser_csv.add_argument(
    "--no-url",
    action="store_true",
    default=False,
    help="Do not include hyperlinks in CSV output",
)
parser_csv.add_argument(
    "-w", "--wbs", default=DEFAULT_WBS, help="Limit results by WBS"
)
parser_csv.set_defaults(func=generate_txt)

parser_tab = subparsers.add_parser(
    "tab",
    help="Generate tabular output",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser_tab.add_argument(
    "-t",
    "--title",
    action="store_true",
    default=False,
    help="Show the JIRA issue title in the table cell (can combine with -k)",
)
parser_tab.add_argument(
    "--no-key",
    action="store_true",
    help="Do not show the JIRA issue key in the table cell",
)
parser_tab.add_argument(
    "-w", "--wbs", default=DEFAULT_WBS, help="Limit results by WBS"
)
parser_tab.set_defaults(func=generate_txt)

parser_dot = subparsers.add_parser(
    "dot",
    help="Generate GraphViz output",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser_dot.add_argument(
    "-w", "--wbs", default=DEFAULT_WBS, help="Limit results by WBS"
)
parser_dot.set_defaults(func=generate_dot)

parser_serve = subparsers.add_parser(
    "serve",
    help="Serve DLP project summaries by HTTP",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser_serve.add_argument(
    "--host", default="0.0.0.0", help="Hostname on which to listen"
)
parser_serve.add_argument(
    "--port", default=8080, type=int, help="Port on which to listen"
)
parser_serve.add_argument(
    "--debug", action="store_true", help="Enable debugging mode in server"
)
parser_serve.set_defaults(func=run_server)

parser_sanity = subparsers.add_parser(
    "sanity",
    help="Check DLP project for consistency",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser_sanity.add_argument(
    "-w", "--wbs", default=DEFAULT_WBS, help="Limit results by WBS"
)
parser_sanity.set_defaults(func=check_sanity)

if __name__ == "__main__":
    opts = parser.parse_args()
    opts.func(opts)
