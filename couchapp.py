#!/usr/bin/env python
import json
import argparse
import os
from couchdb import Database
from itertools import imap

parser = argparse.ArgumentParser(
    description="""
A tiny util for pushing files into CouchDB to create CouchApps.

Adheres to the same naming conventions as couchapp by default, but
unlike couchapp, they can be overridden. We also don't do any codegen.

https://github.com/couchapp/couchapp/wiki/Complete-Filesystem-to-Design-Doc-Mapping-Example
"""
)

parser.add_argument(
    "-d", "--db",
    help="CouchDB url",
    type=str,
    default="http://localhost:5984"
)

parser.add_argument(
    "-f", "--fixture",
    help=""".json fixture file that describes the design document. Fields
present in this document will override fields read from files.""",
    type=argparse.FileType('r'),
    default="couchapp.json"
)

parser.add_argument(
    "-a", "--attachments_dir",
    help="Directory full of static files to attach to design document",
    type=str,
    default="_attachments"
)

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

def put(db, doc, attachments=None):
    """Put a doc with attachments into the database"""
    attachments = attachments or []
    _id = doc["_id"]
    db.save(doc)
    # Get doc after it has an ID
    attach_all(db, _id, attachments)

def replace(db, doc, attachments=None):
    """Replace an old document by deleting it first"""
    _id = doc["_id"]
    old_doc = db.get(_id, None)
    if old_doc:
        db.delete(old_doc)
    put(db, doc, attachments)

def cli_main():
    """Command line integration"""
    args = parser.parse_args()
    db = Database(url=args.db)
    fixture = json.load(args.fixture)
    attachments = walk_files(args.attachments_dir)
    replace(db, fixture, attachments)

if __name__ == "__main__":
    cli_main()