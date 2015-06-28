
"""
Module for helper apps relating to the LSST-DM reporting cycle
"""

def cycles():
    cyclelist = []
    seasons = ['W','S']
    # years 15-20
    years = range(15,21)
    index = 0
    for yy in years:
        for s in seasons:
            cyclelist.append(s + str(yy))
            index += 1

    return cyclelist
