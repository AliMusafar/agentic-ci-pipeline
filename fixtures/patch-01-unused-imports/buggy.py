import os
import json
import requests   # unused
import sys        # unused
import hashlib    # unused


def get_data(filename):
    with open(filename) as f:
        return json.load(f)


def build_path(base, name):
    return os.path.join(base, name)
