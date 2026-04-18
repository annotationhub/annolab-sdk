# Updating the SDK

Update the version
1. Increment verion in setup.py, and create a fresh commit with new version.
2. `git tag [VERSION]`
3. `git push origin main --tags`
4. `python setup.py sdist bdist_wheel`
5. `twine upload dist/*`