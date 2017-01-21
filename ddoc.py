#!/usr/bin/env python
import json
import argparse
import os
from couchdb import Database, ResourceNotFound
from fnmatch import fnmatch
import re

parser = argparse.ArgumentParser(
    description="""
A tiny util for pushing files into CouchDB to create CouchApps.

Adheres to the same naming conventions as couchapp by default, but
unlike couchapp, they can be overridden. We also don't do any codegen.

https://github.com/couchapp/couchapp/wiki/Complete-Filesystem-to-Design-Doc-Mapping-Example
"""
)

parser.add_argument(
    "database",
    help="CouchDB url",
    type=str
)

parser.add_argument(
    "fixture",
    help=""".json fixture file that describes the design document.""",
    type=argparse.FileType('r'),
    default="couchapp.json"
)

SPECIAL_KEYS = frozenset((
    "_attachments",
    "views",
    "shows",
    "lists",
    "filters",
    "validate_doc_update"
))

def omit(d, keys):
    """
    Create a new dictionary object that is a shallow copy of `d` but without
    the listed `keys`.

    Returns a new dictionary.
    """
    out = {}
    for key, value in d.items():
        if key not in keys:
            out[key] = value
    return out

def walk_files(path):
    """Yield all file paths in a directory, recursively"""
    for dirpath, dirs, files in os.walk(path):
        for filepath in files:
            yield os.path.join(dirpath, filepath)

def fnmatch_any(filename, patterns):
    """
    Match a filename to a list of unix glob patterns. If any of the patterns
    match, return True
    """
    basename = os.path.basename(filename)
    for pattern in patterns:
        if fnmatch(basename, pattern):
            return True
    return False

def find_files(path, match=None, ignore=None):
    """
    Find files recursively, filtering the result with optional match
    and ignore arrays. Matches and ignores are unix-style glob patterns
    and applied at every level as we recursively walk for files.
    Returns a generator.
    """
    filepaths = walk_files(path)
    if match:
        filepaths = (fp for fp in filepaths if fnmatch_any(fp, match))
    if ignore:
        filepaths = (fp for fp in filepaths if not fnmatch_any(fp, ignore))
    return filepaths

def re_root_path(root, path):
    """Remove root of path (if any) from path"""
    return re.sub("^{}/?".format(root), "", path)

def attach_all(db, doc_id, attachments, root=""):
    """
    Attach a dict of attachments to a document.

    Optional:
    root - a path string for the head of the path. This head will
    be removed from the attachment's file path.
    """
    for filepath in attachments:
        with open(filepath, "r") as f:
            doc = db[doc_id]
            attachment_filepath = re_root_path(root, filepath)
            db.put_attachment(doc, content=f, filename=attachment_filepath)

def read_entire_file(filepath):
    """
    A mappable file reader.
    Returns a string."""
    with open(filepath, "r") as f:
        return f.read()

def read_file_fixture(fixture):
    """Read all files in fixture to string"""
    return {
        key: read_entire_file(filepath)
        for key, filepath in fixture["views"].keys()
    }

def put_fixture(db, fixture):
    try:
        views = read_file_fixture(fixture["views"])
    except KeyError:
        views = {}
    try:
        shows = read_file_fixture(fixture["views"])
    except KeyError:
        shows = {}
    try:
        lists = read_file_fixture(fixture["views"])
    except KeyError:
        lists = {}
    try:
        filters = read_file_fixture(fixture["views"])
    except KeyError:
        filters = {}
    try:
        validate_doc_update = read_entire_file(fixture["validate_doc_update"])
    except KeyError:
        validate_doc_update = ""
    doc = omit(fixture, SPECIAL_KEYS)
    if views:
        doc["views"] = views
    if shows:
        doc["shows"] = shows
    if lists:
        doc["lists"] = lists
    if filters:
        doc["filters"] = filters
    if validate_doc_update:
        doc["validate_doc_update"] = validate_doc_update
    db.save(doc)
    try:
        root = fixture["_attachments"]["path"]
        attachment_files = find_files(**fixture["_attachments"])
        attach_all(db, doc["_id"], attachment_files, root=root)
    except KeyError:
        pass

def cli_load_fixture():
    """Command line integration"""
    args = parser.parse_args()
    db = Database(url=args.database)
    fixture = json.load(args.fixture)
    # First delete any old design document. This avoids having to merge
    # attachments or store attachment revision history.
    try:
        del db[fixture["_id"]]
    except ResourceNotFound:
        pass
    put_fixture(db, fixture)

if __name__ == "__main__":
    cli_load_fixture()