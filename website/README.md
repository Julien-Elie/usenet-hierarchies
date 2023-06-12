# Web site of usenet-hierarchies

> Copyright (c) 2007-2009, 2011, 2016, 2023 Julien ÉLIE

See the top-level [README](../README.md) file for details about the license
and general support.


## Description

Here are the materials used to generate the web pages at
http://usenet.trigofacile.com/hierarchies/.  This web site provides a merged
view of information related to Usenet hierarchies.  It notably helps in
finding the current list of newsgroups, their moderation status, the latest
changes, and administrative information about hierarchies.

This repository permits sharing its source code, as well as a few generated
useful files that can be found in the [`data`](data) subdirectory, notably a
list of newsgroups with UTF-8 descriptions and the dates of the last changes
in that list.

`libusenet_hierarchies.py` contains routines called by
`sync_usenet_hierarchies.py` and `index.py` to process external data related
to Usenet hierarchies, and to generate these files with merged information.


## Requirements

- Python 2 is currently required as the [web
site](http://usenet.trigofacile.com/hierarchies/) running this package uses
a version of the `mod_wsgi` Apache module that has been built against Python
2.7.

- A web server with a WSGI framework (like `mod_wsgi` for Apache) needs being
installed.

- The Python module `unidecode` is also required to generate descriptions in
mere ASCII.  Its installation is as simple as running `pip install unidecode`.


## Installing

In case you really need your own installation and cannot just use the data
from the [web site](http://usenet.trigofacile.com/hierarchies/), you'll have
to at least do the following actions.

- Copy the files of this project and integrate them in the way which works
best for you.  The beginning of each file contains the parameters you need to
modify so that they fit your configuration.

- Run `sync_usenet_hierarchies.py` at least daily
as a cron job.  This script downloads information from
[ftp.isc.org](https://ftp.isc.org/pub/usenet/CONFIG/) about Usenet
hierarchies: newsgroups with their descriptions, rules for processing control
articles, and PGP keys.  The files will be downloaded into the paths specified
in `libusenet_hierarchies.py`, and then be processed.

- Put in your web directory `index.py`, a script which generates an HTML page
in response to an HTTP request.  It should be part of your web pages along
with `.htaccess`, `favicon.ico`, and `style.css`.  Your Apache configuration,
if running that web server, needs declaring the use of embedded `mod_wsgi`
with something like that in the corresponding VirtualHost:

```ApacheConf
    WSGIScriptAlias /hierarchies /home/iulius/public_html/usenet/hierarchies/index.py process-group=usenet.trigofacile.com
    WSGIDaemonProcess usenet.trigofacile.com
    WSGIProcessGroup usenet.trigofacile.com
```

- If you wish to use URL rewriting to have nice URLs like
http://usenet.trigofacile.com/hierarchies/checkgroups/fr.txt instead of
http://usenet.trigofacile.com/hierarchies/index.py?see=FR&only=checkgroups,
enable the `mod_rewrite` Apache module, set `_REWRITEURL` to `True` in
`index.py`, and ensure the `RewriteRule` lines in `.htaccess` fit your
installation.  Otherwise, just set `_REWRITEURL` to `False` and comment the
`RewriteRule` lines in `.htaccess`.
