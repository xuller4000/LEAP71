# LEAP71 Konstruktions-Connector (MCP)

Stellt `guidelines/`, `Documentation/` und den ShapeKernel-Quellcode für Claude bereit.

Tools: `list_guidelines`, `get_guideline`, `search_guidelines`, `list_shapekernel_classes`, `read_shapekernel_source`, `fusion_script_template`.

## Lokal (Claude Desktop / Claude Code, stdio)
    pip install -r connector/requirements.txt
    claude mcp add leap71 -- python /Pfad/zum/Repo/connector/server.py

## Remote für claude.ai über Cloudflare Tunnel
Umgebungsvariablen des Servers:
- `ALLOWED_HOSTS`: Hostname des Tunnels ohne https://, z.B. `abc-def.trycloudflare.com`
- `SECRET_PATH`: zufälliger Pfadanteil, Endpunkt wird `https://<host>/<SECRET_PATH>/mcp`

PowerShell:
    $env:ALLOWED_HOSTS="abc-def.trycloudflare.com"; $env:SECRET_PATH="<zufall>"
    python connector\server.py --http --port 8000
    cloudflared tunnel --url http://127.0.0.1:8000
