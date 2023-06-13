#!/usr/bin/python2
# -*- encoding: utf-8 -*-
#
# Local script used by nas.trigofacile.com to generate the NAS database
# containing information about hierarchies and newsgroups.  This script gathers
# elements from multiple ftp.isc.org files (control.ctl, PGPKEYS, newsgroups,
# logs) and generates the corresponding files for the NAS database that can be
# automatically generated (see below the list of created files).
#
# The NAS (Netnews Administration System) protocol is defined in experimental
# RFC 4707.
#
# This script fits the needs of my local setup and may not expect your own
# needs.  I just share it in case it could give ideas as for the generation of
# a NAS database generation.
#
# Original version written in August 2019, and maintained since then by
# Julien ÉLIE.
#
# Github repository to view the latest source code and report possible issues:
#   https://github.com/Julien-Elie/usenet-hierarchies/
#
# SPDX-License-Identifier: MIT

import codecs
import os
import urllib2

# Local paths to data directories.
DATAHIERPATH = "/home/news/nas/data/hierarchies"
DATANEWSGROUPSPATH = "/home/news/nas/data/newsgroups"

# Local paths for files to create or update.
NAS_HIER_CTLPGPKEY = os.path.join(DATAHIERPATH, "Ctl-PGP-Key")
NAS_HIER_CTLSENDADR = os.path.join(DATAHIERPATH, "Ctl-Send-Adr")
NAS_HIER_DESCRIPTION = os.path.join(DATAHIERPATH, "Description")
NAS_HIER_SOURCE = os.path.join(DATAHIERPATH, "Source")
NAS_HIER_STATUS = os.path.join(DATAHIERPATH, "Status")

NAS_NEWSGROUPS_CHARTER = os.path.join(DATANEWSGROUPSPATH, "Charter")
NAS_NEWSGROUPS_DATECREATE = os.path.join(DATANEWSGROUPSPATH, "Date-Create")
NAS_NEWSGROUPS_DATEDELETE = os.path.join(DATANEWSGROUPSPATH, "Date-Delete")
NAS_NEWSGROUPS_DESCRIPTION = os.path.join(DATANEWSGROUPSPATH, "Description")
NAS_NEWSGROUPS_MODSUBADR = os.path.join(DATANEWSGROUPSPATH, "Mod-Sub-Adr")
NAS_NEWSGROUPS_STATUS = os.path.join(DATANEWSGROUPSPATH, "Status")

# Local path to external data (usually downloaded from ftp.isc.org for
# control.ctl and PGPKEYS, or reformatted from ftp.isc.org and made available
# at https://github.com/Julien-Elie/usenet-hierarchies/tree/main/website/data
# for changelog and UTF-8 descriptions.
DATAISCPATH = "/home/news/nas/data/isc"

# Local paths for files to read.
ISC_CONTROL_FILE = os.path.join(DATAISCPATH, "control.ctl")
ISC_LOGS_FILE = os.path.join(DATAISCPATH, "changelog")
ISC_NEWSGROUPS_FILE = os.path.join(DATAISCPATH, "newsgroups.utf8")
ISC_PGPKEYS_FILE = os.path.join(DATAISCPATH, "PGPKEYS")

# Try to generate URL for fr.* charters.
GENCHARTERS = False

# Create directories for the NAS database, if needed.
if not os.path.isdir(DATAHIERPATH):
    os.makedirs(DATAHIERPATH)
if not os.path.isdir(DATANEWSGROUPSPATH):
    os.makedirs(DATANEWSGROUPSPATH)

# Grab information for newsgroups in the following dictionaries.
datecreate_dict = {}
datedelete_dict = {}
description_dict = {}
status_dict = {}

# First, take into account current information about the newsgroups: moderation
# status and description.
for line in codecs.open(ISC_NEWSGROUPS_FILE, "r", "utf-8"):
    line = line.rstrip()
    (h, description) = line.split(None, 1)
    description = description.lstrip()
    # Do not keep the description if none is provided.
    if description in ["No description.", "No description", "?"]:
        status_dict[h] = "Unmoderated"
    elif description in [
        "No description. (Moderated)",
        "No description (Moderated)",
    ]:
        status_dict[h] = "Moderated"
    elif description.endswith(" (Moderated)"):
        description_dict[h] = description
        status_dict[h] = "Moderated"
    elif h in ["control", "junk"] or h.startswith("control."):
        description_dict[h] = description
        status_dict[h] = "Readonly"
    else:
        description_dict[h] = description
        status_dict[h] = "Unmoderated"


# Keep trace of old descriptions from removed newsgroups, if present in an
# already existing file.
for line in codecs.open(NAS_NEWSGROUPS_DESCRIPTION, "r", "utf-8"):
    line = line.rstrip()
    (h, description) = line.split(None, 1)
    if h not in status_dict:
        status_dict[h] = "Removed"
        description = description.lstrip()
        if description not in [
            "No description.",
            "No description",
            "?",
            "No description. (Moderated)",
            "No description (Moderated)",
        ]:
            description_dict[h] = description


# Then, take into account previous changes from logs of control articles.
# This file is read from the most recent change to the oldest.
for line in codecs.open(ISC_LOGS_FILE, "r", "iso-8859-1"):
    elements = line.split()
    if len(elements) < 4:
        print("Malformed line: %s" % line)
        continue
    # Do not treat reserved newsgroups.
    if (
        elements[3] in ["to"]
        or elements[3].startswith("control.")
        or elements[3].startswith("private.")
    ):
        continue
    # Update status dictionary (for removals only), and dates.
    # Ensure that the newsgroup is not marked as Removed if it has been
    # recreated.
    if elements[2] == "rmgroup" and (
        not elements[3] in status_dict
        or (
            status_dict[elements[3]] == "Removed"
            and not elements[3] in datedelete_dict
        )
    ):
        status_dict[elements[3]] = "Removed"
        # Only if the removals were not manual, or manual after 2012 (before
        # that, the dates are not always close to the real removal time), and
        # not in 2003 when the logs began and several updates were made.
        if len(elements) == 4 or (
            len(elements) > 4
            and (elements[4] != "(manual)" or int(elements[0][:4]) > 2012)
            and int(elements[0][:4]) != 2003
        ):
            datedelete_dict[elements[3]] = elements[0].replace("-", "")
            datedelete_dict[elements[3]] += elements[1].replace(":", "")
    elif elements[2] == "newgroup" and not elements[3] in datecreate_dict:
        if len(elements) < 5:
            print("Missing status: %s" % line)
            continue
        # Similar rules for the creations, with additional newsgroups to take
        # into account.
        if len(elements) == 5 or (
            len(elements) > 5
            and (
                elements[5] != "(manual)"
                or int(elements[0][:4]) > 2012
                or elements[3].startswith("grisbi.")
            )
            and int(elements[0][:4]) != 2003
        ):
            datecreate_dict[elements[3]] = elements[0].replace("-", "")
            datecreate_dict[elements[3]] += elements[1].replace(":", "")
    elif elements[2] in ["newgroup", "rmgroup", "changedesc", "changegroup"]:
        continue
    else:
        print("Unknown action: %s" % line)
        continue


# Local additions, to show how to eventually add some.
# At one point, like what is done for the descriptions, already existing data
# in files should just be kept.  Local additions hard-coded in this script will
# then no longer be necessary.
datecreate_dict["fr.bienvenue.questions"] = "19971016173454"


# Write in files all these information.
f_ngp_datecreate = codecs.open(NAS_NEWSGROUPS_DATECREATE, "w", "utf-8")
f_ngp_datedelete = codecs.open(NAS_NEWSGROUPS_DATEDELETE, "w", "utf-8")
f_ngp_description = codecs.open(NAS_NEWSGROUPS_DESCRIPTION, "w", "utf-8")
f_ngp_status = codecs.open(NAS_NEWSGROUPS_STATUS, "w", "utf-8")

for ngp in sorted(datecreate_dict.keys()):
    f_ngp_datecreate.write(ngp + "\t" + datecreate_dict[ngp] + "\n")
for ngp in sorted(datedelete_dict.keys()):
    f_ngp_datedelete.write(ngp + "\t" + datedelete_dict[ngp] + "\n")
for ngp in sorted(description_dict.keys()):
    f_ngp_description.write(ngp + "\t" + description_dict[ngp] + "\n")
for ngp in sorted(status_dict.keys()):
    f_ngp_status.write(ngp + "\t" + status_dict[ngp] + "\n")

f_ngp_datecreate.close()
f_ngp_datedelete.close()
f_ngp_description.close()
f_ngp_status.close()


# Grab information in control.ctl for hierarchies.
hierarchies_dict = {}
beginning = False
done = False
for line in codecs.open(ISC_CONTROL_FILE, "r", "utf-8"):
    line = line.strip()
    if beginning:
        # A new hierarchy begins.
        # '## COMP, HUMANITIES, MISC, NEWS, REC, SCI, SOC, TALK (The Big 8)'
        if line.startswith("## "):
            done = False
            elements = line.split("(")
            names = elements[0].lower()
            names = names.replace("#", "")
            names = names.replace(" ", "")
            names = names.replace("&", ",")
            # Sometimes, several hierarchies are in the same control.ctl entry.
            names = names.split(",")
            for hierName in names:
                hierarchies_dict[hierName] = {}
            if len(elements) > 1:
                elements2 = elements[1][:-1].split(" -- ")
                if len(elements2) == 1:
                    for hierName in names:
                        hierarchies_dict[hierName]["Status"] = "Complete"
                        if elements2[0] not in ["?"]:
                            hierarchies_dict[hierName]["Description"] = (
                                elements2[0]
                            )
                else:
                    for hierName in names:
                        status = elements2[0].replace("*", "")
                        if status in ["LOCAL", "PRIVATE"]:
                            hierarchies_dict[hierName]["Status"] = "Incomplete"
                        elif status in ["DEFUNCT", "HISTORIC"]:
                            hierarchies_dict[hierName]["Status"] = "Obsolete"
                        elif status in ["RESERVED"]:
                            hierarchies_dict[hierName]["Status"] = "Complete"
                        if elements2[1] not in ["?"]:
                            hierarchies_dict[hierName]["Description"] = (
                                elements2[1]
                            )
            # alt.* is an unmanaged hierarchy (the proponent sends newgroup
            # control articles himself, and there's no hierarchy manager who
            # sends checkgroups).
            elif names[0] == "alt":
                hierarchies_dict["alt"]["Status"] = "Incomplete"
                # Add a description (currently missing from control.ctl).
                hierarchies_dict["alt"][
                    "Description"
                ] = "Unmanaged alternative hierarchy"
            else:
                print("No description for %s" % elements[0])
        elif line.startswith("# Contact:"):
            contact = line.replace("# Contact: ", "")
            for hierName in names:
                if "Source" not in hierarchies_dict[hierName]:
                    hierarchies_dict[hierName]["Source"] = [contact]
                elif contact not in hierarchies_dict[hierName]["Source"]:
                    hierarchies_dict[hierName]["Source"].append(contact)
        elif line.startswith("# URL:"):
            url = line.replace("# URL: ", "")
            for hierName in names:
                if "Source" not in hierarchies_dict[hierName]:
                    hierarchies_dict[hierName]["Source"] = [url]
                elif url not in hierarchies_dict[hierName]["Source"]:
                    hierarchies_dict[hierName]["Source"].append(url)
        elif line.startswith("# Key URL:"):
            for hierName in names:
                hierarchies_dict[hierName]["Ctl-PGP-Key_L"] = line.replace(
                    "# Key URL: ", ""
                )
        elif line.startswith("# Key fingerprint:"):
            for hierName in names:
                hierarchies_dict[hierName]["Ctl-PGP-Key_F"] = line.replace(
                    "# Key fingerprint: ", ""
                )
        # Useless information for NAS.
        elif line.startswith("#"):
            continue
        elif not done:
            if (
                line.startswith("checkgroups:")
                or line.startswith("newgroup:")
                or line.startswith("rmgroup:")
            ):
                elements = line.split(":")
                if elements[1] != "*":
                    for hierName in names:
                        if "Ctl-Send-Adr" not in hierarchies_dict[hierName]:
                            hierarchies_dict[hierName]["Ctl-Send-Adr"] = [
                                elements[1]
                            ]
                        elif (
                            elements[1]
                            not in hierarchies_dict[hierName]["Ctl-Send-Adr"]
                        ):
                            hierarchies_dict[hierName]["Ctl-Send-Adr"].append(
                                elements[1]
                            )
            elif not line:
                done = True
    # Only begin parsing with the first hierarchy.
    elif line.startswith("## Special reserved groups"):
        beginning = True


# Then grab additional information in PGPKEYS for hierarchies.
beginning = False
pgp = False
keydesc = False
nameFound = False
for line in codecs.open(ISC_PGPKEYS_FILE, "r", "ISO-8859-1"):
    line = line.strip()
    if beginning:
        # A new hierarchy follows.
        if line.endswith("___________"):
            nameFound = False
            continue
        elif line and not nameFound:
            names = line.lower()
            names = names.replace(" ", "")
            names = names.replace("&", ",")
            # Sometimes, several hierarchies are in the same PGPKEYS entry.
            names = names.split(",")
            for hierName in names:
                if not hierName in hierarchies_dict:
                    print("%s in PGPKEYS but not in control.ctl" % hierName)
                    hierarchies_dict[hierName] = {}
            nameFound = True
        elif line.startswith("Key User ID:"):
            for hierName in names:
                hierarchies_dict[hierName]["Ctl-PGP-Key_U"] = [
                    line.replace("Key User ID: ", "")
                ]
        elif line.startswith("pub  ") or line.startswith(u"öff  "):
            keydesc = True
            elements = line.split(None, 3)
            (bits, keyid) = elements[1].split("/")
            for hierName in names:
                hierarchies_dict[hierName]["Ctl-PGP-Key_B"] = bits.rstrip(
                    "R"
                ).rstrip("D")
                hierarchies_dict[hierName]["Ctl-PGP-Key_I"] = keyid
                if (
                    len(elements) > 3
                    and elements[3]
                    not in hierarchies_dict[hierName]["Ctl-PGP-Key_U"]
                ):
                    hierarchies_dict[hierName]["Ctl-PGP-Key_U"].append(
                        elements[3]
                    )
        elif keydesc:
            if line:
                # There are lots of different other patterns to support
                # (see for instance ee, europa, fr, hr, isu, nippon...).
                if line.startswith("uid"):
                    elements = line.split(None, 1)
                    for hierName in names:
                        if (
                            elements[1]
                            not in hierarchies_dict[hierName]["Ctl-PGP-Key_U"]
                        ):
                            hierarchies_dict[hierName]["Ctl-PGP-Key_U"].append(
                                elements[1]
                            )
            else:
                keydesc = False
        elif line == "-----BEGIN PGP PUBLIC KEY BLOCK-----":
            pgp = True
            for hierName in names:
                hierarchies_dict[hierName]["Ctl-PGP-Key_K"] = ["-" + line]
        elif line == "-----END PGP PUBLIC KEY BLOCK-----":
            pgp = False
            for hierName in names:
                hierarchies_dict[hierName]["Ctl-PGP-Key_K"].append(" " + line)
        elif pgp:
            for hierName in names:
                hierarchies_dict[hierName]["Ctl-PGP-Key_K"].append("-" + line)
            if line.startswith("Version: "):
                hierarchies_dict[hierName]["Ctl-PGP-Key_V"] = line.replace(
                    "Version: ", ""
                )
    elif line.endswith("___________"):
        beginning = True


# Write in files all these information.
f_hier_ctlpgpkey = codecs.open(NAS_HIER_CTLPGPKEY, "w", "utf-8")
f_hier_ctlsendadr = codecs.open(NAS_HIER_CTLSENDADR, "w", "utf-8")
f_hier_description = codecs.open(NAS_HIER_DESCRIPTION, "w", "utf-8")
f_hier_source = codecs.open(NAS_HIER_SOURCE, "w", "utf-8")
f_hier_status = codecs.open(NAS_HIER_STATUS, "w", "utf-8")


for hierName in sorted(hierarchies_dict.keys()):
    if hierName in [
        "control",
        "example",
        "general",
        "junk",
        "local",
        "private",
        "test",
        "to",
    ]:
        continue
    if "Ctl-PGP-Key_U" in hierarchies_dict[hierName]:
        for value in hierarchies_dict[hierName]["Ctl-PGP-Key_U"]:
            f_hier_ctlpgpkey.write(hierName + "\tU " + value + "\n")
    if "Ctl-PGP-Key_B" in hierarchies_dict[hierName]:
        f_hier_ctlpgpkey.write(
            hierName
            + "\tB "
            + hierarchies_dict[hierName]["Ctl-PGP-Key_B"]
            + "\n"
        )
    if "Ctl-PGP-Key_I" in hierarchies_dict[hierName]:
        f_hier_ctlpgpkey.write(
            hierName
            + "\tI "
            + hierarchies_dict[hierName]["Ctl-PGP-Key_I"]
            + "\n"
        )
    if "Ctl-PGP-Key_L" in hierarchies_dict[hierName]:
        f_hier_ctlpgpkey.write(
            hierName
            + "\tL "
            + hierarchies_dict[hierName]["Ctl-PGP-Key_L"]
            + "\n"
        )
    if "Ctl-PGP-Key_F" in hierarchies_dict[hierName]:
        f_hier_ctlpgpkey.write(
            hierName
            + "\tF "
            + hierarchies_dict[hierName]["Ctl-PGP-Key_F"]
            + "\n"
        )
    if "Ctl-PGP-Key_V" in hierarchies_dict[hierName]:
        f_hier_ctlpgpkey.write(
            hierName
            + "\tV "
            + hierarchies_dict[hierName]["Ctl-PGP-Key_V"]
            + "\n"
        )
    if "Ctl-PGP-Key_K" in hierarchies_dict[hierName]:
        for value in hierarchies_dict[hierName]["Ctl-PGP-Key_K"]:
            # K is followed by either a space or a dash (already in value).
            f_hier_ctlpgpkey.write(hierName + "\tK" + value + "\n")
    if "Ctl-Send-Adr" in hierarchies_dict[hierName]:
        for value in hierarchies_dict[hierName]["Ctl-Send-Adr"]:
            f_hier_ctlsendadr.write(hierName + "\t" + value + "\n")
    if "Description" in hierarchies_dict[hierName]:
        f_hier_description.write(
            hierName + "\t" + hierarchies_dict[hierName]["Description"] + "\n"
        )
    if "Source" in hierarchies_dict[hierName]:
        for value in hierarchies_dict[hierName]["Source"]:
            if value not in hierarchies_dict[hierName].get("Ctl-Send-Adr", []):
                f_hier_source.write(hierName + "\t" + value + "\n")
    if "Status" in hierarchies_dict[hierName]:
        f_hier_status.write(
            hierName + "\t" + hierarchies_dict[hierName]["Status"] + "\n"
        )

f_hier_ctlpgpkey.close()
f_hier_ctlsendadr.close()
f_hier_description.close()
f_hier_source.close()
f_hier_status.close()


# Try automatical generation of charters and submission addresses
# when possible.
if GENCHARTERS:
    f_ngp_charter = codecs.open(NAS_NEWSGROUPS_CHARTER, "w", "utf-8")
f_ngp_modsubadr = codecs.open(NAS_NEWSGROUPS_MODSUBADR, "w", "utf-8")

for ngp in sorted(status_dict.keys()):
    # Charters for still active newsgroups in the fr.* hierarchy.
    if (
        GENCHARTERS
        and ngp.startswith("fr.")
        and status_dict[ngp]
        in [
            "Moderated",
            "Unmoderated",
        ]
    ):
        url = "http://www.usenet-fr.net/fur/chartes/"
        url += ngp[3:].replace("+", "p")
        url += ".html"

        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError as exception:
            response = exception
        if response.code == 200:
            f_ngp_charter.write(ngp + "\t" + url + "\n")

    # Submission addresses for moderated newsgroups.
    if status_dict[ngp] == "Moderated":
        email = ngp.replace(".", "-")
        f_ngp_modsubadr.write(ngp + "\t")

        if ngp.startswith("aioe."):
            f_ngp_modsubadr.write(email + "-newsgroup@aioe.org\n")
        elif ngp.startswith("fido7."):
            f_ngp_modsubadr.write(email + "@fido7.org\n")
        elif ngp.startswith("ffm."):
            f_ngp_modsubadr.write(email + "@moderators.arcornews.de\n")
        elif ngp.startswith("fj."):
            f_ngp_modsubadr.write(email + "@moderators.fj-news.org\n")
        elif ngp.startswith("medlux."):
            f_ngp_modsubadr.write(email + "@news.medlux.ru\n")
        elif ngp.startswith("nl."):
            f_ngp_modsubadr.write(email + "@nl.news-admin.org\n")
        elif ngp.startswith("perl."):
            f_ngp_modsubadr.write("news-moderator-" + email + "@perl.org\n")
        elif ngp.startswith("relcom."):
            f_ngp_modsubadr.write(email + "@moderators.relcom.ru\n")
        elif ngp.startswith("si."):
            f_ngp_modsubadr.write(email + "@arnes.si\n")
        elif ngp.startswith("ukr."):
            f_ngp_modsubadr.write(email + "@sita.kiev.ua\n")
        else:
            f_ngp_modsubadr.write(email + "@moderators.isc.org\n")

if GENCHARTERS:
    f_ngp_charter.close()
f_ngp_modsubadr.close()
