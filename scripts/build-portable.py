#!/usr/bin/env python3
"""Build the portable package for this plugin (COORDINATION C1/C2, Option B).

The host package (repo root) is unchanged: it keeps its bin/, hooks and settings, and
existing Code contracts stay intact. This script generates the committed ``portable/``
directory DETERMINISTICALLY from the host tree — never hand-edit portable/, edit the host
and re-run this script; ``--check`` (and the test suite) fails when the two drift.

Portable layout rules (COORDINATION C1, from the loading/platform docs):
  - ``.claude-plugin/plugin.json`` keeps the SAME name as the host manifest, so a synced
    copy never double-runs next to the installed marketplace plugin (loading.md
    name-conflict order).
  - no top-level ``bin/`` (top-level bin blocks Chat/Cowork installs, platform-support.md).
  - hook-invoked scripts stay under ``hooks/`` referenced via ``${CLAUDE_PLUGIN_ROOT}``;
    skill-invoked scripts would go to ``skills/<skill>/scripts/`` via
    ``${CLAUDE_SKILL_DIR}`` (none in this repo).
  - the Python import closure is copied, never symlinked outside the root (loading.md).

Also emits ``PORTABLE-BUILD.json`` (schema haiggoh-portable-build/1) and, with ``--zip``,
``dist/<name>-portable.zip`` with the manifest at the zip root (build.md upload shape).

Usage:
  build-portable.py            build portable/ in place (and refresh PORTABLE-BUILD.json)
  build-portable.py --check    build into a temp dir and diff against committed portable/;
                               exit 1 listing any drift (the freshness gate)
  build-portable.py --zip [--out DIR]   also emit the upload zip (default: dist/, gitignored)
  build-portable.py --commit SHA override the recorded source_commit (default: HEAD)

Env: none. Stdlib only.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

SCHEMA = "haiggoh-portable-build/1"
TRANSFORM_VERSION = "1"
BUILDER = "scripts/build-portable.py"
BUILDER_VERSION = "1.0.0"

# host-relative files copied verbatim into portable/, in sorted order (determinism)
COPY_FILES = [
    ".claude-plugin/plugin.json",
    "hooks/hooks.json",
    "hooks/nudge.sh",
    "skills/measure-twice/SKILL.md",
]

# component metadata per C2/C3 vocabulary (adaptation class / evidence level / surfaces)
COMPONENTS = [
    {"path": ".claude-plugin/plugin.json", "kind": "manifest",
     "adaptation_class": "mechanical", "evidence_level": "source-inspected",
     "surfaces": {"chat": True, "cowork": True, "code": True},
     "notes": "same name+version as the host manifest; an installed marketplace plugin wins "
              "over a synced copy in Code (loading.md name-conflict order), so no double-run"},
    {"path": "skills/measure-twice/SKILL.md", "kind": "skill",
     "adaptation_class": "native-unchanged", "evidence_level": "source-inspected",
     "surfaces": {"chat": True, "cowork": True, "code": True},
     "notes": "pure instruction; strict-YAML frontmatter pinned by tests, portable/ tree included"},
    {"path": "hooks/hooks.json", "kind": "hooks",
     "adaptation_class": "mechanical", "evidence_level": "source-inspected",
     "surfaces": {"chat": False, "cowork": True, "code": True},
     "notes": "Chat ignores plugin hooks, Cowork loads them, Code runs them (platform-support.md)"},
    {"path": "hooks/nudge.sh", "kind": "hook-script",
     "adaptation_class": "native-unchanged", "evidence_level": "source-inspected",
     "surfaces": {"chat": False, "cowork": True, "code": True},
     "notes": "bash 3.2, stateless, references ${CLAUDE_PLUGIN_ROOT} only — portable as-is"},
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git(args, cwd):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                          check=True).stdout.strip()


def source_identity(root, commit_override):
    commit = commit_override or git(["rev-parse", "HEAD"], root)
    remote = ""
    try:
        remote = git(["remote", "get-url", "origin"], root)
    except subprocess.CalledProcessError:
        pass
    m = re.match(r"(?:git@([^:]+):|https://([^/]+)/)", remote or "")
    source_repo = f"{m.group(1) or m.group(2)}/{os.path.basename(root.rstrip('/'))}" \
        if m else f"haiggoh/{os.path.basename(root.rstrip('/'))}"
    return source_repo, commit


def build_tree(root, dest):
    """Write the portable package into dest/ (a fresh dir) and return the file map."""
    manifest = json.loads(open(os.path.join(root, ".claude-plugin", "plugin.json")).read())
    for rel in COPY_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        os.chmod(dst, 0o755 if rel.endswith(".sh") else 0o644)
    return manifest


def write_build_json(dest, root, commit_override):
    source_repo, commit = source_identity(root, commit_override)
    files = {}
    for dirpath, _dirnames, filenames in os.walk(dest):
        for fn in sorted(filenames):
            p = os.path.join(dirpath, fn)
            files[os.path.relpath(p, dest)] = sha256_file(p)
    doc = {
        "schema": SCHEMA,
        "source_repo": source_repo,
        "source_commit": commit,
        "builder": BUILDER,
        "builder_version": BUILDER_VERSION,
        "transform_version": TRANSFORM_VERSION,
        "files": files,
        "components": COMPONENTS,
    }
    with open(os.path.join(dest, "PORTABLE-BUILD.json"), "w") as f:
        f.write(json.dumps(doc, indent=2, sort_keys=True) + "\n")


def diff_trees(a, b):
    """Relative paths that differ between two dirs (existence or content)."""
    def rels(root):
        out = set()
        for dirpath, _dn, filenames in os.walk(root):
            for fn in filenames:
                out.add(os.path.relpath(os.path.join(dirpath, fn), root))
        return out
    out = []
    for rel in sorted(rels(a) | rels(b)):
        pa, pb = os.path.join(a, rel), os.path.join(b, rel)
        if not os.path.exists(pa) or not os.path.exists(pb) \
                or sha256_file(pa) != sha256_file(pb):
            out.append(rel)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="build-portable.py",
        description="Generate the committed portable/ package (COORDINATION C1/C2) from the "
                    "host tree. Never hand-edit portable/.")
    ap.add_argument("--check", action="store_true",
                    help="build into a temp dir and diff against committed portable/; "
                         "exit 1 listing drift")
    ap.add_argument("--zip", action="store_true", help="also emit the upload zip")
    ap.add_argument("--out", metavar="DIR", default=None, help="zip output dir (default dist/)")
    ap.add_argument("--commit", metavar="SHA", default=None, help="record this source_commit")
    args = ap.parse_args(argv)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    portable = os.path.join(root, "portable")

    if args.check:
        if not os.path.isdir(portable):
            print("✗ portable/ does not exist — run scripts/build-portable.py first")
            return 1
        with tempfile.TemporaryDirectory() as tmp:
            fresh = os.path.join(tmp, "p")
            build_tree(root, fresh)
            write_build_json(fresh, root, args.commit)
            drift = diff_trees(fresh, portable)
        if drift:
            print("✗ portable/ drifted from a fresh build:")
            for rel in drift:
                print("  ", rel)
            print("  fix: run scripts/build-portable.py and commit the result")
            return 1
        print("✓ portable/ matches a fresh build")
        return 0

    if os.path.isdir(portable):
        shutil.rmtree(portable)
    os.makedirs(portable)
    build_tree(root, portable)
    write_build_json(portable, root, args.commit)
    n = sum(len(fs) for _d, _dn, fs in os.walk(portable))
    print(f"✓ built portable/ ({n} files) + PORTABLE-BUILD.json")

    if args.zip:
        manifest = json.loads(open(os.path.join(root, ".claude-plugin", "plugin.json")).read())
        out_dir = args.out or os.path.join(root, "dist")
        os.makedirs(out_dir, exist_ok=True)
        zpath = os.path.join(out_dir, f"{manifest['name']}-portable.zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for dirpath, _dirnames, filenames in os.walk(portable):
                for fn in sorted(filenames):
                    p = os.path.join(dirpath, fn)
                    z.write(p, os.path.relpath(p, portable))  # manifest at zip root
        print(f"✓ wrote {zpath}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
