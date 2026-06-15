"""
Generate VNNLIB robustness specifications for the MNIST MLP.

For each sample image x (one per digit) and each perturbation radius eps, we emit
one .vnnlib file encoding a local L-infinity robustness property:

    "For every input within the eps-ball around x (clipped to [0, 1]),
     the network still predicts the true label."

VNNLIB convention (same as VNN-COMP):
    - The `assert` block describes the UNSAFE region (the negation of the property).
    - alpha-beta-CROWN returns:
        * unsat  -> no unsafe point exists       -> property holds (robust / "verified")
        * sat    -> an unsafe point was found     -> counterexample (not robust / "falsified")

The unsafe region here is: "some rival class j scores at least as high as the
true label", i.e.  OR_j ( Y_j >= Y_true ),  for all j != true_label.

We reuse the EXACT sample inputs from the Marabou assignment (models/sample_inputs.npy)
so the two tools verify identical instances and the comparison is apples-to-apples.
"""

import os
import argparse
import numpy as np


def write_vnnlib(path, x, true_label, eps, n_inputs=784, n_outputs=10):
    """Write a single robustness VNNLIB spec for image `x` and radius `eps`."""
    # L-infinity ball, clipped to the valid pixel range [0, 1] (inputs were MinMax-scaled).
    lb = np.clip(x - eps, 0.0, 1.0)
    ub = np.clip(x + eps, 0.0, 1.0)

    with open(path, "w") as f:
        f.write(f"; MNIST MLP local robustness\n")
        f.write(f"; true label = {true_label}, eps = {eps}\n\n")

        # Declare input variables X_0 .. X_783
        for i in range(n_inputs):
            f.write(f"(declare-const X_{i} Real)\n")
        f.write("\n")
        # Declare output variables Y_0 .. Y_9
        for j in range(n_outputs):
            f.write(f"(declare-const Y_{j} Real)\n")
        f.write("\n")

        # Input constraints: per-pixel L-inf box
        f.write("; input constraints (eps-ball, clipped to [0,1])\n")
        for i in range(n_inputs):
            f.write(f"(assert (<= X_{i} {ub[i]:.8f}))\n")
            f.write(f"(assert (>= X_{i} {lb[i]:.8f}))\n")
        f.write("\n")

        # Output constraint: negation of robustness.
        # UNSAFE iff some rival class j (j != true_label) scores >= true label.
        f.write("; unsafe region: some rival class beats the true class\n")
        f.write("(assert (or\n")
        for j in range(n_outputs):
            if j == true_label:
                continue
            f.write(f"  (and (>= Y_{j} Y_{true_label}))\n")
        f.write("))\n")


def main():
    parser = argparse.ArgumentParser(description="Generate VNNLIB robustness specs.")
    parser.add_argument("--inputs", default="models/sample_inputs.npy")
    parser.add_argument("--labels", default="models/sample_labels.npy")
    parser.add_argument("--onnx", default="models/model.onnx",
                        help="ONNX path written into the instances CSV")
    parser.add_argument("--out-dir", default="vnnlib")
    parser.add_argument("--csv", default="instances.csv",
                        help="VNN-COMP style instances list (onnx,vnnlib,timeout)")
    parser.add_argument("--eps", type=float, nargs="+", default=[0.01, 0.05],
                        help="perturbation radii to generate")
    parser.add_argument("--timeout", type=int, default=120,
                        help="per-instance timeout (seconds) recorded in the CSV")
    args = parser.parse_args()

    X = np.load(args.inputs)
    y = np.load(args.labels)
    os.makedirs(args.out_dir, exist_ok=True)

    rows = []
    for eps in args.eps:
        for x, label in zip(X, y):
            label = int(label)
            fname = f"prop_digit{label}_eps{eps}.vnnlib"
            fpath = os.path.join(args.out_dir, fname)
            write_vnnlib(fpath, x.astype(np.float64), label, eps)
            # CSV rows use POSIX-style relative paths so they work under WSL/Linux,
            # where alpha-beta-CROWN normally runs.
            vnnlib_rel = f"{args.out_dir}/{fname}"
            rows.append(f"{args.onnx},{vnnlib_rel},{args.timeout}")
            print(f"wrote {fpath}")

    with open(args.csv, "w") as f:
        f.write("\n".join(rows) + "\n")
    print(f"\nwrote {args.csv} with {len(rows)} instances")


if __name__ == "__main__":
    main()
