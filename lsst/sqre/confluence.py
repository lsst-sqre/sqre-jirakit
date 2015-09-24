"""
Module for Confluence text processing.
"""
try:
    # Python 3
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

def bold(text):
    """Make Confluence bold text.
    """
    return "*{0}*".format(text)

def heading(title, level=1):
    """Make a Confluence heading level.
    """
    return "h{0}. {1}".format(level, title)

def table(headings, *columns, **kwargs):
    """Make a Confluence table.

    This function creates a Confluence table.

    Args:
        headings: An iterable of strings representing the column headings for the table.
        columns: A set of iterables (usually strings) containing the corresponding columns
            for the table.
        **kwargs:
            onerow: A boolean flag to make each column information iterable into a single row.

    Returns:
        A string containing the table formatting and information.
    """
    import os
    table = []

    onerow = kwargs.get("onerow", False)

    header = ["||"]
    for heading in headings:
        header.append(heading)
        header.append("||")
    table.append(" ".join(header))

    if onerow:
        row = ["|"]
        for column in columns:
            row.append(os.linesep.join(column))
            row.append("|")
        table.append(" ".join(row))
    else:
        for colvals in zip_longest(*columns, fillvalue=" "):
            row = ["|"]
            for colval in colvals:
                row.append(colval)
                row.append("|")
            table.append(" ".join(row))

    return os.linesep.join(table)

def link(url, alt_txt=None):
    """Make a Confluence link.

    This function makes a Confluence link. If the alt_txt parameter is used, this text is displayed for the
    link.

    Args:
        url: A string containing the URL to make the link.
        alt_txt: An alternate text string for display rather than the URL.

    Returns:
        A string formatted for the link.
    """
    if alt_txt is None:
        return "[{}]".format(url)
    else:
        return "[{}|{}]".format(alt_txt, url)

def heading_plus_link(header_txt, link_alt_txt, link_url):
    """Make a heading with a link.

    This function creates a heading string in the format of:
        heading text ([link alternate text|link URL])

    Args:
        header_txt (str): The heading text.
        link_alt_txt (str): The alternate text for the link.
        link_url (str): The URL for the link.

    Returns:
        str: The formatted heading text.
    """
    return "{0} ({1})".format(header_txt, link(link_url, link_alt_txt))
