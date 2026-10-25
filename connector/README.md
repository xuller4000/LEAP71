# LEAP71 Konstruktions-Connector (MCP)

Stellt `guidelines/`, `Documentation/` und den ShapeKernel-Quellcode für Claude bereit.

Tools: `list_guidelines`, `get_guideline`, `search_guidelines`, `list_shapekernel_classes`, `read_shapekernel_source`, `fusion_script_template`.

## Lokal (Claude Desktop / Claude Code, stdio)
    pip install -r connector/requirements.txt
    claude mcp add leap71 -- python /Pfad/zum/Repo/connector/server.py

Für Claude Desktop in `claude_desktop_config.json` unter `mcpServers`:
    "leap71": {"command": "python", "args": ["C:\\Pfad\\zum\\Repo\\connector\\server.py"]}

## Remote (claude.ai, Custom Connector)
    python connector/server.py --http --port 8000
Server öffentlich per HTTPS erreichbar machen (Hosting oder Tunnel), URL `https://<host>/mcp` unter
claude.ai > Einstellungen > Connectors > Benutzerdefinierten Connector hinzufügen eintragen.
Hinweis: Ohne Authentifizierung ist der Endpunkt für jeden mit der URL lesbar.
