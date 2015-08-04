from __future__ import print_function

"""
Module for helper apps relating to the LSST-DM reporting cycle
"""

import itertools
import os

def cycles(seasons=['W', 'S'], years=range(15,21)):
    return ["%s%d" % (s, y) for y in years for s in seasons]

def token(authfile='~/.sq_jira_token',
          debug=None):

    """
    returns a jira login token
    """

    mytoken = None
    file_credential = os.path.expanduser(authfile)

    if not os.path.isfile(file_credential):
        print("You don't have a token in {0} ".format(file_credential))
        print("Get one and try again")
        sys.exit(1)

    with open(file_credential, 'r') as fd:
        mytoken = fd.readline().strip()
        mysecret = fd.readline().strip()

        if debug: print("Token: ", mytoken)
        if debug: print ("Secret: ", mysecret)
            
    return(mytoken,mysecret)


    
