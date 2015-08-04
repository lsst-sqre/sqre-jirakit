#!/usr/bin/env python

import flask
import graphviz

import os
from contextlib import contextmanager
from functools import partial
from io import StringIO
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
    output = StringIO()
    issues = get_issues(server, query)
    generator(issues, output=output)
    return "<pre>%s</pre>" % (output.getvalue(),)

def build_server(server):
    @app.route('/wbs/<wbs>')
    def get_graph(wbs):
        return flask.redirect(flask.url_for("get_formatted_graph", wbs=wbs, fmt=DEFAULT_FMT))

    @app.route('/wbs/<fmt>/<wbs>')
    def get_formatted_graph(fmt, wbs):
        if fmt not in FMTS:
            flask.abort(404)
        dot = StringIO()
        issues = get_issues(server, build_query(("Milestone", "Meta-epic"), wbs))
        jira2dot(issues, file=dot, attr_func=attr_func, rank_func=rank_func, ranks=cycles())
        graph = graphviz.Source(dot.getvalue(), format=fmt)
        with tempdir() as dirname:
            image = graph.render("graph", cleanup=True, directory=dirname)
            return flask.send_file(os.path.join(dirname, "graph%s%s" % (os.path.extsep, fmt)))

    @app.route('/wbs/csv/<wbs>')
    def get_csv(wbs):
        return render_text(server, build_query(("Milestone",), wbs),
                           partial(jira2txt, csv=True, show_key=True, show_title=True,
                                   url_base=urljoin(server, "/browse")))

    @app.route('/wbs/tab/<wbs>')
    def get_tab(wbs):
        return render_text(server, build_query(("Milestone",), wbs), partial(jira2txt, csv=False))

    @app.route('/wbs/sanity/<wbs>')
    def get_sanity(wbs):
        def sanity_wrapper(issues, output):
            result = check_sanity(issues, output)
            if not result:
                output.write(u"No errors found.")

        return render_text(server, build_query(("Milestone",), wbs), sanity_wrapper)

    return app
