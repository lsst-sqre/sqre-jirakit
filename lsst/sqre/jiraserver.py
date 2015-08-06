#!/usr/bin/env python

import flask
import graphviz

import os
from contextlib import contextmanager
from functools import partial
from shutil import rmtree
from tempfile import mkdtemp

try:
    # Python 3
    from urllib.parse import urljoin
except ImportError:
    # Python 2
    from urlparse import urljoin

from lsst.sqre.jira2dot import jira2dot, attr_func, rank_func
from lsst.sqre.jira2txt import jira2txt
from lsst.sqre.jirakit import build_query, cycles, get_issues, check_sanity

app = flask.Flask(__name__)

DEFAULT_FMT="pdf"

# Supported formats. A request for anything else throws a 404.
FMTS = {"dot", "eps", "fig", "pdf", "svg", "png", "ps", "svg"}

@contextmanager
def tempdir():
    dirname = mkdtemp()
    try:
        yield dirname
    finally:
        rmtree(dirname, ignore_errors=True)

def render_text(server, query, generator):
    return "<pre>%s</pre>" % (generator(get_issues(server, query)))

def build_server(server):
    @app.route('/wbs/<wbs>', defaults={'fmt': DEFAULT_FMT})
    @app.route('/wbs/<fmt>/<wbs>')
    def get_formatted_graph(fmt, wbs):
        if fmt not in FMTS:
            flask.abort(404)
        issues = get_issues(server, build_query(("Milestone", "Meta-epic"), wbs))
        graph = graphviz.Source(jira2dot(issues, attr_func=attr_func, rank_func=rank_func,
                                         ranks=cycles()), format=fmt)
        with tempdir() as dirname:
            image = graph.render("graph", cleanup=True, directory=dirname)
            return flask.send_file(os.path.join(dirname, "graph%s%s" % (os.path.extsep, fmt)))

    @app.route('/wbs/csv/<wbs>')
    def get_csv(wbs):
        return render_text(server, build_query(("Milestone",), wbs),
                           partial(jira2txt, csv=True, show_key=True, show_title=True,
                                   url_base=(urljoin(server, "/browse") if
                                             flask.request.args.get('link') else "")))

    @app.route('/wbs/tab/<wbs>')
    def get_tab(wbs):
        return render_text(server, build_query(("Milestone",), wbs), partial(jira2txt, csv=False))

    @app.route('/wbs/sanity/<wbs>')
    def get_sanity(wbs):
        def sanity_wrapper(issues):
            result = check_sanity(issues)
            if not result:
                return "No errors found."

        return render_text(server, build_query(("Milestone",), wbs), sanity_wrapper)

    return app
