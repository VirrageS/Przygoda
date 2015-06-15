import os
import sys
from setuptools import setup
from config import base_dir

install_requires = ["requests"]
tests_require = ["unittest2"]

version = "0.0.1"

if sys.argv[-1] == 'publish':
	os.system("git tag -a %s -m 'v%s'" % (version, version))
	os.system("python setup.py sdist bdist_wheel upload -r pypi")
	print("Published version %s, do `git push --tags` to push new tag to remote" % version)
	sys.exit()

setup(
	name = "przygoda",
	version = version,
	description = "Aplikacja Przygoda jest najlepszym sposobem na znajdowanie miłośników rowerów",
	long_description="\n\n".join([
		open(os.path.join(base_dir, "README.md"), "r").read()
	]),
	url = "http://github.com/VirrageS/przygoda",
	author = "Janusz Marcinkiewicz",
	author_email = "marcinkiewicz.janusz01@gmail.com",
	packages = ["app"],
	zip_safe = False,
	install_requires = install_requires,
	tests_require = tests_require,
	test_suite = "tests.get_tests",
)
