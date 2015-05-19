#!/usr/bin/env python

from jira import JIRA
import jirakit
import sys, os
import tabulate

debug = os.getenv("DM_SQUARE_DEBUG")
trace = False

options = {
    'server': 'https://jira.lsstcorp.org/'
}

# WBS = 'customfield_10500'

jira = JIRA(options)

project = jira.project('DLP')

cycles = jirakit.cycles()
if debug: print cycles

milestones = jira.search_issues('project = DLP and issuetype = Milestone order by fixVersion DESC')

table = []

for milestone in milestones:
    issue = jira.issue(milestone, fields = 'key, summary, fixVersions, customfield_10500')
    #    if debug: print milestone
    row = dict()
    for k in cycles:
        row[k] = None

    if issue.fields.fixVersions:
        release = issue.fields.fixVersions[0]
        print release.name, '<-->', milestone.key
        row[release.name] = milestone.key
        # cycles[fixVersion] = issue.key
    else:
        print 'No release assigned to', issue.key
    print row
    table.append(row)

print 40 * '-'





