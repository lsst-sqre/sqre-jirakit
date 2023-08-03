#!/usr/bin/env python

from __future__ import absolute_import, division, print_function

import unittest

import lsst.sqre.jirakit as jirakit


class JiraKitTest(unittest.TestCase):
    def testBasic(self):
        self.assertTrue(True)

    def testCycle(self):
        c = jirakit.cycles()
        self.assertEqual(c[0], "S14")


if __name__ == "__main__":
    unittest.main()
