"""Publication renderings and aggregate-only checks of the accepted A-D record.

No scientific fitting, raw-data access, manuscript inference or acceptance decision occurs here.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import os
from pathlib import Path

# Colab's inherited inline backend is unavailable in the locked standalone runtime.
os.environ["MPLBACKEND"] = "Agg"
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from mp1.d_validation import require_close, verify_d_evidence

BASELINE = "56b335c705ef15d5a261865382dd79991d2a93a2"
P = "outputs/provenance/"
B = "outputs/psychometrics/"
K = "outputs/clustering/"
C = "outputs/modeling/work_package_c/"
D = "outputs/outcome_validation/work_package_d/"
X = "outputs/external_validation/work_package_d/"
DISPLAY_HEADERS = {
    "dataset": "Dataset",
    "sample": "Sample",
    "section": "Source section",
    "n": "n",
    "cluster": "Profile",
    "records": "Records",
    "unique_records": "Distinct full patterns",
    "largest_group_size": "Largest pattern n",
    "largest_exact_record_share": "Largest pattern share",
    "silhouette": "Silhouette",
    "ari_mean": "Mean omitted ARI",
    "alpha_raw": "Raw alpha",
    "omega_ordinal_latent_response": "Ordinal omega",
    "minimum_corrected_item_total": "Min. item-total",
    "minimum_ordinal_loading": "Min. loading",
    "one_factor_maximum_residual": "Max. residual",
    "passes_screen": "All criteria pass?",
    "variant": "Sample / target",
    "class_id": "Profile",
    "training_records": "Training n",
    "validation_records": "Held-out n",
    "validation_records_with_pattern_in_training": "Held-out: seen pattern",
    "validation_records_without_pattern_in_training": "Held-out: unseen pattern",
    "validation_overlap_fraction": "Overlap fraction",
    "profile": "Profile",
    "profile_n": "Profile n",
    "kruskal_h_tie_corrected": "H (df=1)",
    "nominal_p_value": "Nominal p",
    "rank_epsilon_squared_H_over_N_minus_1": "H / (N - 1)",
    "cliff_delta_P2_minus_P1": "Cliff delta (P2 - P1)",
    "assumed_independent_units": "Assumed independent unit",
    "resampling_units": "Unit count",
    "conditional_percentile_lower": "Conditional 95% lower",
    "conditional_percentile_upper": "Conditional 95% upper",
    "model": "Configural model",
    "chisq.scaled": "Scaled chi-square",
    "df.scaled": "df",
    "cfi.scaled": "Scaled CFI",
    "rmsea.scaled": "Scaled RMSEA",
    "srmr": "SRMR",
    "cfi.robust": "Robust CFI",
    "rmsea.robust": "Robust RMSEA",
    "passes_followup_screen": "Follow-up allowed?",
    "country": "Country",
    "item_x": "Item X",
    "item_y": "Item Y",
    "spearman_rho": "Spearman rho",
    "permutation_p_value": "Permutation p",
    "holm_p_four_test_family": "Holm p (four tests)",
    "conditional_95_lower": "Conditional 95% lower",
    "conditional_95_upper": "Conditional 95% upper",
}
BLUE, ORANGE = "#176681", "#B45426"
VARIANTS = {
    "full": "Full records",
    "quality_fixed_profiles": "Quality sensitivity: fixed",
    "quality_refit_profiles": "Quality sensitivity: refit",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def safe_path(root: Path, relative: str) -> Path:
    path = root / relative
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Unsafe publication path: {relative}")
    return path


def freeze(root: Path) -> dict:
    value = read_json(root / "config/publication_freeze.json")
    if value["baseline_commit"] != BASELINE:
        raise ValueError("Accepted baseline changed.")
    for name, digest in value["frozen_files"].items():
        if sha(safe_path(root, name)) != digest:
            raise ValueError(f"Frozen accepted file changed: {name}")
    return value


def resolve(root: Path, source: dict, accepted: dict):
    name = source["file"]
    if name not in accepted:
        raise ValueError(f"Evidence is not an accepted output: {name}")
    path = safe_path(root, name)
    if sha(path) != accepted[name]:
        raise ValueError(f"Evidence hash changed: {name}")
    if path.suffix == ".json":
        value = read_json(path)
        for part in source.get("pointer", "").split("/")[1:]:
            part = part.replace("~1", "/").replace("~0", "~")
            value = value[int(part)] if isinstance(value, list) else value[part]
        return value
    if path.suffix != ".csv":
        raise ValueError("Scientific references must select a CSV or JSON output.")
    rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
    selected = [
        dict(csv_data_row=i, **row)
        for i, row in enumerate(rows, 1)
        if all(row[key] == str(value) for key, value in source.get("where", {}).items())
    ]
    if source.get("where") and not selected:
        raise ValueError(f"Evidence selector is empty: {source}")
    if fields := source.get("fields"):
        selected = [{k: row[k] for k in ["csv_data_row", *fields]} for row in selected]
    return selected


def aggregate_checks(root: Path) -> dict:
    """Reconcile aggregate identities without re-estimating scientific models."""
    locked = freeze(root)
    checks = []
    for name in locked["accepted_outputs"]:
        path = root / name
        if path.suffix == ".json":
            manifest = read_json(path)
            for key in ["artifact_sha256", "evidence_table_sha256"]:
                for file, digest in manifest.get(key, {}).items():
                    if sha(path.parent / file) != digest:
                        raise ValueError(f"Accepted manifest mismatch: {file}")
        elif path.suffix == ".csv":
            frame = pd.read_csv(path)
            forbidden = {"RespondentID", "source_record_number", "row_id", "prediction"}
            if forbidden.intersection(frame.columns):
                raise ValueError(f"Private record identifier in output: {name}")
            if np.isinf(frame.select_dtypes(include="number").to_numpy()).any():
                raise ValueError(f"Infinite numerical output: {name}")
    checks.append("All accepted output bytes, manifest links, CSV schemas and finite values")
    read = lambda name: pd.read_csv(root / name)  # noqa: E731
    distributions = read(B + "item_distributions.csv")
    counts = distributions[[f"count_{i}" for i in range(1, 6)]]
    require_close(counts.sum(axis=1), distributions.n, "B item denominators")
    sizes = read(K + "cluster_sizes.csv")
    metrics = read(K + "cluster_metrics.csv")
    for key, frame in sizes.groupby(["dataset", "sample", "k"]):
        match = metrics.set_index(["dataset", "sample", "k"]).loc[key]
        require_close(frame["count"].sum(), match.n, "cluster totals")
        require_close(frame.fraction, frame["count"] / match.n, "cluster fractions")
    centroids = read(K + "cluster_centroids.csv")
    probs = centroids[[f"probability_above_{i}" for i in range(1, 5)]].to_numpy()
    if (probs < -1e-12).any() or (probs > 1 + 1e-12).any() or (np.diff(probs) > 1e-12).any():
        raise ValueError("Ordinal centroid probability ordering is invalid.")
    require_close(centroids.agreement_proportion, probs[:, 2], "agreement threshold")
    merged = centroids.merge(
        sizes, on=["dataset", "sample", "k", "cluster"], validate="many_to_one"
    )
    for (dataset, sample, k, item), frame in merged.groupby(["dataset", "sample", "k", "item"]):
        source = distributions.set_index(["dataset", "sample", "item"]).loc[(dataset, sample, item)]
        for threshold in range(1, 5):
            pooled = np.average(frame[f"probability_above_{threshold}"], weights=frame["count"])
            expected = sum(source[f"count_{i}"] for i in range(threshold + 1, 6)) / source.n
            require_close(pooled, expected, f"Pooled centroid {dataset}/{sample}/{k}/{item}")
    concentration = read(K + "cluster_record_concentration.csv")
    require_close(
        concentration.records - concentration.unique_records,
        concentration.duplicate_excess_rows,
        "repeated-record accounting",
    )
    require_close(
        concentration.largest_group_size / concentration.records,
        concentration.largest_exact_record_share,
        "concentration shares",
    )
    checks.append(
        "Every B item denominator, every k size, all 5440 centroid probabilities and concentration"
    )
    reliability = read(B + "reliability.csv")
    if reliability.passes_screen.any():
        raise ValueError("Frozen no-section-passes decision changed.")
    for dataset, frame in read(B + "parallel_analysis.csv").groupby(["dataset", "sample"]):
        expected = 5 if dataset[0] == "D5" else 2
        if int(frame.retained.sum()) != expected:
            raise ValueError("Parallel-analysis decision changed.")
    checks.append("Reliability screens and retained exploratory factor counts")
    overlap = read(C + "evaluation_overlap.csv")
    require_close(
        overlap.validation_records_with_pattern_in_training
        + overlap.validation_records_without_pattern_in_training,
        overlap.validation_records,
        "C overlap accounting",
    )
    require_close(
        overlap.validation_records_with_pattern_in_training / overlap.validation_records,
        overlap.validation_overlap_fraction,
        "C overlap fractions",
    )
    for row in read(C + "group_allocation_feasibility.csv").itertuples():
        obstruction = row.largest_exact_record_group > max(
            row.requested_training_class_records, row.requested_test_class_records
        )
        if bool(row.proven_incompatible_with_intact_groups) != obstruction:
            raise ValueError("Intact-pattern necessary allocation condition changed.")
    c = read_json(root / (C + "predictive_audit_summary.json"))
    if c["gate"]["modeling_performed"] or c["gate"]["explainability_performed"]:
        raise ValueError("C feasibility boundary changed.")
    checks.append("All C overlap/allocation rows and no-model gate")
    d = verify_d_evidence(root / "config/analysis.yaml", root / "config/work_package_d.yaml")
    checks.append(
        "D count-based independent rank/effect reconciliation, Holm family and hash chains"
    )
    if not read(X + "ordinal_equality_comparisons.csv").empty:
        raise ValueError("Unaccepted equality comparisons present.")
    if read(X + "item_compatibility.csv").exact_common_anchor.any():
        raise ValueError("Accepted no-anchor decision changed.")
    for claim in read_json(root / "config/publication_claims.json"):
        for source in claim["sources"]:
            resolve(root, source, locked["accepted_outputs"])
    checks.append("Every retained-claim selector resolves exclusively to accepted baseline outputs")
    return {
        "baseline_commit": BASELINE,
        "frozen_files": len(locked["frozen_files"]),
        "accepted_outputs": len(locked["accepted_outputs"]),
        "checks": checks,
        "D_checks": d,
        "new_scientific_fits": 0,
        "private_inputs_required": False,
        "status": "PASS",
    }


def evidence_map(root: Path, destination: Path) -> None:
    locked = freeze(root)
    claims = read_json(root / "config/publication_claims.json")
    inventory = []
    register = []
    for name, digest in locked["accepted_outputs"].items():
        path = root / name
        related = [c for c in claims if any(s["file"] == name for s in c["sources"])]
        row_count = None
        if path.suffix == ".csv":
            rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
            row_count = len(rows)
            if not related:
                raise ValueError(f"Accepted CSV omitted from evidence map: {name}")
            for i, row in enumerate(rows, 1):
                register.append(
                    {
                        "file": name,
                        "sha256": digest,
                        "csv_data_row": i,
                        "claim_ids": ";".join(c["id"] for c in related),
                        "exact_evidence_json": json.dumps(row, sort_keys=True),
                        "role": "Accepted evidence; interpretation constrained by listed claims",
                    }
                )
        inventory.append(
            {
                "file": name,
                "sha256": digest,
                "bytes": path.stat().st_size,
                "data_rows": row_count,
                "claim_ids": ";".join(c["id"] for c in related),
                "retention": "frozen accepted evidence; historical status text preserved",
            }
        )
    pd.DataFrame(inventory).to_csv(destination / "accepted_output_inventory.csv", index=False)
    pd.DataFrame(register).to_csv(destination / "complete_evidence_register.csv", index=False)
    master, mapped, markdown = (
        [],
        [],
        [
            "# Manuscript evidence map",
            "",
            "Authority: canonical MP1 Research Control after D acceptance. "
            "A/B/D accepted; C frozen "
            "as the accepted predictive-feasibility blocker. E does not "
            "grant acceptance to itself.",
            "",
            "All scientific references below are baseline outputs, not E-generated findings. "
            "CSV row numbers are one-based data rows (header excluded). Exact strings, including "
            "full numeric precision, are preserved in complete_evidence_register.csv.",
            "",
            "Recovered source replay contains 247 differences confined to nonselected B "
            "k=3-6 diagnostic candidates. Accepted bytes are preserved. Selected k=2 results "
            "and all candidate ranks/screens/choices agree; complete candidate-grid numerical "
            "identity is not claimed. See docs/publication_discrepancy_register.md.",
            "",
        ],
    )
    for c in claims:
        refs = [
            {
                **s,
                "sha256": locked["accepted_outputs"][s["file"]],
                "exact_evidence": resolve(root, s, locked["accepted_outputs"]),
            }
            for s in c["sources"]
        ]
        row = {k: v for k, v in c.items() if k != "sources"}
        master.append({**row, "authoritative_files": ";".join(s["file"] for s in c["sources"])})
        mapped.append({**row, "evidence": refs})
        markdown += [
            f"## {c['id']}: {c['retained_finding']}",
            "",
            f"Research question: {c['research_question']}",
            "",
            f"Key evidence (display precision): {c['key_evidence_display']}",
            "",
            f"Permitted interpretation: {c['permitted_interpretation']}",
            "",
            f"Prohibited overclaim: {c['prohibited_overclaim']}",
            "",
            f"Manuscript placement: {c['manuscript_section']}. Role: {c['role']}.",
            "",
            "Authoritative selectors:",
            "",
            *[
                f"- `{s['file']}`: "
                + (
                    f"JSON pointer `{s.get('pointer', '') or '/'}`"
                    if s["file"].endswith(".json")
                    else f"CSV selector `{json.dumps(s.get('where', {}))}`; {{}} means all rows"
                )
                for s in c["sources"]
            ],
            "",
        ]
    pd.DataFrame(master).to_csv(destination / "retained_results_master.csv", index=False)
    dump(destination / "manuscript_evidence_map.json", mapped)
    (destination / "manuscript_evidence_map.md").write_text("\n".join(markdown), encoding="utf-8")


def table_specifications(root: Path) -> list[dict]:
    def read(name):
        return pd.read_csv(root / name)

    def spec(id_, title, frame, note, claims):
        return {"id": id_, "title": title, "data": frame, "note": note, "claims": claims}

    source = read_json(root / (P + "source_reconciliation.json"))["file_comparisons"]
    samples = read_json(root / (B + "measurement_summary.json"))["samples"]
    sample_table = pd.DataFrame(
        [
            {
                "Dataset": s["dataset"],
                "Full records": s["active_rows"],
                "Quality sensitivity": samples[s["dataset"]]["sensitivity"],
                "Repeated groups": s["active_repeated_groups"],
                "Repeated members": s["repeated_group_member_records"],
                "Excess repetitions": s["active_excess_repeated_records"],
                "Largest group": s["largest_repeated_group"],
            }
            for s in source
        ]
    )
    reliability = read(B + "reliability.csv")[
        [
            "section",
            "sample",
            "n",
            "alpha_raw",
            "omega_ordinal_latent_response",
            "minimum_corrected_item_total",
            "minimum_ordinal_loading",
            "one_factor_maximum_residual",
            "passes_screen",
        ]
    ]
    profiles = read(K + "cluster_record_concentration.csv").merge(
        read(K + "cluster_metrics.csv"), on=["dataset", "sample", "k"], validate="many_to_one"
    )
    profiles = profiles[
        [
            "dataset",
            "sample",
            "cluster",
            "records",
            "unique_records",
            "largest_group_size",
            "largest_exact_record_share",
            "silhouette",
            "ari_mean",
        ]
    ]
    overlap = read(C + "evaluation_overlap.csv")
    overlap = overlap[overlap.stage.eq("held_out_design")][
        [
            "variant",
            "class_id",
            "training_records",
            "validation_records",
            "validation_records_with_pattern_in_training",
            "validation_records_without_pattern_in_training",
            "validation_overlap_fraction",
        ]
    ]
    bands = read(D + "cgpa_distributions.csv")
    bands = bands.assign(
        display=bands.apply(lambda r: f"{r.records} ({100 * r.fraction:.2f}%)", axis=1)
    )
    bands = bands.pivot(
        index=["variant", "profile", "profile_n"], columns="cgpa_band", values="display"
    )
    bands = bands[["Below 2.50", "2.51-3.00", "3.01-3.50", "Above 3.50"]].reset_index()
    effects = read(D + "cgpa_comparisons.csv")[
        [
            "variant",
            "n",
            "kruskal_h_tie_corrected",
            "nominal_p_value",
            "rank_epsilon_squared_H_over_N_minus_1",
            "cliff_delta_P2_minus_P1",
        ]
    ]
    intervals = read(D + "conditional_uncertainty.csv")[
        [
            "variant",
            "assumed_independent_units",
            "resampling_units",
            "conditional_percentile_lower",
            "conditional_percentile_upper",
        ]
    ]
    ordinal = read(X + "ordinal_model_fit.csv")[
        [
            "model",
            "chisq.scaled",
            "df.scaled",
            "cfi.scaled",
            "rmsea.scaled",
            "srmr",
            "cfi.robust",
            "rmsea.robust",
            "passes_followup_screen",
        ]
    ]
    associations = read(X + "observed_item_associations.csv")[
        [
            "country",
            "item_x",
            "item_y",
            "n",
            "spearman_rho",
            "permutation_p_value",
            "holm_p_four_test_family",
            "conditional_95_lower",
            "conditional_95_upper",
        ]
    ]
    return [
        spec(
            "T01",
            "Source records and repeated-pattern accounting",
            sample_table,
            "Record counts do not establish unique people. All primary records are retained. "
            "D5 metadata reports 2614 although the release contains 2613; D3 "
            "reports 22 universities "
            "although 30 literal labels are released. No institution aliases are applied.",
            "A01-A04, B01",
        ),
        spec(
            "T02",
            "D5 source-section measurement screens",
            reliability,
            "U: AI usage; CD: cognitive dependence; T: trust in AI; CT: "
            "reported reduction in independent "
            "thinking; AD: academic decision-making. Names are "
            "source-defined headings, not validated "
            "subscales. Ordinal omega concerns latent responses conditional on a one-factor model. "
            "All-section screen requires alpha/omega >=0.70, item-total >=0.30, loading >=0.40, "
            "maximum residual <=0.10 and no model boundary. No section passes all criteria.",
            "B02-B04",
        ),
        spec(
            "T03",
            "Accepted descriptive k=2 profiles and concentration",
            profiles,
            "Neutral profile numbers are dataset-specific and unordered. ARI "
            "is mean omitted-record "
            "perturbation agreement over 100 subsamples of 80%; it is not predictive accuracy. "
            "D5_P2 includes 200 copies of one full-record pattern: 200/207 "
            "primary and 200/205 sensitivity. "
            "Stability is conditional on these released multiplicities.",
            "B07-B10",
        ),
        spec(
            "T04",
            "C feasibility audit: record-random held-out overlap",
            overlap,
            "Diagnostic allocation only; no classifier was fitted. All 25 survey items define the "
            "target. Five contextual metadata fields avoid that construction but do not restore "
            "respondent independence. The 200-record P2 pattern exceeds both primary allocations "
            "(166 training, 41 held-out); intact-pattern protection cannot satisfy this design.",
            "C01-C04",
        ),
        spec(
            "T05",
            "D3 CGPA bands by nominal descriptive profile",
            bands,
            "Cells are records (within-profile percentage). Self-reported ordered bands are not "
            "continuous grades; the source does not specify an exact 2.50 value. Fixed sensitivity "
            "retains primary labels; refit sensitivity uses accepted B sensitivity labels. "
            "Percentages may differ from 100 by rounding.",
            "D01, D03",
        ),
        spec(
            "T06a",
            "D3 rank comparison and effect size",
            effects,
            "H is tie-corrected Kruskal-Wallis with nominal chi-square reference (df=1). "
            "Rank epsilon squared is explicitly H/(N-1). Cliff delta is P2 minus P1; a negative "
            "value favors higher bands in P1. Profiles are not ordered severity tiers. "
            "Record independence remains unverified, so reference p values are nominal. "
            "All variants are very small and inconclusive, not evidence of equivalence.",
            "D02-D05",
        ),
        spec(
            "T06b",
            "D3 conditional 95% percentile intervals for Cliff delta",
            intervals,
            "10,000 bootstrap repetitions per row. Record and intact-pattern draws are stratified "
            "by fixed profile; literal-institution draws are not. "
            "Independent units are assumptions. "
            "None of these intervals includes profile-estimation uncertainty or establishes "
            "population coverage. All intervals include zero.",
            "D04",
        ),
        spec(
            "T07",
            "External GAID ordinal configural follow-up",
            ordinal,
            "WLSMV with std.lv, theta parameterization and the Wu-Estabrook identification plan. "
            "Follow-up uses scaled CFI >=0.90, RMSEA <=0.08 and SRMR <=0.08; "
            "robust alternatives are "
            "reported separately. Indonesia and multigroup fits fail. CT and TP are blocked by "
            "category support. No equality constraints are tested. USA n=116; Indonesia n=111. "
            "No Bangladesh anchors or latent equivalence are established.",
            "D06-D11",
        ),
        spec(
            "T08",
            "Exploratory observed-item associations within each country",
            associations,
            "GAID6: confidence without AI; CT9: source-credibility checking; TP6: efficient work "
            "completion (consult the source workbook for exact wording). Spearman rho; "
            "9,999 permutations; Holm adjustment across all four tests; "
            "5,000 bootstrap repetitions. "
            "Intervals are marginal conditional 95% intervals, not "
            "multiplicity-adjusted intervals. "
            "No country-difference test, latent comparison or causal inference is made.",
            "D12",
        ),
    ]


def display_value(value) -> str:
    if pd.isna(value):
        return "NA"
    if isinstance(value, (float, np.floating)):
        return f"{value:.4f}"
    return (
        str(value)
        .replace("quality_fixed_profiles", "Quality: fixed")
        .replace("quality_refit_profiles", "Quality: refit")
        .replace("independent_records_reference", "Records (reference)")
        .replace("intact_full_record_patterns", "Intact full patterns")
        .replace("literal_institution_labels", "Literal institutions")
    )


def make_tables(root: Path, destination: Path) -> list[dict]:
    folder = destination / "tables"
    folder.mkdir(exist_ok=True)
    fonts = Path(matplotlib.get_data_path()) / "fonts/ttf"
    pdfmetrics.registerFont(TTFont("ERegular", str(fonts / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("EBold", str(fonts / "DejaVuSans-Bold.ttf")))
    styles = getSampleStyleSheet()
    styles["Title"].fontName = "EBold"
    styles["Title"].fontSize = 17
    styles["Title"].leading = 21
    styles.add(
        ParagraphStyle(
            name="CellE",
            fontName="ERegular",
            fontSize=8,
            leading=10,
            alignment=TA_LEFT,
            spaceAfter=0,
            wordWrap="LTR",
        )
    )
    styles.add(ParagraphStyle(name="NoteE", fontName="ERegular", fontSize=9, leading=12))
    story, pages, specs = [], [], table_specifications(root)

    def footer(canvas, doc):
        canvas.setFont("ERegular", 8)
        canvas.setFillColor(colors.HexColor("#45616D"))
        canvas.drawString(32, 22, "MP1 | Accepted A-D evidence | Publication-lock review copy")
        canvas.drawRightString(809, 22, str(doc.page))

    doc = BaseDocTemplate(
        str(folder / "statistical_tables.pdf"),
        pagesize=landscape(A4),
        leftMargin=32,
        rightMargin=32,
        topMargin=32,
        bottomMargin=38,
        title="MP1 accepted statistical tables",
        author="MP1 research project",
        initialFontName="ERegular",
        invariant=1,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=footer))
    for s in specs:
        data = s["data"]
        data.to_csv(folder / (s["id"] + ".csv"), index=False)
        shown = data.map(display_value)
        labels = [DISPLAY_HEADERS.get(x, x.replace("_", " ")) for x in data.columns]
        rendered = shown.copy()
        rendered.columns = labels
        body = rendered.to_html(index=False, escape=True)
        pages.append(
            f"<section><h2>{s['id']}. {s['title']}</h2>{body}<p>{html.escape(s['note'])}</p>"
            f"<p>Evidence-map claims: {s['claims']}.</p></section>"
        )
        # Standalone LaTeX fragments use booktabs; all values also have full-precision CSV versions.
        (folder / (s["id"] + ".tex")).write_text(
            rendered.to_latex(index=False, escape=True), encoding="utf-8"
        )
        story.extend([Paragraph(f"{s['id']}. {s['title']}", styles["Title"]), Spacer(1, 14)])
        cells = [[Paragraph(html.escape(str(x)), styles["CellE"]) for x in labels]]
        cells += [
            [Paragraph(html.escape(str(x)), styles["CellE"]) for x in row]
            for row in shown.itertuples(index=False, name=None)
        ]
        widths = [doc.width / len(labels)] * len(labels)
        if len(labels) > 5:
            widths[0] *= 1.45
            widths[1:] = [(doc.width - widths[0]) / (len(labels) - 1)] * (len(labels) - 1)
        table = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "ERegular"),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DAE8EC")),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#F3F6F7")],
                    ),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#176681")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        story.extend(
            [
                table,
                Spacer(1, 15),
                Paragraph(s["note"], styles["NoteE"]),
                Spacer(1, 8),
                Paragraph(
                    f"Evidence-map claims: {s['claims']}. CSV retains full precision.",
                    styles["NoteE"],
                ),
                PageBreak(),
            ]
        )
    doc.build(story[:-1])
    (folder / "statistical_tables.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>MP1 statistical tables</title>'
        "<style>body{font:16px/1.5 Arial;max-width:1300px;margin:40px;color:#17323f}"
        "table{border-collapse:collapse;width:100%;font-size:13px}"
        "th,td{padding:8px;border-bottom:1px solid #ccd}"
        "th{background:#dae8ec;text-align:left}section{break-after:page;margin-bottom:60px}"
        "@media print{body{font-size:10pt;margin:0}table{font-size:8pt}}</style>"
        "<h1>Accepted A-D statistical tables</h1>" + "".join(pages) + "</html>",
        encoding="utf-8",
    )
    return [{k: v for k, v in s.items() if k != "data"} for s in specs]


def make_figures(root: Path, destination: Path) -> list[dict]:
    folder = destination / "figures"
    folder.mkdir(exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "MP1-E-accepted",
            "savefig.facecolor": "white",
        }
    )
    read = lambda name: pd.read_csv(root / name)  # noqa: E731
    result = []

    def save(fig, name, data, caption, claims):
        fig.savefig(
            folder / f"{name}.pdf",
            bbox_inches="tight",
            metadata={
                "CreationDate": None,
                "ModDate": None,
                "Creator": "MP1 accepted-evidence renderer",
            },
        )
        fig.savefig(folder / f"{name}.svg", bbox_inches="tight", metadata={"Date": None})
        svg = folder / f"{name}.svg"
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
        fig.savefig(folder / f"{name}.png", bbox_inches="tight", dpi=600)
        data.to_csv(folder / f"{name}_data.csv", index=False)
        plt.close(fig)
        result.append(
            {
                "id": name,
                "caption": caption,
                "claims": claims,
                "formats": ["pdf", "svg", "png"],
                "raster_dpi": 600,
                "plot_data": f"figures/{name}_data.csv",
            }
        )

    data = read(B + "reliability.csv")
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.9), sharey=True, layout="constrained")
    labels = [
        "AI usage",
        "Cognitive dependence",
        "Trust in AI",
        "Reported thinking reduction",
        "Academic decision-making",
    ]
    for ax, col, title in zip(
        axes,
        ["alpha_raw", "omega_ordinal_latent_response"],
        ["A  Raw alpha", "B  Conditional ordinal omega"],
        strict=True,
    ):
        for sample, offset, color, marker in [
            ("full", -0.09, BLUE, "o"),
            ("sensitivity", 0.09, ORANGE, "s"),
        ]:
            values = data[data["sample"].eq(sample)]
            ax.scatter(
                values[col],
                np.arange(5) + offset,
                color=color,
                marker=marker,
                s=35,
                label="Full records" if sample == "full" else "Quality sensitivity",
            )
        ax.set(
            xticks=np.arange(0.3, 0.91, 0.1),
            xlim=(0.3, 0.85),
            title=title,
            yticks=range(5),
            yticklabels=labels,
            xlabel="Coefficient",
        )
        ax.axvline(0.7, color="#888888", linestyle=":", linewidth=1)
        ax.grid(axis="x", alpha=0.15)
    axes[0].invert_yaxis()
    axes[1].legend(loc="lower right", fontsize=8)
    save(
        fig,
        "F01_measurement",
        data,
        "Raw alpha and conditional ordinal omega by source-defined D5 "
        "section. Dotted line marks the reliability component of the fixed screen (0.70); "
        "passing it alone is insufficient. No section passes all screens; "
        "these are not validated subscales.",
        "B02",
    )
    data = read(K + "cluster_metrics.csv")
    fig, axes = plt.subplots(2, 2, figsize=(8.2, 5.6), layout="constrained")
    for row, dataset in enumerate(["D5", "D3"]):
        for col, (metric, label) in enumerate(
            [("silhouette", "Silhouette"), ("ari_mean", "Mean omitted-record ARI")]
        ):
            ax = axes[row, col]
            for sample, color, marker in [("full", BLUE, "o"), ("sensitivity", ORANGE, "s")]:
                part = data[data.dataset.eq(dataset) & data["sample"].eq(sample)]
                ax.plot(
                    part.k,
                    part[metric],
                    color=color,
                    marker=marker,
                    linestyle="-" if sample == "full" else "--",
                    label=sample.capitalize(),
                )
            ax.set(
                title=f"{dataset}: {label}", xticks=range(2, 7), xlabel="Candidate k", ylabel=label
            )
            ax.grid(alpha=0.15)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle(
        "Accepted candidate diagnostics: k=2 reproduces; k=3-6 replay differences disclosed",
        fontsize=10,
    )
    save(
        fig,
        "F02_candidate_partitions",
        data,
        "All accepted k=2 to 6 candidates. The accepted "
        "multicriterion rule selects k=2 in each dataset and sample; these two plotted diagnostics "
        "do not replace that rule. ARI reflects 100 perturbations with 80% subsamples against the "
        "full-record reference, not external validation. Repeated-record "
        "concentration remains explicit in F03. The reconstructed source replay has 247 differing "
        "cells across six nonselected candidate tables. Plotted k=3-6 values remain the "
        "accepted values; complete candidate-grid reproduction is not claimed. Selected k=2 "
        "and the selection ranks/screens/decisions agree. See the discrepancy register.",
        "B07, B09",
    )
    data = read(K + "cluster_centroids.csv")
    data = data[data.k.eq(2) & data["sample"].eq("full")]
    fig, axes = plt.subplots(2, 1, figsize=(9.5, 4.5), layout="constrained")
    for ax, dataset, title in zip(
        axes,
        ["D5", "D3"],
        [
            "D5: 200 of 207 P2 records share one full-record pattern (96.62%)",
            "D3: different instrument; profile numbers do not correspond to D5",
        ],
        strict=True,
    ):
        part = data[data.dataset.eq(dataset)]
        items = list(part.item.drop_duplicates())
        values = part.pivot(index="cluster", columns="item", values="agreement_proportion")[items]
        im = ax.imshow(values, cmap="cividis", vmin=0, vmax=1, aspect="auto")
        sizes = [2406, 207] if dataset == "D5" else [769, 335]
        ax.set(
            xticks=range(len(items)),
            xticklabels=items,
            yticks=[0, 1],
            yticklabels=[f"{dataset}_P{i + 1} (n={n})" for i, n in enumerate(sizes)],
            title=title,
        )
        ax.tick_params(axis="x", labelsize=8)
        for (y, x), value in np.ndenumerate(values.to_numpy()):
            ax.text(
                x,
                y,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=6.6,
                color="black" if value > 0.58 else "white",
            )
    fig.colorbar(im, ax=axes, label="Agreement probability (response > 3)", shrink=0.85, pad=0.02)
    save(
        fig,
        "F03_descriptive_profiles",
        data,
        "Primary k=2 profiles on each dataset's own ordinal "
        "items, with equal item weight. Item IDs resolve to exact wording in "
        "the accepted inventory. "
        "Profiles are unordered, descriptive and instrument-specific. D5_P2 concentration prevents "
        "interpreting its size or stability as prevalence or replication of a psychological type. "
        "No Bangladesh or cross-country latent equivalence is established.",
        "B06, B08, B10",
    )
    bands = read(D + "cgpa_distributions.csv")
    intervals = read(D + "conditional_uncertainty.csv")
    fig, axes = plt.subplots(
        1, 2, figsize=(10, 5.5), layout="constrained", gridspec_kw={"width_ratios": [1, 1.45]}
    )
    colors4 = ["#414487", "#2A788E", "#22A884", "#BBD73B"]
    primary = bands[bands.variant.eq("full")]
    left = np.zeros(2)
    for order, color in enumerate(colors4):
        p = primary[primary.order_code.eq(order)].sort_values("profile")
        axes[0].barh([0, 1], p.fraction, left=left, color=color, label=p.cgpa_band.iloc[0])
        left += p.fraction.to_numpy()
    axes[0].set(
        yticks=[0, 1],
        yticklabels=["D3_P1\nn=769", "D3_P2\nn=335"],
        xlim=(0, 1),
        xlabel="Within-profile fraction",
        title="A  Self-reported CGPA bands",
    )
    axes[0].legend(loc="lower center", bbox_to_anchor=(0.5, -0.3), fontsize=8, ncol=2)
    ax = axes[1]
    labels = []
    for i, row in enumerate(intervals.itertuples()):
        color = [BLUE, ORANGE, "#6A4C93"][i // 3]
        ax.plot(
            [row.conditional_percentile_lower, row.conditional_percentile_upper],
            [i, i],
            color=color,
        )
        ax.scatter(row.cliff_delta, i, color=color, s=23)
        unit = ["Records", "Intact patterns", "Institutions"][i % 3]
        labels.append(f"{list(VARIANTS.values())[i // 3]}\n{unit}")
    ax.axvline(0, color="#888", linestyle=":", linewidth=1)
    ax.set(
        yticks=range(9),
        yticklabels=labels,
        xlabel="Cliff delta (P2 minus P1)",
        title="B  Conditional 95% percentile intervals\nRespondent independence remains unverified",
        xlim=(-0.17, 0.10),
    )
    ax.tick_params(axis="y", labelsize=7.5)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.15)
    save(
        fig,
        "F04_cgpa",
        pd.concat([bands.assign(component="bands"), intervals.assign(component="intervals")]),
        "D3 outcome evidence is very small and inconclusive. Panel A preserves the released "
        "ordinal bands; no grade midpoint is assigned. Panel B shows all nine conditional "
        "bootstrap intervals under distinct independent-unit assumptions (10,000 repetitions). "
        "Profile estimation is fixed and population coverage is not established. Every interval "
        "contains zero; this does not establish no association or equivalence.",
        "D01-D04",
    )
    data = read(X + "observed_item_associations.csv")
    fig, ax = plt.subplots(figsize=(8.3, 3.4), layout="constrained")
    labels = []
    for i, row in enumerate(data.itertuples()):
        color = BLUE if row.country == "USA" else ORANGE
        ax.plot([row.conditional_95_lower, row.conditional_95_upper], [i, i], color=color)
        ax.scatter(row.spearman_rho, i, color=color, s=30)
        labels.append(f"{row.country}, n={row.n}: {row.item_x} with {row.item_y}")
        ax.text(0.39, i, f"{row.holm_p_four_test_family:.4f}", va="center", fontsize=9)
    ax.text(0.39, -0.65, "Holm p", fontsize=9)
    ax.set(
        yticks=range(4),
        yticklabels=labels,
        xlim=(-0.3, 0.51),
        ylim=(3.6, -1),
        xlabel="Within-country Spearman rho",
        title="Observed-item associations: small and uncertain",
    )
    ax.axvline(0, color="#888", linestyle=":", linewidth=1)
    ax.grid(axis="x", alpha=0.15)
    save(
        fig,
        "F05_observed_associations",
        data,
        "Four accepted exploratory observed-item associations. "
        "Segments show marginal conditional 95% bootstrap intervals (5,000 repetitions). "
        "Holm p values adjust the fixed four-test permutation family (9,999 "
        "permutations per test). "
        "No cross-country difference test is performed; no latent, causal or "
        "performance claim follows.",
        "D12",
    )
    return result


def build(root: Path, destination: Path) -> dict:
    os.environ["SOURCE_DATE_EPOCH"] = "0"
    root, destination = root.resolve(), destination.resolve()
    if destination == root or destination.is_relative_to(root / "data"):
        raise ValueError("Publication destination must not overwrite source or private data.")
    audit = aggregate_checks(root)
    destination.mkdir(parents=True, exist_ok=True)
    evidence_map(root, destination)
    tables = make_tables(root, destination)
    figures = make_figures(root, destination)
    dump(destination / "aggregate_consistency.json", audit)
    dump(destination / "table_manifest.json", tables)
    dump(destination / "figure_manifest.json", figures)
    (destination / "figure_captions.md").write_text(
        "# Publication figure captions\n\n"
        + "\n\n".join(
            f"## {f['id']}\n\n{f['caption']}\n\nEvidence-map claims: {f['claims']}."
            for f in figures
        )
        + "\n"
    )
    files = {
        str(p.relative_to(destination)): sha(p)
        for p in sorted(destination.rglob("*"))
        if p.is_file() and p.name != "render_manifest.json"
    }
    manifest = {
        "baseline_commit": BASELINE,
        "source": "Only accepted A-D aggregates",
        "files": files,
        "raw_data_read": False,
        "scientific_fits": 0,
        "reproducibility": "Deterministic under requirements.lock; PDF dates suppressed",
    }
    dump(destination / "render_manifest.json", manifest)
    return {"status": "PASS", "generated_files": len(files) + 1, "destination": str(destination)}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    os.environ.setdefault("SOURCE_DATE_EPOCH", "0")
    value = (
        aggregate_checks(args.root)
        if args.check_only
        else build(args.root, args.output or args.root / "outputs/publication/work_package_e")
    )
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
