After making changes
====================

1. Change the version number in ``config.py``
2. Push the latest code to GitHub
3. Check the distribution::

    python setup.py check


Uploading
=========
1. Build the distribution::

    python setup.py sdist bdist_wheel

2. Upload (also see the `Python Packaging User Guide <https://packaging.python.org/tutorials/distributing-packages/#uploading-your-project-to-pypi>`__::

    twine upload dist/*