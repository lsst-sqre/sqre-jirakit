"""
Module for Confluence helper functions.
"""


def check_description(descr):
    """Check a JIRA description field."""
    if descr is None:
        return "No description provided."
    else:
        return descr


def create_list_from_numbered_description(desrc, bulletType="*"):
    """Create Confluence list from a JIRA numbered description."""
    import os

    olist = []
    for line in desrc.strip().split(os.linesep):
        values = line.split()
        listnum = values[0].split(".")
        lenlist = len(listnum)
        if listnum[-1] == "":
            lenlist -= 1
        numbered = bulletType * lenlist
        olist.append("{0} {1}".format(numbered, " ".join(values[1:])))
    return olist
