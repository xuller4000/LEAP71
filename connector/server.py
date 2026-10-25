"""MCP-Connector: stellt Konstruktionsrichtlinien und ShapeKernel-Doku aus diesem Repo bereit.

Start lokal (Claude Desktop / Claude Code):  python connector/server.py
Start remote (claude.ai Custom Connector):   python connector/server.py --http --port 8000
"""
import argparse
import re
from pathlib import Path

from mcp.server.mcpserver import MCPServer

ROOT = Path(__file__).resolve().parent.parent
GUIDELINES = ROOT / "guidelines"
DOCS = ROOT / "Documentation"
SHAPEKERNEL = ROOT / "ShapeKernel"

mcp = MCPServer(
    "leap71-konstruktion",
    instructions=(
        "Vor jeder Konstruktion in Fusion zuerst list_guidelines und die passenden "
        "Richtlinien mit get_guideline lesen und einhalten. Fusion-Skripte mit "
        "fusion_script_template als Gerüst beginnen."
    ),
)


def _md_files():
    files = []
    for base in (GUIDELINES, DOCS):
        if base.is_dir():
            files += sorted(base.rglob("*.md"))
    readme = ROOT / "README.md"
    if readme.is_file():
        files.append(readme)
    return files


def _resolve(name: str) -> Path | None:
    for f in _md_files():
        if name in (f.name, f.stem, str(f.relative_to(ROOT))):
            return f
    return None


@mcp.tool()
def list_guidelines() -> list[str]:
    """Listet alle Richtlinien- und Doku-Dateien (relativ zum Repo-Root)."""
    return [str(f.relative_to(ROOT)) for f in _md_files()]


@mcp.tool()
def get_guideline(name: str) -> str:
    """Liefert den Inhalt einer Richtlinie (Dateiname, Name ohne Endung oder relativer Pfad)."""
    f = _resolve(name)
    if f is None:
        return f"Nicht gefunden: {name}. Verfügbar: {', '.join(list_guidelines())}"
    return f.read_text(encoding="utf-8", errors="replace")


@mcp.tool()
def search_guidelines(query: str, max_hits: int = 20) -> list[str]:
    """Volltextsuche (ohne Groß-/Kleinschreibung) in Richtlinien und Doku. Gibt Datei:Zeile: Text zurück."""
    pat = re.compile(re.escape(query), re.IGNORECASE)
    hits = []
    for f in _md_files():
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if pat.search(line):
                hits.append(f"{f.relative_to(ROOT)}:{i}: {line.strip()}")
                if len(hits) >= max_hits:
                    return hits
    return hits


@mcp.tool()
def list_shapekernel_classes(category: str = "") -> list[str]:
    """Listet ShapeKernel-Quelldateien (C#), optional gefiltert nach Unterordner, z.B. 'BaseShapes'."""
    base = SHAPEKERNEL / category if category else SHAPEKERNEL
    if not base.is_dir():
        return [f"Unbekannte Kategorie: {category}"]
    return [str(f.relative_to(ROOT)) for f in sorted(base.rglob("*.cs"))]


@mcp.tool()
def read_shapekernel_source(path: str) -> str:
    """Liest eine ShapeKernel-Quelldatei (Pfad relativ zum Repo, muss unter ShapeKernel/ liegen)."""
    f = (ROOT / path).resolve()
    if SHAPEKERNEL.resolve() not in f.parents or not f.is_file():
        return "Pfad ungültig oder nicht unter ShapeKernel/."
    return f.read_text(encoding="utf-8", errors="replace")


@mcp.tool()
def fusion_script_template(name: str = "LEAP71Part") -> str:
    """Gerüst für ein Fusion-Python-Skript (Autodesk Fusion API). Maße in cm, wie von Fusion intern verwendet."""
    return f'''import adsk.core, adsk.fusion, traceback


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        root = design.rootComponent

        # Parameter aus den Richtlinien hier als Benutzerparameter anlegen (Fusion rechnet intern in cm).
        # design.userParameters.add("wall", adsk.core.ValueInput.createByString("2 mm"), "mm", "Wandstärke")

        comp = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
        comp.name = "{name}"

        sketch = comp.sketches.add(root.xYConstructionPlane)
        # TODO: Geometrie gemäß Richtlinien skizzieren und extrudieren

    except:
        if ui:
            ui.messageBox(traceback.format_exc())
'''


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--http", action="store_true", help="Streamable HTTP statt stdio (für claude.ai)")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    if args.http:
        mcp.settings.port = args.port
        mcp.settings.host = "0.0.0.0"
        mcp.run("streamable-http")
    else:
        mcp.run()
