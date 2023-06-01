#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Generate and manipulate an XML document containing information about Usenet
# hierarchies.
#
# This library is primarily used to generate the web pages at:
#   http://usenet.trigofacile.com/hierarchies/
#
# Original version written in 2007, and maintained since then by Julien ÉLIE.
#
# Github repository to view the latest source code and report possible issues:
#   https://github.com/Julien-Elie/usenet-hierarchies/
#
# SPDX-License-Identifier: MIT

import codecs
import os
import os.path
from xml.dom.minidom import Document, parseString

# URL and paths to customize, to fit your configuration.
_PATH = "/home/iulius/public_html/usenet/hierarchies/data/"

# https://ftp.isc.org/pub/pgpcontrol/PGPKEYS
_PGPKEYS = os.path.join(_PATH, "isc/PGPKEYS")

# https://ftp.isc.org/pub/usenet/CONFIG/control.ctl
_CONTROL = os.path.join(_PATH, "isc/control.ctl")

# https://ftp.isc.org/pub/usenet/CONFIG/newsgroups
_NEWSGROUPS = os.path.join(_PATH, "isc/newsgroups")

# https://ftp.isc.org/pub/usenet/CONFIG/LOGS/
_LOGS = os.path.join(_PATH, "isc/LOGS/")

# Location of the files generated by this library.
_DATABASE = os.path.join(_PATH, "hierarchies.xml")
_NEWSGROUPS_ASCII = os.path.join(_PATH, "newsgroups.ascii")
_NEWSGROUPS_UTF8 = os.path.join(_PATH, "newsgroups.utf8")
_PRETTYLOGS = os.path.join(_PATH, "changelog")

# Attributes used in the XML document (except "name", which is a string for
# the name of the hierarchy -- for instance, NEWS).
# All the other attributes are *lists*, allowing several occurrences.
#
# status: from control.ctl (DEFUNCT, HISTORIC, LOCAL, PRIVATE, RESERVED)
#         PGPMANAGED, MANAGED, UNMANAGED, and HISTORIC added by _add_info().
# description: from control.ctl (after the name of the hierarchy)
# comments: from control.ctl (everything beginning with "#", which is kept)
# contact: from control.ctl and PGPKEYS
# admin_group: from control.ctl and PGPKEYS
# url: from control.ctl
# key: from PGPKEYS
# key_id: from control.ctl (verify-ID) and PGPKEYS
# key_url: from control.ctl and PGPKEYS
# key_fingerprint: from control.ctl
# syncable_server: from control.ctl
# control: from control.ctl ([message, sender, newsgroups, action]
#          where action does not contain 'verify-')
#
_ATTRIBUTES = [
    "status",
    "description",
    "comments",
    "contact",
    "admin_group",
    "url",
    "key",
    "key_id",
    "key_url",
    "key_fingerprint",
    "syncable_server",
    "control",
]


class Hierarchy:
    """A class useful to handle the information about hierarchies."""

    def __init__(self):
        """Create a new element of the class."""
        self.name = ""
        for attribute in _ATTRIBUTES:
            setattr(self, attribute, [])

    def __str__(self):
        """Pretty print."""
        return self.description

    def hier2dict(self):
        """Convert a Hierarchy to a dictionary."""
        d = dict()
        for attribute in _ATTRIBUTES:
            # Only existing attributes are put into the dictionary.
            if getattr(self, attribute):
                d[attribute] = getattr(self, attribute)
        return {self.name: d}

    def dict2hier(self, d):
        """Convert a dictionary to a Hierarchy."""
        # Only the first hierarchy in the dictionary is processed.
        self.name = list(d.keys())[0]
        information = d[self.name]
        for attribute in _ATTRIBUTES:
            setattr(self, attribute, information.get(attribute, []))


def _update_dict(dictionary, d):
    """Update entries of dictionary with all the information
    available in d (new hierarchies and also attributes)."""
    for key in list(d.keys()):
        # New hierarchy found.
        if key not in dictionary:
            dictionary[key] = dict()
        # Update the provided attributes.
        for attribute in _ATTRIBUTES:
            if attribute in d[key]:
                if attribute in dictionary[key]:
                    for item in d[key][attribute]:
                        if not item in dictionary[key][attribute]:
                            dictionary[key][attribute].append(item)
                else:
                    dictionary[key][attribute] = d[key][attribute]
    return dictionary


def _dict2xml(dictionary, doc_path):
    """Convert a dictionary to an XML document."""
    doc = Document()
    # <usenet>
    root = doc.createElement("usenet")
    # Sort the XML document by hierarchy.
    hierarchies = sorted(dictionary.keys())
    for hierarchy in hierarchies:
        # hierarchy is a string (the name of the hierarchy).
        # <hierarchy>
        node_hier = doc.createElement("hierarchy")
        # <name>
        node = doc.createElement("name")
        node.appendChild(doc.createTextNode(hierarchy))
        node_hier.appendChild(node)
        # </name>
        information = dictionary[hierarchy]
        for key in list(information.keys()):
            # key is a string (the name of an attribute).
            for item in information[key]:
                # item is an element of the attribute value.
                # <attribute>
                node = doc.createElement(key)
                if key == "control":
                    # <message>
                    node2 = doc.createElement("message")
                    node2.appendChild(doc.createTextNode(item[0]))
                    node.appendChild(node2)
                    # </message>
                    # <sender>
                    node2 = doc.createElement("sender")
                    node2.appendChild(doc.createTextNode(item[1]))
                    node.appendChild(node2)
                    # </sender>
                    # <newsgroups>
                    node2 = doc.createElement("newsgroups")
                    node2.appendChild(doc.createTextNode(item[2]))
                    node.appendChild(node2)
                    # </newsgroups>
                    # <action>
                    node2 = doc.createElement("action")
                    node2.appendChild(doc.createTextNode(item[3]))
                    node.appendChild(node2)
                    # </action>
                else:
                    node.appendChild(doc.createTextNode(item))
                node_hier.appendChild(node)
                # </attribute>
        root.appendChild(node_hier)
        # </hierarchy>
    doc.appendChild(root)
    # </usenet>

    # Write the XML document.
    doc_file = codecs.open(doc_path, "w", "utf-8")
    doc_file.writelines(doc.toprettyxml(" ", "\n", "utf-8").decode("utf-8"))
    doc_file.close()


def _xml2dict(doc_path):
    """Convert an XML document to a dictionary."""
    dictionary = dict()
    document = codecs.open(doc_path, "r", "utf-8").read()
    doc = parseString(document.encode("utf-8"))
    # Search every hierarchy.
    for node in doc.getElementsByTagName("hierarchy"):
        # node is a hierarchy.
        d = dict()
        name = None
        for info in node.childNodes:
            # info is either 'name' or an attribute.
            if info.nodeName in _ATTRIBUTES:
                if info.nodeName == "control":
                    for info2 in info.childNodes:
                        if info2.nodeName == "message":
                            message = (info2.firstChild.nodeValue).strip()
                        elif info2.nodeName == "sender":
                            sender = (info2.firstChild.nodeValue).strip()
                        elif info2.nodeName == "newsgroups":
                            newsgroups = (info2.firstChild.nodeValue).strip()
                        elif info2.nodeName == "action":
                            action = (info2.firstChild.nodeValue).strip()
                    # Check whether d has such a key.
                    if info.nodeName in d:
                        d[info.nodeName].append(
                            [message, sender, newsgroups, action]
                        )
                    else:
                        d[info.nodeName] = [
                            [message, sender, newsgroups, action]
                        ]
                else:
                    # Check whether d has such a key.
                    if info.nodeName in d:
                        d[info.nodeName].append(
                            (info.firstChild.nodeValue).strip().encode("utf-8")
                        )
                    else:
                        d[info.nodeName] = [
                            (info.firstChild.nodeValue).strip().encode("utf-8")
                        ]
            elif info.nodeName == "name":
                name = (info.firstChild.nodeValue).strip().encode("utf-8")
        # If we have everything we need, update the dictionary.
        if name:
            dictionary = _update_dict(dictionary, {name: d})
    return dictionary


def _add_info(dictionary):
    """Add a possible PGPMANAGED, UNMANAGED, MANAGED, or HISTORIC status."""
    for hierarchy in list(dictionary.keys()):
        if "status" not in dictionary[hierarchy]:
            if list(dictionary[hierarchy].keys()):
                if "key" in dictionary[hierarchy]:
                    dictionary[hierarchy]["status"] = ["PGPMANAGED"]
                else:
                    # alt.* and free.* are special.
                    if hierarchy in ["ALT", "FREE"]:
                        dictionary[hierarchy]["status"] = ["UNMANAGED"]
                    else:
                        dictionary[hierarchy]["status"] = ["MANAGED"]
            else:
                dictionary[hierarchy]["status"] = ["HISTORIC"]
    return dictionary


def _parse_control(file_control, dictionary):
    """Parse the control.ctl file."""
    beginning = False
    hier = None
    for line in codecs.open(file_control, "r", "utf-8"):
        line = line.strip()
        if beginning:
            # A new hierarchy.
            # ## COMP, HUMANITIES, MISC, NEWS, REC, SCI, SOC, TALK (The Big 8)
            if line.startswith("## "):
                hier = Hierarchy()
                comments = ""
                controllist = line.split("(")
                hier.name = controllist[0]
                hier.name = hier.name.replace("#", "")
                hier.name = hier.name.replace(" ", "")
                hier.name = hier.name.replace("&", ",")
                # Sometimes, several hierarchies are in the same control.ctl
                # entry.
                names = hier.name.split(",")
                # We need to save the different entries for control articles.
                control = dict()
                for name in names:
                    control[name] = []
                if len(controllist) > 1:
                    controllist2 = controllist[1][:-1].split(" -- ")
                    if len(controllist2) == 1:
                        hier.description.append(controllist2[0])
                    else:
                        hier.status.append(controllist2[0].replace("*", ""))
                        hier.description.append(controllist2[1])
            elif line.startswith("# Contact:"):
                hier.contact.append(line.replace("# Contact: ", ""))
            elif line.startswith("# Admin group:"):
                hier.admin_group.append(line.replace("# Admin group: ", ""))
            elif line.startswith("# URL:"):
                hier.url.append(line.replace("# URL: ", ""))
            elif line.startswith("# Key URL:"):
                hier.key_url.append(line.replace("# Key URL: ", ""))
            elif line.startswith("# Key fingerprint:"):
                hier.key_fingerprint.append(
                    line.replace("# Key fingerprint: ", "")
                )
            elif line.startswith("# Syncable server:"):
                hier.syncable_server.append(
                    line.replace("# Syncable server: ", "")
                )
            # Not processing the line "# *PGP*   See comment at top of file.".
            elif line.startswith("# *PGP* "):
                continue
            # It must be a comment.
            elif line.startswith("#"):
                # Keep the wrapping and the "#" char too.
                if comments:
                    comments += "<br>"
                comments += line
            # It must be a control article entry or the end of the hierarchy
            # entry.
            elif hier:
                if (
                    line.startswith("checkgroups:")
                    or line.startswith("newgroup:")
                    or line.startswith("rmgroup:")
                ):
                    controllist = line.split(":")
                    # Remove 'verify-' if it exists.
                    if controllist[3].startswith("verify-"):
                        controllist[3] = controllist[3].replace("verify-", "")
                        if not controllist[3] in hier.key_id:
                            hier.key_id.append(controllist[3])
                    for name in names:
                        for wildmat in controllist[2].split("|"):
                            # Keep only the relevant newsgroups for the
                            # hierarchy.
                            if wildmat.startswith(name.lower()):
                                control[name].append(
                                    [
                                        controllist[0],
                                        controllist[1],
                                        wildmat,
                                        controllist[3],
                                    ]
                                )
                elif not line:
                    # All done for the hierarchy!
                    if comments:
                        hier.comments.append(comments)
                    for name in names:
                        hier.name = name
                        hier.control = control[name]
                        dictionary = _update_dict(dictionary, hier.hier2dict())
                    hier = None
        # Only begin with the first hierarchy.
        elif line.startswith("## Special reserved groups"):
            beginning = True
    # All done for the last hierarchy!
    if hier:
        if comments:
            hier.comments.append(comments)
        for name in names:
            hier.name = name
            hier.control = control[name]
            dictionary = _update_dict(dictionary, hier.hier2dict())
    return dictionary


def _parse_pgpkeys(file_pgpkeys, dictionary):
    """Parse the PGPKEYS file."""
    beginning = False
    pgp = False
    for line in codecs.open(file_pgpkeys, "r", "ISO-8859-1"):
        line = line.strip()
        if beginning:
            # A new hierarchy.
            if line.endswith("___________"):
                hier = Hierarchy()
            # elif line.startswith("Control message sender:"):
            #     hier.contact.append(
            #         line.replace("Control message sender: ", "")
            #     )
            elif line.startswith("Key User ID:"):
                hier.key_id.append(line.replace("Key User ID: ", ""))
            elif line.startswith("Administrative group:"):
                hier.admin_group.append(
                    line.replace("Administrative group: ", "")
                )
            elif line.startswith("+ "):
                hier.key_url.append(line.replace("+ ", ""))
            elif line == "-----BEGIN PGP PUBLIC KEY BLOCK-----":
                pgp = True
                key = line + "<br>"
            elif line == "-----END PGP PUBLIC KEY BLOCK-----":
                pgp = False
                key += line
                hier.key.append(key)
                # All done for the hierarchy!
                hier.name = hier.name.replace(" ", "")
                hier.name = hier.name.replace("&", ",")
                # Sometimes, several hierarchies share the same PGPKEYS entry.
                names = hier.name.split(",")
                for name in names:
                    hier.name = name
                    dictionary = _update_dict(dictionary, hier.hier2dict())
            elif pgp:
                key += line + "<br>"
            elif line and not hier.name:
                hier.name = line
        elif line.endswith("___________"):
            hier = Hierarchy()
            beginning = True
    return dictionary


def _parse_newsgroups(file_newsgroups, dictionary):
    """Parse the newsgroups file."""
    hierarchies = []
    prev = ""
    for line in codecs.open(file_newsgroups, "r"):
        newsgroupslist = line.split("\t")
        hierarchy = newsgroupslist[0].split(".")[0].upper()
        if hierarchy != prev:
            if prev:
                hierarchies.append(prev)
            prev = hierarchy
    # The last hierarchy.
    hierarchies.append(prev)
    d = dict()
    for h in hierarchies:
        d[h] = dict()
    return _update_dict(dictionary, d)


def _make_pretty_logs(logfile, actions):
    """Return a list of actions from the logs."""
    tempactions = []
    for line in codecs.open(logfile, "r"):
        line = line.strip()
        loglist = line.split()
        if len(loglist) < 5:
            continue
        elif line.endswith("(manual)"):
            actions.append(
                loglist[0] + " " + loglist[1] + " " + " ".join(loglist[4:])
            )
        elif loglist[4] == "processed":
            if loglist[5] == "checkgroups":
                for item in tempactions:
                    actions.append(item + " (by checkgroups)")
            elif tempactions:
                actions.append(tempactions[0])
            tempactions = []
        elif loglist[3] == "ACTION:":
            tempactions.append(
                loglist[0] + " " + loglist[1] + " " + " ".join(loglist[4:])
            )
    return actions


def _write_pretty_logs(file_prettylogs, path_logs):
    """Write pretty logs from a directory."""
    actions = []
    for log in sorted(os.listdir(path_logs)):
        logfile = os.path.join(path_logs, log)
        if os.path.isfile(logfile):
            actions = _make_pretty_logs(logfile, actions)
    actions.reverse()
    log_file = codecs.open(file_prettylogs, "w")
    for line in actions:
        log_file.write(line + "\n")
    log_file.close()


def _list_hierarchies(dictionary, key="all", value="all"):
    """Return the list of hierarchies matching key/value."""
    hierlist = []
    for hierarchy in list(dictionary.keys()):
        if key == "all" or key in dictionary[hierarchy]:
            if value == "all":
                hierlist.append(
                    (
                        hierarchy,
                        dictionary[hierarchy].get("description", [""])[0],
                    )
                )
            else:
                for item in dictionary[hierarchy][key]:
                    if item == value:
                        hierlist.append(
                            (
                                hierarchy,
                                dictionary[hierarchy].get("description", [""])[
                                    0
                                ],
                            )
                        )
    hierlist.sort()
    return hierlist


# For debugging purpose, when run interactively.
if __name__ == "__main__":
    dictionary = dict()
    dictionary = _parse_control(_CONTROL, dictionary)
    dictionary = _parse_pgpkeys(_PGPKEYS, dictionary)
    dictionary = _parse_newsgroups(_NEWSGROUPS, dictionary)
    _dict2xml(dictionary, _DATABASE)
    keys = sorted(dictionary.keys())
    print(_list_hierarchies(dictionary, "status", "LOCAL"))
    _write_pretty_logs(_PRETTYLOGS, _LOGS)
