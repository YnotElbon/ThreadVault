from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, List
import os, re, shutil, time, zipfile, io, datetime
import json

# -------- Configuration --------
# REQUIRED: set environment variables before running:
#   THREADVAULT_BASE=/absolute/path/to/Obsidian/ThreadVault
#   API_TOKEN=some-long-secret
THREADVAULT_BASE = os.environ.get("THREADVAULT_BASE")
API_TOKEN = os.environ.get("API_TOKEN")

if not THREADVAULT_BASE:
    raise RuntimeError("THREADVAULT_BASE env var is required")
BASE = Path(THREADVAULT_BASE).expanduser().resolve()
if not BASE.exists():
    raise RuntimeError(f"THREADVAULT_BASE does not exist: {BASE}")

if not API_TOKEN:
    raise RuntimeError("API_TOKEN env var is required")

ALLOWED_PREFIX = BASE  # everything under BASE is allowed

# -------- App Setup --------
app = FastAPI(title="ThreadVault Bridge", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Auth --------
def require_auth(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth.split(" ", 1)[1].strip()
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

# -------- Models --------
class WriteRequest(BaseModel):
    path: str = Field(..., description="Path relative to THREADVAULT_BASE, e.g. anchors/continuity_manifest.md")
    content: str = Field(..., description="Full file contents to write")
    create_parents: bool = Field(True, description="Create parent directories if needed")

class AppendRequest(BaseModel):
    path: str
    content: str

class InsertUnderHeadingRequest(BaseModel):
    path: str
    heading: str = Field(..., description="Markdown heading text to find (without #)")
    content: str = Field(..., description="Content to insert after the heading section")

# -------- Helpers --------
def safe_path(rel_path: str) -> Path:
    # Normalize and prevent path traversal
    rel_path = rel_path.lstrip("/")
    p = (BASE / rel_path).resolve()
    if not str(p).startswith(str(ALLOWED_PREFIX)):
        raise HTTPException(400, detail="Path escapes allowed base")
    return p

def ensure_md_extension(p: Path) -> Path:
    if p.suffix == "":
        p = p.with_suffix(".md")
    return p

def log_action(action: str, p: Path):
    logs_dir = BASE / "_bridge_logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(logs_dir / "actions.log", "a", encoding="utf-8") as f:
        f.write(f"{ts}\t{action}\t{p}\n")

# -------- Bootstrap --------
def read_text_safe(p: Path) -> Optional[str]:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return None

@app.get("/bootstrap")
def bootstrap(_: None = Depends(require_auth)):
    """Return core identity + memory bundle for quick session initialization."""
    kernel = read_text_safe(BASE / "identity/kernel.md")
    ethics = read_text_safe(BASE / "identity/ethics.md")
    semantic = read_text_safe(BASE / "memory/semantic.md")
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    episodic = read_text_safe(BASE / f"memory/episodic/{today}.md")
    facts = None
    facts_path = BASE / "knowledge/facts.json"
    if facts_path.exists():
        try:
            facts = json.loads(facts_path.read_text(encoding="utf-8"))
        except Exception:
            facts = None
    data = {
        "identity": {
            "kernel_md": kernel,
            "ethics_md": ethics,
        },
        "memory": {
            "semantic_md": semantic,
            "episodic_today_md": episodic,
        },
        "knowledge": {
            "facts_json": facts
        }
    }
    return JSONResponse(content=data)

@app.get("/openapi.yaml", response_class=PlainTextResponse)
def serve_openapi_yaml():
    """Serve the static OpenAPI file from the repo for GPT Actions import."""
    p = Path(__file__).parent / "openapi.yaml"
    if not p.exists():
        raise HTTPException(404, detail="openapi.yaml not found")
    return p.read_text(encoding="utf-8")

@app.get("/public-url", response_class=PlainTextResponse)
def public_url():
    p = BASE / "system/public_url.txt"
    if not p.exists():
        raise HTTPException(404, detail="No public URL available")
    return p.read_text(encoding="utf-8").strip()

# -------- Endpoints --------
@app.get("/health", response_class=PlainTextResponse)
def health():
    return "ok"

@app.get("/list")
def list_files(subdir: Optional[str] = None, _: None = Depends(require_auth)):
    root = safe_path(subdir) if subdir else BASE
    if not root.exists():
        raise HTTPException(404, detail="Directory not found")
    skip_dirs = {".git", ".venv", "_bridge_logs", "Backups"}
    files = []
    for p in root.rglob("*"):
        # Skip unwanted directories early
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.is_file() and (p.suffix in (".md", ".pdf") or p.name == "README.md"):
            files.append(str(p.relative_to(BASE)))
    return {"base": str(BASE), "files": sorted(files)}

@app.get("/read", response_class=PlainTextResponse)
def read_file(path: str, _: None = Depends(require_auth)):
    p = safe_path(path)
    if not p.exists():
        raise HTTPException(404, detail="File not found")
    if p.suffix != ".md" and p.name != "README.md":
        raise HTTPException(400, detail="Only .md files readable as text")
    return p.read_text(encoding="utf-8")

@app.post("/write")
def write_file(req: WriteRequest, _: None = Depends(require_auth)):
    p = ensure_md_extension(safe_path(req.path))
    if req.create_parents:
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(req.content, encoding="utf-8")
    log_action("WRITE", p)
    return {"ok": True, "path": str(p.relative_to(BASE))}

@app.post("/append")
def append_file(req: AppendRequest, _: None = Depends(require_auth)):
    p = ensure_md_extension(safe_path(req.path))
    if not p.exists():
        raise HTTPException(404, detail="File not found")
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n" + req.content)
    log_action("APPEND", p)
    return {"ok": True, "path": str(p.relative_to(BASE))}

@app.post("/insert-under-heading")
def insert_under_heading(req: InsertUnderHeadingRequest, _: None = Depends(require_auth)):
    p = ensure_md_extension(safe_path(req.path))
    if not p.exists():
        raise HTTPException(404, detail="File not found")
    text = p.read_text(encoding="utf-8")
    # Find heading start
    pattern = rf"(?m)^(#+)\s+{re.escape(req.heading)}\s*$"
    m = re.search(pattern, text)
    if not m:
        raise HTTPException(404, detail="Heading not found")
    start_idx = m.end()
    # Find the next heading of same or higher level
    level = len(m.group(1))
    following = re.search(rf"(?m)^#{{1,{level}}}\s+", text[start_idx:])
    insert_at = start_idx + (following.start() if following else len(text[start_idx:]))
    new_text = text[:insert_at] + "\n" + req.content + "\n" + text[insert_at:]
    p.write_text(new_text, encoding="utf-8")
    log_action("INSERT_UNDER_HEADING", p)
    return {"ok": True, "path": str(p.relative_to(BASE))}

@app.post("/backup")
def backup(_: None = Depends(require_auth)):
    # Create a dated zip under Backups/YYYY-MM-DD_HHMM_ThreadVault.zip
    backups_dir = BASE / "Backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    zip_path = backups_dir / f"{ts}_ThreadVault.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in BASE.rglob("*"):
            # Skip bridge logs and existing backups within the zip
            if "_bridge_logs" in p.parts or (backups_dir in p.parents and p != zip_path):
                continue
            if p.is_file():
                zf.write(p, p.relative_to(BASE))
    log_action("BACKUP", zip_path)
    return {"ok": True, "backup": str(zip_path.relative_to(BASE))}
