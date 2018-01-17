During development
==================

1. Develop and test changes using::

    python setup.py develop


After making changes
====================

1. Change the version number in ``setup.py``
2. Check the distribution::

    python setup.py check

3. Create a tag for the version number::

    git tag vX.Y.Z

4. Push the latest code to GitHub, including the new tag::

    git push --follow-tags


Uploading to PyPI
=================

1. Build the distribution::

    python setup.py sdist bdist_wheel

2. Upload (also see the `Python Packaging User Guide <https://packaging.python.org/tutorials/distributing-packages/#uploading-your-project-to-pypi>`__::

    twine upload dist/*

