import sys
import logging
import textwrap
from io import StringIO

def attr_func(issue):
    if issue.fields.issuetype.name == "Milestone":
        if issue.fields.resolution and issue.fields.resolution.name == "Done":
            return 'style="rounded,filled";fillcolor="palegreen"',
        else:
            return 'style="rounded,filled";fillcolor="powderblue"',
    if (issue.fields.issuetype.name == "Meta-epic" and issue.fields.resolution and
        issue.fields.resolution.name == "Done"):
        return 'style="filled";fillcolor="seashell2"',
    else:
        return ()

def rank_func(issue):
    if issue.fields.issuetype.name == "Milestone" and len(issue.fields.fixVersions) > 0:
        return issue.fields.fixVersions[0]
    return None

def jira2dot(issues, link_types=("Blocks",), attr_func=None, rank_func=None,
             ranks=None, diag_name="Diagram"):
    """Generate a GraphViz dot file displaying the relationships between JIRA issues.

    Arguments:
      issues ---------------- Iterable of issues to process
      link_types ------------ Sequence of link types to include in the graph
      attr_func ------------- Callback function that takes a jira.Issue object and returns a sequence
                              of GraphViz attribute key/value pairs (e.g. "shape=box")
      rank_func ------------- Callback function that takes a jira.Issue object and returns a string
                              that the issue should be sorted by - typically a release version or cycle.
      rank ------------------ An ordered sequence of rank strings to sort issues by (only affects issues
                              for which rank_func returns a result other than None)
      diag_name ------------- Name for the top-level graph node.
    """
    output = StringIO()
    output.write(u'digraph "{0}" {{\n'.format(diag_name))
    output.write(u'  node [fontname="monospace", shape="box"]')
    by_key = {}
    by_rank = {}

    for issue in issues:
        by_key[issue.key] = issue

        # Populate a dict indexed by caller-defined rank.
        if rank_func is not None:
            rank = rank_func(issue)
            if rank:
                by_rank.setdefault(str(rank), []).append(issue)
                logging.debug("Set rank {0} for issue {1}".format(rank, issue.key))

        # Get any custom attributes from the caller.
        if attr_func is None:
            attr = [u"shape=box"]
        else:
            attr = list(attr_func(issue))

        # Get the owner (WBS or Team) for the issue
        issuetype = issue.fields.issuetype.name
        if issuetype == "Milestone" or issuetype == "Meta-epic" or issuetype == "Epic":
            owner = issue.fields.customfield_10500  # WBS
        else:
            owner = issue.fields.customfield_10502.value  # Team

        # Generate a fancy label containing the issue key, the owner (WBS or Team), and summary.
        summary = issue.fields.summary.replace("&", u"&amp;")
        label = u"""
        label=
            <<table border="0">
                <tr><td><b>{0}</b></td><td><b>{1}</b></td></tr>
                <tr><td colspan="2">{2}</td></tr>
            </table>>
        """.format(issue.key, owner, u"<br/>".join(textwrap.wrap(summary, width=25)))
        attr.append(label)

        # Use the issue description as the tooltip (mouseover text)
        if issue.fields.description:
            description = u"&#10;".join(issue.fields.description.replace('"', "'").split("\n"))
            tooltip = u'tooltip="{0}"'.format(description)
        else:
            tooltip = u'tooltip="{0}"'.format(summary)
        attr.append(tooltip)

        # Write the node's attributes.
        attr.append(u'URL="{0}"'.format(issue.permalink()))
        output.write(u'  "{0}" [{1}]\n'.format(issue.key, ", ".join(attr)))

    # Setup ranks (caller-defined, but probably indicate a release or cycle)
    if ranks:
        output.write(u'  node [fontname="monospace", shape=none]\n')
        output.write(u'  {0}\n'.format(u" -> ".join(u'"{0}"'.format(r) for r in ranks)))
        for rank in ranks:
            items = [rank] + [i.key for i in by_rank.get(str(rank), [])]
            output.write(u'  {{ rank=same; {0} }}\n'.format(u"; ".join(u'"{0}"'.format(item) for item in items)))

    # Declare issue links
    for issue in by_key.values():
        for link in issue.fields.issuelinks:
            if link.type.name in link_types:
                if hasattr(link, "outwardIssue"):
                    if link.outwardIssue.key in by_key:
                        output.write(u'  "{0.key}" -> "{1.key}"\n'.format(issue, link.outwardIssue))
                    else:
                        logging.debug(
                            "Skipping external link {0.key} -> {1.key}".format(issue, link.outwardIssue)
                        )
                else:
                    logging.debug("Skipping inward link {0.key} -> {1.key}".format(link.inwardIssue, issue))

    output.write(u"}\n")
    return output.getvalue()
