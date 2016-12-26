import os
from setuptools import setup, find_packages

__version__ = "0.1.0"

print(os.environ)
twobradleys_app_name = os.environ["TWOBRADLEYS_APP"]
git_repo_url = "https://github.com/%s" % os.environ["GIT_REPO"]

setup(
    name=twobradleys_app_name,
    version=__version__,
    url=git_repo_url,
    packages=find_packages(),
    entry_points={'console_scripts': [
        '%s-serve = %s.main:main' % (twobradleys_app_name, twobradleys_app_name)
    ]},
)
