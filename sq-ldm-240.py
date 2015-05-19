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

table = [cycles]

for milestone in milestones:
    issue = jira.issue(milestone, fields = 'key, summary, fixVersions, customfield_10500')
    #    if debug: print milestone

    # Get the release associated with this milestone
    if issue.fields.fixVersions:
        release = issue.fields.fixVersions[0]
        cyc = release.name
        milestonestr = milestone.key

        row = []
        for k in cycles:
            if k == cyc:
                row.append(milestonestr)
            else:
                row.append("-")
        table.append(row)
    else:
        print 'No release assigned to', issue.key


print tabulate.tabulate(table)





