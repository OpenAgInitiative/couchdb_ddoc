# couchdb_ddoc

Easily push design documents into CouchDB. Useful for deploying static webapps as [CouchApps](http://docs.couchdb.org/en/2.0.0/couchapp/index.html)!

couchdb_ddoc adds the `ddoc_load_fixture` command, which can load a CouchApp into the DB from a `.json` manifest file.

```bash
ddoc_load_fixture http://mycouch:5984/app couchapp.json
```

## .json manifest format

`.json` manifest files look just like [CouchDB Design Documents](http://docs.couchdb.org/en/2.0.0/couchapp/ddocs.html), with a small difference:

- views, shows, lists, and filters can point to `.js` files. The contents of the files will be loaded and appended as stringified functions.
- `_attachments` can point to a directory. The directory will be recursively searched and all files added as attachments.

For example, to load a project with this directory structure:

```
views/
  my_view.js
shows/
  my_show.js
lists/
  my_filter.js
filters/
  my_filter.js
attachments/
  ...
```

You could create the following manifest file:

```json
{
  "_id": "_design/app",
  "rewrites": [
    {"from": "/", "to": "index.html"},
    {"from": "/api", "to": "../../"},
    {"from": "/api/*", "to": "../../*"},
    {"from": "/*", "to": "*"}
  ],
  "views": {
    "my_view": "views/my_view.js"
  },
  "shows": {
    "my_show": "shows/my_show.js"
  },
  "lists": {
    "my_list": "lists/my_list.js"
  },
  "filters": {
    "my_filter": "filters/my_filter.js"
  },
  "_attachments": "_attachments/"
}
```

## Other Tools

There are some other tools that might also suite your needs:

- [couchapp on NPM](https://www.npmjs.com/package/couchapp) - a Node.js module
- [couchapp](https://github.com/couchapp/couchapp) - Python utility that will deploy your CouchApp using an opinionated directory structure.
- [erica](https://github.com/benoitc/erica/) an Erlang tool for pushing CouchApps.

The [couchapp wiki](https://github.com/couchapp/couchapp/wiki) is also useful.