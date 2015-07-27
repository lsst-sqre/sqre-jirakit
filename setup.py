from setuptools import setup, find_packages

setup(
    name="jirakit",
    version="0.5",
    description="JIRA manipulation kit for LSST DM",
    license="GPL",
    author="LSST DM team",
    author_email="dm-devel@lists.lsst.org",
    url="https://github.com/lsst-sqre/sqre-jirakit",
    packages=['lsst', 'lsst.sqre'],
    scripts=['bin/sq-ldm-240', 'bin/dlp-graph', 'bin/dlp-web', 'bin/dlp-sanity'],
    install_requires=['jira', 'tabulate', 'flask', 'graphviz'],
    test_suite="tests",
)
