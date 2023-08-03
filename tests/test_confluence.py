#!/usr/bin/env python

from __future__ import absolute_import, division, print_function

import unittest

import lsst.sqre.confluence as confluence


class ConfluenceTest(unittest.TestCase):
    def testBold(self):
        istr = "test"
        self.assertEqual(confluence.bold(istr), "*test*")

    def testHeading(self):
        self.assertEqual(confluence.heading("title"), "h1. title")
        self.assertEqual(confluence.heading("title", 4), "h4. title")

    def testTable(self):
        import os

        table = []
        table.append("|| A || B ||")
        table.append("| a | d |")
        table.append("| b | e |")
        table.append("| c |   |")

        headings = ["A", "B"]
        col1 = ["a", "b", "c"]
        col2 = ["d", "e"]
        self.assertEqual(confluence.table(headings, col1, col2), os.linesep.join(table))

        table2 = []
        table2.append("|| A || B ||")
        table2.append("| a\nb\nc | d\ne |")
        self.assertEqual(
            confluence.table(headings, col1, col2, onerow=True), os.linesep.join(table2)
        )


if __name__ == "__main__":
    unittest.main()
