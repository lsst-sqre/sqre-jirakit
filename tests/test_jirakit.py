#!/usr/bin/env python

from __future__ import print_function, absolute_import, division

import unittest

import lsst.sqre.jirakit as jirakit

class JiraKitTest(unittest.TestCase):

    def testBasic(self):
        self.assertTrue(True)

    def testCycle(self):

        c = jirakit.cycles()
        self.assertEqual(c[0],'W15')

if __name__ == '__main__':
    unittest.main()

    
