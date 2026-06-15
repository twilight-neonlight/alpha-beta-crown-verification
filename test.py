"""
Entry point: run alpha-beta-CROWN on our MNIST MLP and record the results.

alpha-beta-CROWN is invoked as an external program (its complete_verifier/abcrown.py),
driven by configs/mnist_mlp.yaml, which in turn reads the instances in instances.csv.
This wrapper:
    1. locates the cloned abcrown.py,
    2. runs it from THIS project's root (so the relative paths in the CSV resolve),
    3. streams the verifier's output to the console and saves it to
       results/verification_results.txt.

How to point this script at your alpha-beta-CROWN clone (any one of these):
    * pass it explicitly:   python test.py --abcrown /path/to/alpha-beta-CROWN
    * set an env variable:   ABCROWN_PATH=/path/to/alpha-beta-CROWN
    * place the clone next to this repo (../alpha-beta-CROWN), which is auto-detected.
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def find_abcrown(explicit=None):
    """Locate complete_verifier/abcrown.py from an arg, env var, or common paths."""
    candidates = []
    if explicit:
        candidates.append(explicit)
    if os.environ.get("ABCROWN_PATH"):
        candidates.append(os.environ["ABCROWN_PATH"])
    # Common layouts: clone beside or inside this repo.
    candidates += [
        os.path.join(PROJECT_ROOT, "..", "alpha-beta-CROWN"),
        os.path.join(PROJECT_ROOT, "alpha-beta-CROWN"),
        os.path.expanduser("~/alpha-beta-CROWN"),
    ]

    for base in candidates:
        if not base:
            continue
        # Accept either the repo root or the complete_verifier dir or the file itself.
        for rel in ("complete_verifier/abcrown.py", "abcrown.py", ""):
            path = os.path.normpath(os.path.join(base, rel)) if rel else os.path.normpath(base)
            if path.endswith("abcrown.py") and os.path.isfile(path):
                return path
    return None


def main():
    parser = argparse.ArgumentParser(description="Run alpha-beta-CROWN on the MNIST MLP.")
    parser.add_argument("--abcrown", default=None,
                        help="path to the alpha-beta-CROWN clone (or its abcrown.py)")
    parser.add_argument("--config", default="configs/mnist_mlp.yaml",
                        help="verification config (relative to this project root)")
    parser.add_argument("--results", default="results/verification_results.txt",
                        help="where to save the captured verifier output")
    args = parser.parse_args()

    abcrown_py = find_abcrown(args.abcrown)
    if abcrown_py is None:
        sys.exit(
            "ERROR: could not find abcrown.py.\n"
            "Clone it and retry, e.g.:\n"
            "  git clone https://github.com/Verified-Intelligence/alpha-beta-CROWN ../alpha-beta-CROWN\n"
            "or pass --abcrown /path/to/alpha-beta-CROWN (or set ABCROWN_PATH)."
        )

    config_path = os.path.join(PROJECT_ROOT, args.config)
    results_path = os.path.join(PROJECT_ROOT, args.results)
    os.makedirs(os.path.dirname(results_path), exist_ok=True)

    # Force the verifier to resolve CSV-relative paths against THIS project root.
    cmd = [
        sys.executable, abcrown_py,
        "--config", config_path,
        "--root_path", PROJECT_ROOT,
    ]
    print("Running:", " ".join(cmd))
    print("Working dir:", PROJECT_ROOT)
    print("-" * 70)

    # Stream output live while also capturing it for the results file.
    with open(results_path, "w", encoding="utf-8") as out:
        out.write(f"# alpha-beta-CROWN run @ {datetime.now().isoformat()}\n")
        out.write(f"# config: {args.config}\n")
        out.write(f"# command: {' '.join(cmd)}\n\n")
        out.flush()
        proc = subprocess.Popen(
            cmd, cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        for line in proc.stdout:
            sys.stdout.write(line)
            out.write(line)
        proc.wait()

    print("-" * 70)
    print(f"Exit code: {proc.returncode}")
    print(f"Full log saved to: {results_path}")
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
