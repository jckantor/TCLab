During development
==================

1. Develop using::

    python setup.py develop
    
2. Test changes using::

    pytest -v
    pytest --cov=tclab tests/


After making changes
--------------------
	
1. Change the version number in ``tclab/version.py``.
2. Check the distribution::

    python setup.py check
    
3. Push changes through to the master branch on Github.
4. Create and push tag for the version number::

    git tag vX.Y.Z
    git push --tags


Uploading to PyPI
-----------------

1. Build the distribution::

    python setup.py sdist bdist_wheel

2. Upload (also see the `Python Packaging User Guide <https://packaging.python.org/tutorials/distributing-packages/#uploading-your-project-to-pypi>`__::

    twine upload dist/*

