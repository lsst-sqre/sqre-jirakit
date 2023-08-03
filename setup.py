from setuptools import find_packages, setup

setup(
    name="jirakit",
    version="0.5",
    description="JIRA manipulation kit for LSST DM",
    license="GPL",
    author="LSST DM team",
    author_email="dm-devel@lists.lsst.org",
    url="https://github.com/lsst-sqre/sqre-jirakit",
    packages=['lsst', 'lsst.sqre'],
    scripts=['bin/dlp', 'bin/dlp-kpm'],
    install_requires=['jira', 'tabulate', 'flask', 'graphviz'],
    test_suite="tests",
)
