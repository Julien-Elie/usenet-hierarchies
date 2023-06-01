#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Download information from ftp.isc.org about Usenet hierarchies
# (newsgroups with their descriptions, rules for control articles, PGP keys).
#
# This script is primarily used to generate the web pages at:
#   http://usenet.trigofacile.com/hierarchies/
#
# Original version written in 2007, and maintained since then by Julien ÉLIE.
#
# Github repository to view the latest source code and report possible issues:
#   https://github.com/Julien-Elie/usenet-hierarchies/
#
# SPDX-License-Identifier: MIT

import bz2
import os.path
import sys
import time
import unidecode
import urllib

# Import required libusenet_hierarchies library.
# Customize the path to fit your configuration.
_LIBUSENET = "/home/iulius/scripts/usenet"
sys.path.insert(0, _LIBUSENET)
import libusenet_hierarchies

# URL to ftp.isc.org and your local web site.
URL_ISC_CONFIG = "https://ftp.isc.org/pub/usenet/CONFIG/"
URL_ISC_CONTROL = "https://ftp.isc.org/pub/pgpcontrol/"
URL_LOCAL = "http://usenet.trigofacile.com/hierarchies/index.py"

# Whether to use a local mirror (rsync = True) or download the files from
# ftp.isc.org (rsync = False).
# Default to True for usenet.trigofacile.com which is mirroring
# archives.eyrie.org, but that may not be the case for other installations.
rsync = True

# Whether to download the controlperm, control.conf, control.ctl and PGPKEYS
# files generated by the local web site (default is True).
# This permits providing these files, organized differently than the original
# ones (for control.ctl and PGPKEYS).
download = True

# Whether to parse the files to generate the database (default is True).
parse = True

# Whether to generate ASCII and UTF-8 newsgroups descriptions (default is
# True).
descriptions = True


if not rsync:
    urllib.urlretrieve(
        URL_ISC_CONTROL + "PGPKEYS",
        libusenet_hierarchies._PGPKEYS,
    )
    urllib.urlretrieve(
        URL_ISC_CONFIG + "control.ctl",
        libusenet_hierarchies._CONTROL,
    )
    # Save bandwidth with the bz2 compressed file.
    urllib.urlretrieve(
        URL_ISC_CONFIG + "newsgroups.bz2",
        libusenet_hierarchies._NEWSGROUPS + ".bz2",
    )

    today = time.strftime("%Y-%m", time.gmtime(time.time()))
    yesterday = time.strftime("%Y-%m", time.gmtime(time.time() - 86400))

    # If it is the first day of the month, also download the logs of the
    # previous month to be sure we have the latest updates.
    if today == yesterday:
        logs = [today]
    else:
        logs = [today, yesterday]

    for log in logs:
        urllib.urlretrieve(
            URL_ISC_CONFIG + "LOGS/log." + log,
            os.path.join(libusenet_hierarchies._LOGS, "log." + log),
        )

    newsgroups_file = file(libusenet_hierarchies._NEWSGROUPS, "w")
    for line in bz2.BZ2File(
        libusenet_hierarchies._NEWSGROUPS + ".bz2", "rb"
    ).read():
        newsgroups_file.write(line)
    newsgroups_file.close()


if download:
    urllib.urlretrieve(
        URL_LOCAL + "?see=ALL&only=control&controlstyle=cnews",
        os.path.join(libusenet_hierarchies._PATH, "controlperm"),
    )
    urllib.urlretrieve(
        URL_LOCAL + "?see=ALL&only=control&controlstyle=dnews",
        os.path.join(libusenet_hierarchies._PATH, "control.conf"),
    )
    urllib.urlretrieve(
        URL_LOCAL + "?see=ALL&only=control&controlstyle=inn",
        os.path.join(libusenet_hierarchies._PATH, "control.ctl"),
    )
    urllib.urlretrieve(
        URL_LOCAL + "?see=ALL&only=pgpkeys",
        os.path.join(libusenet_hierarchies._PATH, "PGPKEYS"),
    )


if parse:
    dictionary = dict()
    dictionary = libusenet_hierarchies._parse_control(
        libusenet_hierarchies._CONTROL, dictionary
    )

    dictionary = libusenet_hierarchies._parse_pgpkeys(
        libusenet_hierarchies._PGPKEYS, dictionary
    )

    dictionary = libusenet_hierarchies._parse_newsgroups(
        libusenet_hierarchies._NEWSGROUPS, dictionary
    )

    libusenet_hierarchies._dict2xml(
        dictionary, libusenet_hierarchies._DATABASE
    )

    libusenet_hierarchies._write_pretty_logs(
        libusenet_hierarchies._PRETTYLOGS, libusenet_hierarchies._LOGS
    )


if descriptions:
    newsgroups_ascii = file(libusenet_hierarchies._NEWSGROUPS_ASCII, "w")
    newsgroups_utf8 = file(libusenet_hierarchies._NEWSGROUPS_UTF8, "w")

    # Convert to UTF-8 the descriptions written with various encodings.
    for line in file(libusenet_hierarchies._NEWSGROUPS, "r"):
        group = line.split("\t")[0]
        hierarchy = group.split(".")[0]
        if hierarchy in ["cn", "han"]:
            utf8line = unicode(line, "gb18030").encode("utf-8")
        elif hierarchy in ["fido7", "medlux", "relcom"]:
            utf8line = unicode(line, "koi8-r").encode("utf-8")
        elif hierarchy in ["ukr"]:
            utf8line = unicode(line, "koi8-u").encode("utf-8")
        elif group in ["alt.am.wikipedia"]:
            utf8line = unicode(line, "iso-8859-15").encode("utf-8")
        elif hierarchy in ["nctu", "ncu", "tw"] or group in [
            "scout.forum.chinese",
            "scout.forum.korean",
        ]:
            utf8line = unicode(line, "big5").encode("utf-8")
        elif hierarchy in ["eternal-september", "fido", "fr"]:
            utf8line = line
        else:
            utf8line = unicode(line, "cp1252").encode("utf-8")
        newsgroups_ascii.write(unidecode.unidecode(utf8line.decode("utf-8")))
        newsgroups_utf8.write(utf8line)

    newsgroups_ascii.close()
    newsgroups_utf8.close()
