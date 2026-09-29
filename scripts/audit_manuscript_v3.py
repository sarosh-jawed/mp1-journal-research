"""Verify the exact V3 source and render the complete pre-reviewed disposition register."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def paragraph_text(element):
    parts = []
    for child in element.iter():
        if child.tag == W + "t":
            parts.append(child.text or "")
        elif child.tag == W + "tab":
            parts.append("\t")
        elif child.tag in {W + "br", W + "cr"}:
            parts.append("\n")
    return "".join(parts)


def verify_source(source: Path, audit: dict) -> None:
    if hashlib.sha256(source.read_bytes()).hexdigest() != audit["source_sha256"]:
        raise ValueError(
            "V3 source changed; review the new version rather than reusing old locations."
        )
    with zipfile.ZipFile(source) as doc:
        body = ET.fromstring(doc.read("word/document.xml")).find(W + "body")
        paragraphs = body.findall(W + "p")
        if len(paragraphs) != audit["paragraphs"]:
            raise ValueError("V3 paragraph coverage changed.")
        for element, row in zip(paragraphs, audit["audit"][:156], strict=True):
            if (
                hashlib.sha256(paragraph_text(element).encode()).hexdigest()
                != row["source_text_sha256"]
            ):
                raise ValueError(f"Source paragraph anchor changed: {row['location']}")
        if len(body.findall(W + "tbl")) != audit["tables"]:
            raise ValueError("V3 table coverage changed.")
        ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
        rels = ET.fromstring(doc.read("word/_rels/document.xml.rels"))
        targets = {x.attrib["Id"]: "word/" + x.attrib["Target"] for x in rels}
        embeds = body.findall(".//a:blip", ns)
        if len(embeds) != audit["figures"]:
            raise ValueError("V3 figure coverage changed.")
        relationship = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
        for embed, row in zip(embeds, audit["audit"][-8:], strict=True):
            name = targets[embed.attrib[relationship]]
            if hashlib.sha256(doc.read(name)).hexdigest() != row["source_text_sha256"]:
                raise ValueError("V3 image anchor changed.")


def render(audit: dict, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    with (output / "manuscript_v3_disposition.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(audit["audit"][0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(audit["audit"])
    lines = [
        "# Manuscript V3: complete claims audit",
        "",
        audit["location_convention"],
        "",
        f"Source: {audit['source_name']}; SHA-256 `{audit['source_sha256']}`.",
        "",
        "Coverage: 156 paragraphs, all seven tables, all eight embedded figures. Original "
        "manuscript and individual-case graphics are not included in the delivery. "
        "Unchanged background references require normal bibliographic verification before "
        "submission; no new empirical or journal-selection work is implied.",
        "",
    ]
    for row in audit["audit"]:
        lines.extend(
            [
                f"## {row['location']}: {row['action']}",
                "",
                row["reason"],
                "",
                row["required_replacement"],
                "",
                f"Evidence claims: {row['claim_ids']}.",
                "",
            ]
        )
    (output / "manuscript_v3_audit.md").write_text("\n".join(lines))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path)
    p.add_argument("--output", type=Path, default=Path("outputs/publication/manuscript_audit"))
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    audit = json.loads((root / "config/manuscript_v3_audit.json").read_text())
    if args.source:
        verify_source(args.source, audit)
    render(audit, args.output)
    print(
        "Complete V3 disposition register rendered; source verified"
        if args.source
        else "Complete V3 disposition register rendered from the frozen review specification"
    )


if __name__ == "__main__":
    main()
