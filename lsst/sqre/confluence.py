"""
Module for Confluence text processing.
"""
try:
    # Python 3
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


def bold(text):
    """Make Confluence bold text."""
    return f"*{text}*"


def heading(title, level=1):
    """Make a Confluence heading level."""
    return f"h{level}. {title}"


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
