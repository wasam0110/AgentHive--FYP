"""Tracked-file hygiene only; this is not a secret-content scanner."""

from pathlib import Path, PurePosixPath
import subprocess


def main():
    for name in ["AGENTS.md", "README.md", "docs/PRD.md", ".gitignore"]:
        if not Path(name).is_file():
            raise SystemExit(f"Missing required file: {name}")
    paths = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
    blocked = []
    for path in filter(None, paths):
        parts = PurePosixPath(path).parts
        name = parts[-1]
        private_env = (name == ".env" or name.startswith(".env.")) and name != ".env.example"
        private_dir = bool(
            set(parts)
            & {
                ".venv",
                "venv",
                "node_modules",
                "__pycache__",
                ".next",
                ".local",
                "playwright-report",
                "test-results",
            }
        )
        if (
            private_env
            or private_dir
            or name
            in {
                "AGENTS.local.md",
                "Wasam-instructions.md",
                "Asad-instructions.md",
                "Arif-instructions.md",
                "shizza-instructions.md",
            }
            or path.startswith("submissions/private/")
            or name.endswith((".db", ".db-wal", ".db-shm"))
        ):
            blocked.append(path)
    if blocked:
        raise SystemExit("Private/generated files tracked: " + ", ".join(blocked))
    print("Required files and tracked-file hygiene passed (not a secret scan).")


if __name__ == "__main__":
    main()
