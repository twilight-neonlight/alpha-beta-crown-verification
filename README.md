# alpha-beta-crown-verification

Neural-network robustness verification using **α,β-CROWN** on an external MNIST MLP.

This project reuses the *same* model and inputs as the Marabou assignment
(Assignment #3) so the two verifiers can be compared on identical instances.

---

## What is verified

For each sample image `x` (one per digit) and radius `ε`, we check local
L∞ robustness: *does the network keep the true label for every input within the
ε-ball around `x` (clipped to `[0,1]`)?*

- **safe** → property holds for the whole ε-ball (Verified / robust)
- **unsafe** → a counterexample was found (Falsified / not robust)
- **unknown / timeout** → not decided within the time budget

The negation of robustness is encoded as VNNLIB (the "unsafe" region where some
rival class beats the true class), exactly as in VNN-COMP.

---

## Project structure

```
alpha-beta-crown-verification/
├── models/
│   ├── model.onnx              # MNIST MLP 784→32→16→10 (ReLU), reused from Marabou
│   ├── sample_inputs.npy       # one correctly-classified image per digit (10×784)
│   └── sample_labels.npy       # labels 0..9
├── configs/
│   └── mnist_mlp.yaml          # α,β-CROWN config (drives instances.csv)
├── vnnlib/                     # 20 generated robustness specs (10 digits × 2 ε)
├── src/
│   └── gen_vnnlib.py           # builds vnnlib specs + instances.csv from samples
├── results/                    # captured verifier output
├── instances.csv               # VNN-COMP style: onnx,vnnlib,timeout per row
├── train.py                    # (reproducibility) trains the MLP and exports ONNX
├── test.py                     # entry point: runs α,β-CROWN via configs/mnist_mlp.yaml
├── requirements.txt            # deps for spec generation + the test wrapper
└── report.pdf                  # analysis report
```

---

## Setup

### 1. Python deps for this repo (spec generation + wrapper)

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt      # Windows
# source .venv/bin/activate && pip install -r requirements.txt   # Linux/WSL
```

### 2. Install α,β-CROWN (separate environment)

α,β-CROWN ships its own Conda environment (PyTorch + auto_LiRPA). A Linux box or
WSL is recommended; a GPU is optional for this tiny MLP.

```bash
git clone https://github.com/Verified-Intelligence/alpha-beta-CROWN ../alpha-beta-CROWN
cd ../alpha-beta-CROWN
conda env create -f complete_verifier/environment.yml   # creates env 'alpha-beta-crown'
conda activate alpha-beta-crown
```

---

## Run

```bash
# 1. (re)generate the VNNLIB specs + instances.csv from the saved samples
python src/gen_vnnlib.py

# 2. run α,β-CROWN on every instance and capture the verdicts
python test.py
```

`test.py` finds your α,β-CROWN clone automatically if it sits at
`../alpha-beta-CROWN`; otherwise pass `--abcrown /path/to/alpha-beta-CROWN`
or set the `ABCROWN_PATH` environment variable. The full verifier log is saved to
`results/verification_results.txt`.

---

## Reproducing the model (optional)

`models/model.onnx` is committed, so this is only needed to rebuild from scratch:

```bash
python train.py     # trains the MLP and re-exports models/model.onnx + samples
```
