import os
import runpy

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

# Extract the version from mudtrix
VERSION = runpy.run_path(os.path.join(here, "mudtrix/version.py"))["VERSION"]


def requirements(filename):
    if os.path.exists(filename):
        return [l for l in open(filename).read().splitlines()
                    if not l.startswith("#")]
    else:
        return ""


setup(name='mudtrix',
      version=VERSION,
      description='MUDtrix, a matrix<->MUD bridge',
      long_description=(README + '\n\n' + "*" * 30 + " CHANGES " + "*" * 30 +
                        "\n\n" + CHANGES),
      classifiers=[
          "Intended Audience :: End Users/Desktop",
          "Operating System :: POSIX",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.8",
          "Development Status :: 3 - Alpha",
          ],
      author='Chris Newton',
      author_email='redshodan@gmail.com',
      url='https://github.com/redshodan/mudtrix',
      keywords=["mudtrix", "matrix", "MUD"],
      packages=find_packages(),
      python_requires='>=3.8',
      include_package_data=True,
      zip_safe=False,
      platforms=["Any"],
      test_suite='mudtrix',
      install_requires=requirements("requirements.txt"),
      setup_requires=['pytest-runner'],
      tests_require=requirements("requirements-test.txt"),
      license="GPLv2"
      )
