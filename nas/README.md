# NAS implementation of usenet-hierarchies

> Copyright (c) 2019-2020, 2023 Julien ÉLIE

See the top-level [README](../README.md) file for details about the license
and general support.


## Description

This project is a working server-side implementation of the Netnews
Administration System (NAS), an experimental system described in [RFC
4707](https://www.rfc-editor.org/rfc/rfc4707.html).

Though its source code is still not present in this repository, I have already
made available the data it serves in the [`data`](data) directory.


## NAS Database

The `data` directory contains information organized along the [header
names](https://www.rfc-editor.org/rfc/rfc4707.html#section-6.3.4) defined in
the **Netnews Administration System** protocol.  The files that are manually
maintained in this repository are currently mostly incomplete, and essentially
serve as examples.  Suggestions of additions are welcome (you can use the
[issue tracker](https://github.com/Julien-Elie/usenet-hierarchies/issues) to
submit improvements).


### `data/hierarchies`:

| Header name | Source | Description |
| :---------: | :----: | ----------- |
| Area | manual | Description of the geographical region or organization of this hierarchy |
| Article-Length | manual | Maximum length of an article in bytes in this hierarchy |
| Charset | manual | Charset that will normally be used in postings in this hierarchy |
| Charter | manual | URL that points to the charter of a hierarchy |
| Ctl-Newsgroup | manual | Name of the newsgroup that will get the postings for checkgroups, rmgroup, and newgroup control messages |
| Ctl-PGP-Key | [ftp.isc.org](https://ftp.isc.org/pub/pgpcontrol/) | PGP key (with additional information: key owner, key-id, etc.) of the sender of control messages in this hierarchy |
| Ctl-Send-Adr | [ftp.isc.org](https://ftp.isc.org/usenet/CONFIG/) | Email address of the sender of control messages |
| Date-Create | manual | Creation date of a hierarchy |
| Date-Delete | manual | Date of removal of a hierarchy |
| Description | [ftp.isc.org](https://ftp.isc.org/usenet/CONFIG/) | Short description of a hierarchy |
| Encoding | manual | Encoding for this hierarchy according to MIME |
| Hier-Type | manual | Type of hierarchy |
| Language | manual | The language that will normally be used in postings |
| Mod-Wildcard | [INN](https://raw.githubusercontent.com/InterNetNews/inn/main/samples/moderators) | Moderator wildcard for this hierarchy |
| Netiquette | manual | URL that points to the netiquette of a hierarchy |
| Newsgroup-Type | manual | Default newsgroup type in this hierarchy |
| &nbsp;&nbsp;&nbsp;&nbsp;Replacement&nbsp;&nbsp;&nbsp;&nbsp; | manual | Name of the hierarchy that replaced a removed hierarchy if status is "Obsolete" |
| Rules | manual | URL pointing to a document that describes the rules for creating, deleting, or renaming newsgroups in this hierarchy |
| Source | [ftp.isc.org](https://ftp.isc.org/usenet/CONFIG/) | URL or email address pointing to an organization or person responsible for this hierarchy |
| Status | &nbsp;&nbsp;&nbsp;&nbsp;[ftp.isc.org](https://ftp.isc.org/usenet/CONFIG/)&nbsp;&nbsp;&nbsp; | Status of a hierarchy |

Three other header names are defined in the NAS protocol but do not have
a corresponding file in the database as they are dynamically computed:
the maximum length of a newsgroup name in a hierarchy (`Name-Length`),
the maximum length of a single component in a newsgroup name in a hierarchy
(`Comp-Length`), and the timestamp for hierarchy data (`Serial`).


### `data/newsgroups`:

| Header name | Source | Description |
| :---------: | :----: | ----------- |
| Article-Length | manual | Maximum length of an article in bytes in this group |
| Charset | manual | Charset that will normally be used in postings in this group |
| Charter | auto-generated for fr.\* | URL that points to the charter of a newsgroup |
| Date-Create | [ftp.isc.org](https://ftp.isc.org/usenet/CONFIG/LOGS/) | Creation date of a newsgroup |
| Date-Delete | [ftp.isc.org](https://ftp.isc.org/usenet/CONFIG/LOGS/) | Date of removal of a newsgroup |
| Description | [ftp.isc.org](https://ftp.isc.org/usenet/CONFIG/) | Short description of a newsgroup |
| Encoding | manual | Encoding for this newsgroup according to MIME |
| FAQ | manual | URL for the FAQ of a newsgroup |
| Followup | manual | Name of the newsgroup that will take the followup postings of a moderated group |
| Language | manual | The language that will normally be used in postings |
| Mod-Adm-Adr | manual | Email address of the moderator of the newsgroup |
| Mod-Group-Info | manual | URL that points to a document where the moderator presents information about the newsgroup and the submission of articles |
| Mod-PGP-Key | manual | Public PGP key (with additional information: key owner, key-id, etc.) of this newsgroup's moderator |
| Mod-Sub-Adr | auto-generated | Email address for submissions to the newsgroup |
| Netiquette | manual | If a group has some special rules, this is the pointer to these rules |
| Newsgroup-Type | manual | Type of newsgroup |
| &nbsp;&nbsp;&nbsp;&nbsp;Replacement&nbsp;&nbsp;&nbsp;&nbsp; | manual | Name of the newsgroup or newsgroups that replaced a removed newsgroup if status is  "Removed" |
| Status | [ftp.isc.org](https://ftp.isc.org/usenet/CONFIG/) | Status of a newsgroup |

One another header name is defined in the NAS protocol but does not have
a corresponding file in the database as it is dynamically computed: the
timestamp for newsgroup data (`Serial`).