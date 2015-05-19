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

milestones = jira.search_issues('project = DLP and issuetype = Milestone order by WBS ASC')

table = [cycles]

for milestone in milestones:
    issue = jira.issue(milestone)
    #    if debug: print milestone
    print 40 * '*'
    # Get the release associated with this milestone
    if issue.fields.fixVersions:
        release = issue.fields.fixVersions[0]
        cyc = release.name
        milestonestr = milestone.key
        if issue.fields.customfield_10500:
            WBS =  issue.fields.customfield_10500
        else:
            WBS = None
            
        row = [WBS]

        for k in cycles:
            if k == cyc:
                row.append(milestonestr)
            else:
                row.append("-")
        table.append(row)
    else:
        print 'No release assigned to', issue.key


print tabulate.tabulate(table)





