# sqre-jirakit

JIRA manipulation tools using the python jira module

## Installation instructions

Assuming you have a python environment and git installed:

    pip install git+https://github.com/lsst-sqre/sqre-jirakit.git

This code should work under both Python 2.7+ and Python 3.3+.

## Scripts

### `dlp`

General purpose interface to viewing information in the DLP project. Supports
fve different output modes: generating summaries of the project in CSV, ASCII
tables or GraphViz `dot` format, serving those summaries over the web, and
checking the project for correctness ("sanity").

Invoke `dlp` with the `-h` command line option for help:

    $ dlp -h
    usage: dlp [-h] [-s SERVER] [-v] {csv,tab,dot,serve,sanity} ...

    positional arguments:
      {csv,tab,dot,serve,sanity}
        csv                 Generate CSV output
        tab                 Generate tabular output
        dot                 Generate GraphViz output
        serve               Serve DLP project summaries by HTTP
        sanity              Check DLP project for consistency

    optional arguments:
      -h, --help            show this help message and exit
      -s SERVER, --server SERVER
      -v, --version         show program's version number and exit

    LSST jirakit: https://github.com/lsst-sqre/sqre-jirakit

Provide a positional argument followed by `-h` for help on that particular
mode (e.g. `dlp csv -h`).

#### `csv`

Generates an "LDM-240" style table as CSV output (for importing into Excel
etc).

By default, table cells contains the JIRA keys of milestones scheduled for a
particular WBS and cycle. Add the `--title` option to also include the JIRA
issue titles; use `--no-key` to disable the display of the key.

An Excel-specific syntax is used to embed hyperlinks. If you're not using
Excel, it may be distracting; disable it with `--no-url`.

The range of WBS elements included may be limited by using the `--wbs` option
(e.g. `--wbs=02C*`, `--wbs=02C.04.03`).

#### `tab`

Generate an "LDM-240" style table as ASCII. Options as `csv`, but excluding
`--no-url`.

#### `dot`

Generate a [Graphviz](http://www.graphviz.org) `dot` format output describing
a graph of the DLP project. Use `--wbs` to limit the range of WBS elements
included. For example:

    $ dlp dot | dot -T svg > graph.svg

#### `serve`

Run a web server which exposes summaries of the DLP project to the outside
world. Access at `http://<host>:<port>/wbs/<format>/<wbs>`, where `<host>` is
the address of the machine running `dlp serve` (customize interfaces on which
to listen with the `--host` option), `port` defaults to `8080` (change with
`--port`), `<wbs>` selects a particular set of WBS elements (analagous to the
`--wbs` option, above) and `<format>` may be one of `tab`, `csv`, `sanity`,
`pdf`, `svg`, and a number of other image formats.

Use the `--debug` option to start the server in debug mode, which will provide
more information (in terms of stack traces etc) if things go wrong, but should
likely not be exposed to the public internet.

#### `sanity`

Checks the DLP JIRA project for consistency. At present, this means it
identifies:

* Milestones which are not scheduled for a particular release ("fixVersion");
* Milestones which are scheduled for more than one release;
* "Bad" blocking relationships.

Bad blocks are those in which a blocked Milestone is scheduled to take place
in an earlier cycle than the Milestone or Meta-epics which are blocking it.
This is smart enough to follow chains of blocks (ie, if A blocks B and B
blocks C, A is regarded as blocking C), but the current implementation does
not report intermediate issues (thus the above relationship is simply reported
as "A blocks C"); use e.g. dlp-graph (above) to identify these where
necessary.

Accepts the `--wbs` option to limit the WBS elements checked. Returns 0 if no
problems are detected; prints a list of bad blocks and exits with status 1
otherwise.

### `add_kpm_epics`

Utility to add epics to a particular project to specify when a particular
value of the metric should be reached.  Values, units, and development cycle
are specified as commandline arguments.  Values and cycles are read left to
right and grouped in that order.  In other words, the number of value and
cycle arguments must be the same and they must be in the same order.  The
units are assumed to be the same for all cycles.

This only works for plugging epics into the DM project since the schema
differs from project to project.

## Known Bugs etc

### Issues with jira python module

- https://github.com/pycontribs/jira/issues/66

Until this bug is fixed, this won't work on projects requiring authentication

- undeclared iPython dependency for jirashell
