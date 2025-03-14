#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script used to generate the web pages at:
#   http://usenet.trigofacile.com/hierarchies/
#
# Original version written in 2007, and maintained since then by Julien ÉLIE.
#
# Github repository to view the latest source code and report possible issues:
#   https://github.com/Julien-Elie/usenet-hierarchies/
#
# SPDX-License-Identifier: MIT

import cgi
import re
import sys
import time
import urlparse

# URL and paths to customize, to fit your configuration.
_WEBSITE = "http://usenet.trigofacile.com"
_FAVICON = "/favicon.ico"
_STYLE = "/style.css"
_SUBDIR = "/hierarchies/"

# Enable if URL rewriting is on.
_REWRITEURL = True

# These URLs may be local paths if you're hosting a mirror.
_URL_CONTROL_ISC = "https://ftp.isc.org/usenet/control/"
_URL_LOGS_ISC = "https://ftp.isc.org/usenet/CONFIG/LOGS/"

# Import required libusenet_hierarchies library.
_LIBUSENET = "/home/iulius/scripts/usenet"
sys.path.insert(0, _LIBUSENET)
import libusenet_hierarchies

# Texts displayed at the top of web pages.
_MANAGED = (
    "<p>A public managed hierarchy is a publically available hierarchy for"
    " which someone maintains the canonical list of its newsgroups.</p>\n"
)
_UNMANAGED = (
    "<p>An unmanaged hierarchy is a hierarchy in which everyone can create"
    " a newsgroup.  There is no official, generally accepted policy.  The"
    " proponent sends creation articles himself, and there isn't any hierarchy"
    " manager who sends a list of current newsgroups in the hierarchy.  The"
    " list of actually carried newsgroups is usually different between news"
    " servers.</p>\n"
)
_PRIVATE = (
    "<p>A private hierarchy should only be carried after making arrangements"
    " with the given contact address for it.</p>\n"
)
_LOCAL = (
    "<p>A local hierarchy is a private hierarchy intended to be used only by"
    " the organization itself.  It is not generally distributed.</p>\n"
)
_RESERVED = (
    "<p>A reserved hierarchy, as defined by"
    ' <a href="https://datatracker.ietf.org/doc/html/rfc5536#section-3.1.4">'
    " Section 3.1.4 of RFC 5536</a>, must not be used for regular newsgroups;"
    " it is used by some news implementations as a special hierarchy.</p>\n"
)
_HISTORIC = (
    "<p>A historic hierarchy is not entirely defunct, but it is very"
    " low-traffic, not widely read or carried, and may not be worth"
    " carrying.  For most of them, no information is available, except a list"
    " of their hypothetical newsgroups.</p>\n"
)
_DEFUNCT = "<p>A defunct hierarchy is no longer used.</p>\n"

_DISCLAIMER = (
    "<p><strong>Please remove all groups in such a hierarchy from your news"
    " server, unless you've contacted the listed contact address and arranged"
    " a feed.  If you have permission to carry them, you should change the"
    " entries hereby provided for their control articles.</strong></p>\n"
)

_UPDATE = (
    "<p><em>If you know a hierarchy which is not listed in these pages or if"
    " you have more up-to-date information about an existing hierarchy, please"
    " send a mail to"
    ' <a href="mailto:usenet-config@isc.org">usenet-config@isc.org</a>'
    " or post to"
    ' <a href="news:news.admin.hierarchies">news.admin.hierarchies</a>'
    " so that these pages can be updated.</em></p>\n"
)

_SEVERAL = (
    "<p>You can display information about up to 30 hierarchies in the row by"
    " loading a web page of the form:<br>"
    '\n<a href="'
    + _SUBDIR
    + (
        'comp,humanities,misc,news,rec,sci,soc,talk.html">'
        if _REWRITEURL
        else 'index.py?see=COMP,HUMANITIES,MISC,NEWS,REC,SCI,SOC,TALK">'
    )
    + _WEBSITE
    + _SUBDIR
    + (
        "comp,humanities,misc,news,rec,sci,soc,talk.html"
        if _REWRITEURL
        else "index.py?see=COMP,HUMANITIES,MISC,NEWS,REC,SCI,SOC,TALK"
    )
    + "</a> (example for the Big 8).</p>\n"
)

_CHECKLOGS = (
    '[check <a href="'
    + _URL_LOGS_ISC
    + '">raw logs</a> if your checkgroups differs from the one below]'
)

_SOURCE = (
    "<p><em>Information in these pages comes from"
    ' <a href="https://ftp.isc.org/pub/usenet/CONFIG/control.ctl">INN\'s'
    " control.ctl</a>,"
    ' <a href="https://ftp.isc.org/pub/usenet/CONFIG/newsgroups">ftp.isc.org'
    " newsgroups file</a>,"
    ' <a href="https://ftp.isc.org/pub/pgpcontrol/README.html">the list of PGP'
    " public keys for newsgroup administration</a> and"
    ' <a href="https://ftp.isc.org/pub/usenet/CONFIG/LOGS/">the logs of'
    " control messages</a>.</em><br>\n<em>Those external data are used to"
    " generate this web site.  To report an issue about the generation, please"
    " use the "
    ' <a href="https://github.com/Julien-Elie/usenet-hierarchies/issues">issue'
    " tracker on GitHub</a> or post to"
    ' <a href="news:news.admin.hierarchies">news.admin.hierarchies</a>.'
    " </em><br>\n<em>You might also want to read"
    ' <a href="https://www.eyrie.org/~eagle/faqs/usenet-hier.html">the Usenet'
    " hierarchy administration FAQ</a>.</em></p>\n"
)


def _html_begin(title):
    """Return the beginning of the HTML page."""
    answer = (
        """<!DOCTYPE html>
<html lang="en">
<head>
<title>"""
        + title
        + '''</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="stylesheet" href="'''
        + _STYLE
        + '''" type="text/css">
<link rel="shortcut icon" href="'''
        + _FAVICON
        + """" type="image/x-icon">
<meta name="robots" content="index, follow, all">
</head>
<body>
<h1 id="top">"""
        + title
        + '''</h1>
<p class="navigation">
<a href="'''
        + _SUBDIR
        + (
            "managed-hierarchies.html"
            if _REWRITEURL
            else "index.py?status=managed"
        )
        + '">Public managed hierarchies</a> | <a href="'
        + _SUBDIR
        + (
            "unmanaged-hierarchies.html"
            if _REWRITEURL
            else "index.py?status=unmanaged"
        )
        + '">Unmanaged hierarchies</a> | <a href="'
        + _SUBDIR
        + (
            "private-hierarchies.html"
            if _REWRITEURL
            else "index.py?status=private"
        )
        + '">Private hierarchies</a> | <a href="'
        + _SUBDIR
        + (
            "local-hierarchies.html"
            if _REWRITEURL
            else "index.py?status=local"
        )
        + '">Local hierarchies</a> | <a href="'
        + _SUBDIR
        + (
            "reserved-hierarchies.html"
            if _REWRITEURL
            else "index.py?status=reserved"
        )
        + '">Reserved hierarchies</a> | <a href="'
        + _SUBDIR
        + (
            "historic-hierarchies.html"
            if _REWRITEURL
            else "index.py?status=historic"
        )
        + '">Historic hierarchies</a> | <a href="'
        + _SUBDIR
        + (
            "defunct-hierarchies.html"
            if _REWRITEURL
            else "index.py?status=defunct"
        )
        + '">Defunct hierarchies</a> | <a href="'
        + _SUBDIR
        + (
            "notes-about-hierarchies.html"
            if _REWRITEURL
            else "index.py?status=notes-about"
        )
        + """">Miscellaneous notes</a>
</p>
"""
    )
    return answer


def _html_end():
    """Return the end of the HTML page."""
    answer = (
        '<p class="bottom"><a href="#top">&uarr; Return to top of'
        " page</a></p>\n<hr>\n" + _SEVERAL + _SOURCE + "</body>\n</html>"
    )
    return answer


def _anchorify(text, mailModif=True, urlModif=True):
    """Recognize URL and mail patterns, and HTMLify them."""
    text = cgi.escape(text)
    if mailModif:
        text = re.sub(
            "([_a-zA-Z0-9-+]+)(\\.[_a-zA-Z0-9-+]+)*"
            "@([a-zA-Z0-9-]+)(\\.[a-zA-Z0-9-]+)*(\\.[a-zA-Z]{2,4})",
            '<a href="mailto:\\g<0>">\\g<0></a>',
            text,
        )
    if urlModif:
        text = re.sub(
            "(ftp|http|https):\\/\\/(\\w+:{0,1}\\w*@)?"
            "(\\S+)(:[0-9]+)?(\\/|\\/([\\w#!:.?+=&%@!\\-\\/]))?",
            '<a href="\\g<0>">\\g<0></a>',
            text,
        )
    return text


def _print_list_hierarchies(hierlist):
    """Return the HTML list of hierarchies."""
    answer = "<ul>\n"
    for h, d in hierlist:
        answer += (
            '<li><a href="'
            + _SUBDIR
            + (h.lower() + ".html" if _REWRITEURL else "index.py?see=" + h)
            + '">'
            + h
            + "</a>"
        )
        if d:
            answer += " (" + _anchorify(d) + ")"
        answer += "</li>\n"
    answer += "</ul>\n"
    return answer


def _print_control_entry(dictionary, name, text=True, controlstyle="inn"):
    """Write a control.ctl, control.conf or controlperm entry."""
    h = libusenet_hierarchies.Hierarchy()
    h.dict2hier({name: dictionary.get(name, {})})
    answer = ""

    if text:
        # First line:
        # ## hierarchy (status -- description)
        line = "## " + h.name + " ("
        if not h.status[0].endswith("MANAGED"):
            line += "*" + h.status[0] + "* -- "
        if h.description:
            line += h.description[0]
        answer += line + ")\n"

        for contact in h.contact:
            answer += "# Contact: " + contact + "\n"
        for group in h.admin_group:
            answer += "# Admin group: " + group + "\n"
        for url in h.url:
            answer += "# URL: " + url + "\n"
        for server in h.syncable_server:
            answer += "# Syncable server: " + server + "\n"
        for url in h.key_url:
            answer += "# Key URL: " + url + "\n"
        for fingerprint in h.key_fingerprint:
            answer += "# Key fingerprint: " + fingerprint + "\n"
        for comment in h.comments:
            answer += comment.replace("<br>", "\n") + "\n"
        for note in h.notes:
            answer += note.replace("<br>", "\n") + "\n"

    for item in h.control:
        # We need to *copy* it (a deepcopy is not necessary here).
        control = [
            item[0].encode("utf-8"),
            item[1].encode("utf-8"),
            item[2].encode("utf-8"),
            item[3].encode("utf-8"),
        ]
        if controlstyle == "cnews":
            if control[2].endswith(".*"):
                control[2] = control[2][:-2]
            if control[1] == "*":
                control[1] = "any"
            if control[3] == "doit":
                param = "yv"
            elif control[3] == "drop":
                param = "nq"
            elif control[3] in ["log", "mail"]:
                param = "nv"
            # pgp
            else:
                param = "pv " + control[3]
            answer += (
                " ".join([control[2], control[1], control[0][0], param]) + "\n"
            )
        elif controlstyle == "dnews":
            # pgp
            if control[3] not in ["doit", "drop", "log", "mail"]:
                control[3] = "doit,pgp"
            answer += ":".join(control) + "\n"
        else:
            # pgp, so add 'verify-'
            if control[3] not in ["doit", "drop", "log", "mail"]:
                control[3] = "verify-" + control[3]
            answer += ":".join(control) + "\n"
    return answer


def _page_list_hierarchies(dictionary, status):
    """What appears when a status is given (list of hierarchies)."""
    if status == "private":
        answer = _html_begin("List of Usenet private hierarchies")
        answer += _UPDATE + _PRIVATE + _DISCLAIMER
        answer += "<h2>Private hierarchies</h2>\n"
        answer += _print_list_hierarchies(
            libusenet_hierarchies._list_hierarchies(
                dictionary, "status", "PRIVATE"
            )
        )
    elif status == "local":
        answer = _html_begin("List of Usenet local hierarchies")
        answer += _UPDATE + _LOCAL + _DISCLAIMER
        answer += "<h2>Local hierarchies</h2>\n"
        answer += _print_list_hierarchies(
            libusenet_hierarchies._list_hierarchies(
                dictionary, "status", "LOCAL"
            )
        )
    elif status == "reserved":
        answer = _html_begin("List of Usenet reserved hierarchies")
        answer += _UPDATE + _RESERVED
        answer += "<h2>Reserved hierarchies</h2>\n"
        answer += _print_list_hierarchies(
            libusenet_hierarchies._list_hierarchies(
                dictionary, "status", "RESERVED"
            )
        )
    elif status == "historic":
        answer = _html_begin("List of Usenet historic hierarchies")
        answer += _UPDATE + _HISTORIC
        answer += "<h2>Historic hierarchies</h2>\n"
        answer += _print_list_hierarchies(
            libusenet_hierarchies._list_hierarchies(
                dictionary, "status", "HISTORIC"
            )
        )
    elif status == "defunct":
        answer = _html_begin("List of Usenet defunct hierarchies")
        answer += _UPDATE + _DEFUNCT
        answer += "<h2>Defunct hierarchies</h2>\n"
        answer += _print_list_hierarchies(
            libusenet_hierarchies._list_hierarchies(
                dictionary, "status", "DEFUNCT"
            )
        )
    elif status == "unmanaged":
        answer = _html_begin("List of Usenet unmanaged hierarchies")
        answer += _UPDATE + _UNMANAGED
        answer += "<h2>Unmanaged hierarchies</h2>\n"
        answer += _print_list_hierarchies(
            libusenet_hierarchies._list_hierarchies(
                dictionary, "status", "UNMANAGED"
            )
        )
    elif status == "notes-about":
        answer = _html_begin("Miscellaneous notes about Usenet hierarchies")
        beginHier = False
        beginNotes = False
        beginPar = False
        for line in file(libusenet_hierarchies._HIERARCHY_NOTES, "r"):
            line = line.rstrip()
            if line.startswith("   "):
                # Main title.
                continue
            elif line.startswith(" "):
                # We're reading the notes for a hierarchy.
                if not beginNotes:
                    answer += "<dd>"
                    beginNotes = True
                line = line.replace("Gabor", "Gábor")
                line = line.replace("Nandor", "Nándor")
                line = line.replace("Horvath", "Horváth")
                answer += cgi.escape(line[2:]) + " "
            elif line.endswith(".*") and not line.startswith(" "):
                # New hierarchy.
                if not beginHier:
                    answer += "<dl>"
                    beginHier = True
                if beginNotes:
                    answer += "</dd>\n"
                    beginNotes = False
                hierName = line[:-2]
                if hierName.upper() in dictionary:
                    answer += (
                        '<dt><a href="'
                        + _SUBDIR
                        + (
                            hierName + ".html"
                            if _REWRITEURL
                            else "index.py?see=" + hierName
                        )
                        + '">'
                        + line
                        + "</a></dt>\n"
                    )
                else:
                    answer += "<dt>" + line + "</dt>\n"
            elif not line:
                if beginPar:
                    answer += "</p>\n"
                    beginPar = False
                if beginNotes:
                    answer += "</dd>\n"
                    beginNotes = False
                if beginHier:
                    answer += "</dl>\n"
                    beginHier = False
            elif line.startswith("=== "):
                answer += "<h2>" + line.replace("=", "") + "</h2>\n"
            else:
                if not beginPar:
                    answer += "<p>"
                    beginPar = True
                line = line.replace(
                    "opening an issue at",
                    '<a href="https://github.com/Julien-Elie/'
                    + 'usenet-hierarchies/issues">opening an issue</a>.',
                )
                line = line.replace(
                    "<https://github.com/Julien-Elie/"
                    + "usenet-hierarchies/issues>.",
                    "",
                )
                line = line.replace(
                    "old Master List of Newsgroup Hierarchies",
                    '<a href="https://web.archive.org/web/20160407174854/'
                    + 'http://pfx.ca/mlnh/mlnhtables.html">'
                    + "old Master List of Newsgroup Hierarchies</a>",
                )
                line = line.replace(
                    "<https://web.archive.org/web/20160407174854/"
                    + "http://pfx.ca/mlnh/mlnhtables.html>",
                    "",
                )
                line = line.replace(
                    "<https://raw.githubusercontent.com/Julien-Elie/"
                    + "usenet-hierarchies/main/nas/data/hierarchies/"
                    + "Description>",
                    '<a href="https://raw.githubusercontent.com/Julien-Elie/'
                    + "usenet-hierarchies/main/nas/data/hierarchies/"
                    + 'Description">a merged list of hierarchies</a>',
                )
                line = line.replace("_many_", "<em>many</em>")
                answer += line + " "
        if beginNotes:
            answer += "</dd>\n"
        if beginHier:
            answer += "</dl>\n"
    else:
        answer = _html_begin("List of Usenet public managed hierarchies")
        answer += _UPDATE + _MANAGED
        answer += "<h2>PGP-managed hierarchies</h2>\n"
        answer += _print_list_hierarchies(
            libusenet_hierarchies._list_hierarchies(
                dictionary, "status", "PGPMANAGED"
            )
        )
        answer += "<h2>Other managed hierarchies</h2>\n"
        answer += _print_list_hierarchies(
            libusenet_hierarchies._list_hierarchies(
                dictionary, "status", "MANAGED"
            )
        )
    return answer


def _page_info_hierarchies(dictionary, hierlist, controlstyle):
    """What appears when a list of hierarchies is given (information about
    them)."""
    controlfiles = {
        "cnews": "controlperm",
        "dnews": "control.conf",
        "inn": "control.ctl",
    }
    answer = _html_begin("Information about Usenet hierarchies")
    answer += (
        _UPDATE
        + "<p>A text-only version of that page can also be retrieved for"
        ' <a href="'
        + _SUBDIR
        + (
            controlfiles.get(controlstyle, "control.ctl")
            + "/"
            + ",".join(hierlist).lower()
            + ".txt"
            if _REWRITEURL
            else "index.py?see="
            + ",".join(hierlist)
            + "&amp;controlstyle="
            + controlstyle
            + "&amp;only=control"
        )
        + '">a <em>'
        + controlfiles[controlstyle]
        + '</em> access file</a>, <a href="'
        + _SUBDIR
        + (
            "pgpkeys/" + ",".join(hierlist).lower() + ".txt"
            if _REWRITEURL
            else "index.py?see=" + ",".join(hierlist) + "&amp;only=pgpkeys"
        )
        + '">PGP keys</a> and <a href="'
        + _SUBDIR
        + (
            "checkgroups/" + ",".join(hierlist).lower() + ".txt"
            if _REWRITEURL
            else "index.py?see=" + ",".join(hierlist) + "&amp;only=checkgroups"
        )
        + '">a checkgroups</a>.  <a href="'
        + _SUBDIR
        + 'data/">Full files</a> are also available.</p>\n'
    )

    prettylogs = []
    for line in file(libusenet_hierarchies._PRETTYLOGS, "r"):
        prettylogs.append(line.strip())

    newsgroups = []
    for line in file(libusenet_hierarchies._NEWSGROUPS_UTF8, "r"):
        newsgroups.append(line.strip())

    seen = []
    if len(hierlist) > 30:
        answer += (
            "<p><strong>Only the first 30 asked hierarchies are"
            " displayed.</strong></p>"
        )
        hierlist = hierlist[:30]
    for item in hierlist:
        if item in seen:
            continue
        seen.append(item)
        item = item.upper()
        answer += "<h2>Hierarchy " + item + "</h2>\n"
        answer += "<ul>\n"

        if item in dictionary:
            d = dictionary[item]

            if "description" in d:
                answer += (
                    "<li>Description: "
                    + _anchorify(d["description"][0])
                    + "</li>\n"
                )
            else:
                answer += "<li><em>No description provided</em></li>\n"

            if "status" in d:
                answer += "<li>Status: " + d["status"][0].lower() + "</li>\n"

            if "contact" in d:
                for contact in d["contact"]:
                    answer += (
                        "<li>Contact: "
                        + _anchorify(contact, urlModif=False)
                        + "</li>\n"
                    )
            else:
                answer += "<li><em>No contact information provided</em></li>\n"

            if "admin_group" in d:
                for group in d["admin_group"]:
                    answer += (
                        '<li>Administrative group: <a href="news:'
                        + group
                        + '">'
                        + group
                        + "</a></li>\n"
                    )
            else:
                answer += (
                    "<li><em>No administrative group provided</em></li>\n"
                )

            if "url" in d:
                for url in d["url"]:
                    answer += (
                        "<li>URL: "
                        + _anchorify(url, mailModif=False)
                        + "</li>\n"
                    )
            else:
                answer += "<li><em>No URL provided</em></li>\n"

            if "syncable_server" in d:
                for server in d["syncable_server"]:
                    answer += (
                        '<li>Syncable server: <a href="news://'
                        + server
                        + '/">'
                        + server
                        + "</a></li>\n"
                    )

            if "key_id" in d:
                for id in d["key_id"]:
                    answer += "<li>Key User ID: " + cgi.escape(id) + "</li>\n"

            if "key_url" in d:
                for url in d["key_url"]:
                    answer += (
                        "<li>Key URL: "
                        + _anchorify(url, mailModif=False)
                        + "</li>\n"
                    )
            elif "key_id" in d:
                answer += "<li><em>No key URL provided</em></li>\n"

            if "key_fingerprint" in d:
                for fingerprint in d["key_fingerprint"]:
                    answer += (
                        "<li>Key fingerprint: "
                        + fingerprint.replace(" ", "&nbsp;")
                        + "</li>\n"
                    )
            elif "key_id" in d:
                answer += "<li><em>No key fingerprint provided</em></li>\n"

            if "key" in d:
                answer += '<li><p>Key:</p>\n<pre class="key">\n'
                for line in d["key"]:
                    answer += line.replace("<br>", "\n") + "\n"
                answer += "</pre></li>\n"
            else:
                answer += "<li><em>No PGP key provided</em></li>\n"

            if "comments" in d:
                answer += '<li><p>Comments:</p>\n<pre class="comment">\n'
                for comment in d["comments"]:
                    answer += (
                        cgi.escape(comment).replace("&lt;br&gt;", "\n") + "\n"
                    )
                answer += "</pre></li>\n"

            if "notes" in d:
                answer += '<li><p>Historic notes:</p>\n<pre class="comment">\n'
                for note in d["notes"]:
                    answer += (
                        cgi.escape(note).replace("&lt;br&gt;", "\n") + "\n"
                    )
                answer += "</pre></li>\n"

            if "control" in d:
                answer += (
                    "<li><p>INN's <em>control.ctl</em> entry:</p>\n"
                    '<pre class="control">\n'
                    + _print_control_entry(dictionary, item, False, "inn")
                    + "</pre>\n<details><summary>Click to see C News'"
                    " <em>controlperm</em> entry"
                    '</summary>\n<pre class="control">\n'
                    + _print_control_entry(dictionary, item, False, "cnews")
                    + "</pre></details>\n<details><summary>Click to see DNews'"
                    " <em>control.conf</em> entry"
                    '</summary>\n<pre class="control">\n'
                    + _print_control_entry(dictionary, item, False, "dnews")
                    + "</pre></details><p>&nbsp;</p></li>\n"
                )

            hierarchy = item.lower() + "."
            actions = []
            nextactions = []
            changegroup = []
            for line in prettylogs:
                elem = line.split()
                if elem[3].startswith(hierarchy):
                    if elem[2] == "changegroup":
                        if (
                            len(elem) < 8
                            or len(elem[5]) != 1
                            or len(elem[7]) != 1
                        ):
                            continue
                        if line.endswith("(manual)"):
                            changegroup.append(line)
                        elif line.endswith("(by checkgroups)"):
                            changegroup.append(
                                line.replace(
                                    "by checkgroups",
                                    '<a href="'
                                    + _URL_CONTROL_ISC
                                    + "other.ctl/checkgroups."
                                    + elem[0][:4]
                                    + '.gz">by checkgroups</a>',
                                )
                            )
                        else:
                            changegroup.append(
                                line
                                + ' (<a href="'
                                + _URL_CONTROL_ISC
                                + hierarchy[:-1]
                                + "/"
                                + elem[3]
                                + '.gz">by control article</a>)'
                            )
                    if line.endswith("(manual)"):
                        pass
                    elif line.endswith("(by checkgroups)"):
                        line = line.replace(
                            "by checkgroups",
                            '<a href="'
                            + _URL_CONTROL_ISC
                            + "other.ctl/checkgroups."
                            + elem[0][:4]
                            + '.gz">by checkgroups</a>',
                        )
                    else:
                        line += (
                            ' (<a href="'
                            + _URL_CONTROL_ISC
                            + hierarchy[:-1]
                            + "/"
                            + elem[3]
                            + '.gz">by control article</a>)'
                        )
                    # Only display by default the action if it occurred within
                    # the year.
                    # 365*24*60*60 = 31536000 seconds in a year.
                    timestamp = time.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
                    delta = time.mktime(time.gmtime()) - time.mktime(timestamp)
                    if delta > 31536000:
                        nextactions.append(line)
                    else:
                        actions.append(line)
            if changegroup:
                answer += (
                    "<li><p>Newsgroups which have had retrocharters changing"
                    " their moderation flags: [make sure such changes are"
                    ' legitimate]</p>\n<pre class="actions">\n'
                )
                for action in changegroup:
                    answer += action + "\n"
                answer += "</pre></li>\n"
            if actions:
                answer += (
                    '<li><p>Actions since a year:</p>\n<pre class="actions">\n'
                )
                for action in actions:
                    answer += action + "\n"

                answer += "</pre>\n"
                if nextactions:
                    answer += (
                        "<details><summary>Click to see more actions"
                        " (since May 2003)"
                        '</summary>\n<pre class="actions">\n'
                    )
                    for nextaction in nextactions:
                        answer += nextaction + "\n"
                    answer += "</pre></details><p>&nbsp;</p>"
                answer += "</li>\n"
            else:
                if nextactions:
                    answer += (
                        "<li><p>Actions since a year: none</p>\n"
                        "<details><summary>Click to see more actions"
                        " (since May 2003)"
                        '</summary>\n<pre class="actions">\n'
                    )
                    for nextaction in nextactions:
                        answer += nextaction + "\n"
                    answer += "</pre></details><p>&nbsp;</p></li>\n"
                else:
                    answer += "<li><p>Actions since May 2003: none</p></li>\n"

            matched = []
            for line in newsgroups:
                if line.startswith(hierarchy):
                    matched.append(line)
            if matched:
                answer += (
                    "<li><p>Newsgroups: "
                    + _CHECKLOGS
                    + '</p>\n<pre class="newsgroups">\n'
                )
                for line in matched:
                    answer += cgi.escape(line) + "\n"
                answer += "</pre></li>\n"
            else:
                answer += (
                    "<li><p>Newsgroups: none "
                    + _CHECKLOGS
                    + "<br>&nbsp;</p></li>\n"
                )
        else:
            answer += (
                "<li><strong>That hierarchy is unknown.  Please tell us if it"
                " really exists.</strong></li>\n"
            )
        answer += "</ul>\n"
    return answer


def application(environ, start_response):
    httpstatus = "200 OK"
    answer = ""

    query = urlparse.parse_qs(environ["QUERY_STRING"])
    status = cgi.escape(query.get("status", ["managed"])[0])
    see = cgi.escape(query.get("see", [""])[0])
    controlstyle = cgi.escape(query.get("controlstyle", ["inn"])[0])
    only = cgi.escape(query.get("only", [""])[0])

    # As the information is not provided in the query string after RewriteRule
    # rewrites the URL, we need to compute it.
    if _REWRITEURL and "controlstyle" not in query:
        if only == "control.conf":
            only = "control"
            controlstyle = "dnews"
        elif only == "controlperm":
            only = "control"
            controlstyle = "cnews"
        else:
            if only.startswith("control"):
                only = "control"
            controlstyle = "inn"

    dictionary = libusenet_hierarchies._xml2dict(
        libusenet_hierarchies._DATABASE
    )
    dictionary = libusenet_hierarchies._add_info(dictionary)

    hierlist = see.upper().split(",")
    seen = []

    if only:
        content_type = "text/plain; charset=utf-8"
        if hierlist == ["ALL"]:
            answer += (
                "## Generated at <" + _WEBSITE + _SUBDIR + ">.\n"
                "## Based on <https://ftp.isc.org/pub/usenet/CONFIG/>.\n\n"
            )
            hierlist = sorted(dictionary.keys())
        if only == "control":
            for item in hierlist:
                if item in seen:
                    continue
                seen.append(item)
                if item in dictionary:
                    answer += _print_control_entry(
                        dictionary, item, True, controlstyle
                    )
                    answer += "\n"
        elif only == "pgpkeys":
            for item in hierlist:
                if item in dictionary:
                    if "key_id" in dictionary[item]:
                        if dictionary[item]["key_id"][0] in seen:
                            continue
                        seen.append(dictionary[item]["key_id"][0])
                        answer += "## " + item + " ##\n\n"
                        for line in dictionary[item].get("key", []):
                            answer += line.replace("<br>", "\n")
                            answer += "\n\n"
        elif only == "checkgroups":

            def trans(item):
                return item.lower() + "."

            hierlist = list(map(trans, hierlist))
            for line in file(libusenet_hierarchies._NEWSGROUPS_UTF8):
                for item in hierlist:
                    if line.startswith(item):
                        answer += line
        # Always write something to prevent the error
        # "mod_python.publisher: nothing to publish".
        # Though we no longer use mod_python, now deprecated, keeping that
        # write won't do any harm.
        answer += "\n"
    else:
        content_type = "text/html; charset=utf-8"
        if see:
            answer += _page_info_hierarchies(
                dictionary, hierlist, controlstyle
            )
        else:
            answer += _page_list_hierarchies(dictionary, status)
        answer += _html_end()

    response_headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(answer))),
    ]

    start_response(httpstatus, response_headers)

    return [answer]
