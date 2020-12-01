# setuptools with setup.cfg

This `setup.cfg` was actuall generated from `setup.py` (from sibling example) with command:
```bash
pip install setup-py-upgrade
setup-py-upgrade setup.cfg/ # called on entire directory, not just setup.cfg file
```

`setup.py` is still needed so the directory is "installable", but it only contains minimum code:
```python
from setuptools import setup
setup()
```
