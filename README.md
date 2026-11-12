# Telematics TSI — Message & Data Explorer

A single-page browser for the messages and data elements of the Telematics TSI
(Commission Implementing Regulation (EU) 2026/253). Pick a message and explore its
full element tree, with occurrence, types, constraints, documentation and code lists.

Open `index.html` in a browser. It is one self-contained file and works offline.

## What it shows

A switch in the header selects the schema:

| View | Content |
|---|---|
| **TEL TSI · official** | 52 freight, passenger and ticket-data messages from the official XML / ASN.1 schemas |
| **RU/IM sector · XSD 3.5.2.1** | 46 messages of the RU/IM sector schema, 20 of which are not in the official schema |
| **Compare the two** | The 26 messages present in both, with elements marked as sector only, official only or changed |

Links can carry the schema and the message, for example `index.html#sector:PathRequestMessage`
or `index.html#compare:PathRequestMessage`. A link without a prefix opens the official schema.

## Sources and limits

- The sector view is **rebuilt from the schema documentation** published as Annex 6.2 of the
  RU/IM Telematics Sector Handbook 3.9 ([taf-jsg.info](https://taf-jsg.info/?page_id=280)),
  not from the original XSD file. The rebuilt schema compiles and all its references resolve,
  but the authoritative file is `taf_cat_complete_sector_3.5.2.1.xsd` as distributed by the sector.
- The comparison covers structure, occurrence, types, constraints and code-list values.
  Documentation text and code-list labels are not compared.
- This is a working tool. Only the texts published in the Official Journal of the European Union
  and the technical documents they reference are authentic.

## Build scripts

`build/` holds the scripts that produced the sector and comparison data and the version/change-log
entries. They expect the source schemas and the Annex 6.2 text extract next to them; these inputs
are not part of this repository.

| Script | Purpose |
|---|---|
| `recon.py` | Rebuilds the sector XSD from the documentation's source blocks |
| `gen.py` | Turns an XSD into the element trees the app displays |
| `diff.py` | Merges the official and sector trees for the compare view |
| `build.py` | Assembles the page, the schema switch, compare mode, version and change log |

See [CHANGELOG.md](CHANGELOG.md) for the version history; the same log opens from the version
button in the app header.
