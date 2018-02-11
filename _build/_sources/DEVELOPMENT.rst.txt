During development
==================

1. Develop using::

    python setup.py develop
    
2. Test changes using::

    pytest -v


After making changes
====================

1. Update documentation::

    python3 -m sphinx .  _build
	
2. Change the version number in ``setup.py``
3. Check the distribution::

    python setup.py check
    
4. Push changes through to the master branch on Github.
5. Create and push tag for the version number::

    git tag vX.Y.Z
    git push --tags


Uploading to PyPI
=================

1. Build the distribution::

    python setup.py sdist bdist_wheel

2. Upload (also see the `Python Packaging User Guide <https://packaging.python.org/tutorials/distributing-packages/#uploading-your-project-to-pypi>`__::

    twine upload dist/*

