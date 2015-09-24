#!/usr/bin/env python

from __future__ import print_function, absolute_import, division

import unittest

import lsst.sqre.jirakit as jirakit

class JiraKitTest(unittest.TestCase):

    def testBasic(self):
        self.assertTrue(True)

    def testCycle(self):

        c = jirakit.cycles()
        self.assertEqual(c[0], 'S14')

    def testIssueUrl(self):
        try:
            # Python 3
            from urllib.parse import urljoin
        except ImportError:
            # Python 2
            from urlparse import urljoin
        key = "SIM-1289"
        comp_url = urljoin(jirakit.SERVER, "browse/" + key)
        self.assertEqual(jirakit.url_for_issue(key), comp_url)

if __name__ == '__main__':
    unittest.main()
