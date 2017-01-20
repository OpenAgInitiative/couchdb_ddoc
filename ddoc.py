#!/usr/bin/env python
import json
import argparse
import os
from couchdb import Database, ResourceNotFound

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

def path_split_top(path):
    i = path.find("/")
    return path[0:i], path[i + 1:]

def attach_all(db, doc_id, attachments):
    """Attach a dict of attachments to a document"""
    for filepath in attachments:
        with open(filepath, "r") as f:
            doc = db[doc_id]
            head, rest = path_split_top(filepath)
            db.put_attachment(doc, content=f, filename=rest)

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
        attachment_files = walk_files(fixture["_attachments"])
        attach_all(db, doc["_id"], attachment_files)
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