"""Make tests/schemaorg.json, a small copy of the schema.org vocabulary.

The tests use the file to check the microdata of the generated pages. They
do not use the network, so the tests are stable.

Usage:

    python3 tests/update_schemaorg.py            # use the version below
    python3 tests/update_schemaorg.py 29.4       # use another version

The vocabulary comes from the releases folder of the schema.org repository
on GitHub (https://github.com/schemaorg/schemaorg).
"""

import json
import sys
import urllib.request
from pathlib import Path

VERSION = "29.4"
URL = ("https://raw.githubusercontent.com/schemaorg/schemaorg/v{v}-release/"
       "data/releases/{v}/schemaorg-current-https.jsonld")
OUT = Path(__file__).resolve().parent / "schemaorg.json"


def ids(value):
    """The local names of a JSON-LD reference or a list of references."""
    if value is None:
        return []
    if isinstance(value, dict):
        value = [value]
    return sorted(v["@id"].removeprefix("schema:") for v in value if v["@id"].startswith("schema:"))


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else VERSION
    with urllib.request.urlopen(URL.format(v=version)) as response:
        graph = json.load(response)["@graph"]

    types, properties, members = {}, {}, {}
    for node in graph:
        name = node["@id"].removeprefix("schema:")
        kinds = node["@type"] if isinstance(node["@type"], list) else [node["@type"]]
        if "rdfs:Class" in kinds:
            types[name] = ids(node.get("rdfs:subClassOf"))
        if "rdf:Property" in kinds:
            properties[name] = {
                "domain": ids(node.get("schema:domainIncludes")),
                "range": ids(node.get("schema:rangeIncludes")),
                "superseded": bool(node.get("schema:supersededBy")),
            }
        enumeration = [k.removeprefix("schema:") for k in kinds if k.startswith("schema:")]
        if enumeration:
            members[name] = enumeration
    # Data types are classes and instances of schema:DataType.
    for node in graph:
        kinds = node["@type"] if isinstance(node["@type"], list) else [node["@type"]]
        if "schema:DataType" in kinds:
            types.setdefault(node["@id"].removeprefix("schema:"), [])

    data = {"version": version, "source": URL.format(v=version),
            "types": dict(sorted(types.items())),
            "properties": dict(sorted(properties.items())),
            "members": dict(sorted(members.items()))}
    OUT.write_text(json.dumps(data, indent=0, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} (schema.org {version}): {len(types)} types, {len(properties)} properties")


if __name__ == "__main__":
    main()
