#!/usr/bin/env python
import fire  # Automated CLI generator
import os
import re

version_filepath = os.path.join('.', 'VERSION')
version_pattern = re.compile(fr'^v\d+.\d+.\d+(-.+)?$')


def get():
    with open(version_filepath, 'r') as version_file:
        # Skip comments and empty lines in version file
        version_lines = []
        for line in version_file.readlines():
            li = line.strip()
            if not li.startswith("#") and not len(li) == 0:
                version_lines.append(li)
        assert len(version_lines) == 1, 'Version file is malformed'
        version = version_lines[0]
        assert version_pattern.match(version), 'Version string is malformed'
        return version.split("-")[0]


# This will completely overwrite the VERSION file, removing all comments if here is any
def write_version_file(major: int, minor: int, patch: int):
    version = f'{major}.{minor}.{patch}'
    # Read in the original file
    file_lines = []
    with open(version_filepath, 'r') as version_file:
        for line in version_file.readlines():
            file_lines.append(line)
    # Replace the non empty, non comment line -> must be version line, or get function would have failed
    for index, line in enumerate(file_lines):
        li = line.strip()
        if not li.startswith("#") and not len(li) == 0:
            file_lines[index] = 'v' + version + '\n'
    # Write back version file
    with open(version_filepath, 'w') as version_file:
        for line in file_lines:
            version_file.write(line)


def inc_patch():
    version = get()
    major, minor, patch = version.split('.')
    write_version_file(major[1:], minor, int(patch) + 1)


def inc_minor():
    version = get()
    major, minor, patch = version.split('.')
    write_version_file(major[1:], int(minor) + 1, 0)


def inc_major():
    version = get()
    major, minor, patch = version.split('.')
    write_version_file(int(major[1:]) + 1, 0, 0)


if __name__ == "__main__":
    fire.Fire({
        'get': get,
        'inc-patch': inc_patch,
        'inc-minor': inc_minor,
        'inc-major': inc_major
    })

# Usage: version.py <command>
#   available commands: get | inc-patch | inc-minor| inc-major
