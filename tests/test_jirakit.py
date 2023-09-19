#!/usr/bin/env python


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
