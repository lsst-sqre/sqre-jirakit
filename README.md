# sqre-jirakit
JIRA manipulation tools using the python jira module

Installation instructions
=========================

Assuming you have a python environment and git installed:

    pip install git+https://github.com/lsst-sqre/sqre-jirakit.git

This code should work under both Python 2.7+ and Python 3.3+

Scripts
=======

sq-ldm-240
----------

Generates an 'LDM-240' type table. Type -h for options. 

Known Bugs etc
==============

Issues with jira python module
------------------------------

- https://github.com/pycontribs/jira/issues/66

Until this bug is fixed, this won't work on projects requiring authentication

- undeclared iPython dependency for jirashell
