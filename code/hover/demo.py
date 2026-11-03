"""Demo: RMN directional tuning in Drosophila vs. Eristalis models, plus one
controversial-stimulus search between the H2 model (MIO <- HSN) and an alternative (MIO <- HSNE).

Run:  python -m hover.demo
"""
from __future__ import annotations

from .controversial import search
from .emd import grating
from .snn import FIELD, drosophila, eristalis, preferred_direction, rmn_rates

DT = 1 / 120
DIRS = [0, 45, 90, 135, 180, 225, 270, 315]


def tuning(circuit):
    per_dir = {d: rmn_rates(circuit, grating(d, FIELD, 0.5, DT), DT) for d in DIRS}
    names = per_dir[0].keys()
    return {n: preferred_direction({d: per_dir[d][n] for d in DIRS}) for n in names}


def main():
    for label, c in [("Drosophila", drosophila()),
                     ("Eristalis female", eristalis("female")),
                     ("Eristalis male (H2: MIO<-HSN)", eristalis("male", "HSN"))]:
        pd = tuning(c)
        print(f"{label:32s} " + "  ".join(f"{k}: {v:5.1f} deg" for k, v in pd.items()))
    print("(0 deg = rightward, 90 deg = downward; HS cells are given a leftward preferred direction in this toy field)")

    p, score, hist = search(eristalis("male", "HSN"), eristalis("male", "HSNE"),
                            readout="MIO", generations=12, lam=5)
    print("\nControversial stimulus H2 (MIO<-HSN) vs alt (MIO<-HSNE):")
    print("  " + ", ".join(f"{k}={v:.1f}" for k, v in p.items()))
    print(f"  |delta MIO rate| = {score:.1f} Hz  (search trace: {[round(float(h), 1) for h in hist]})")


if __name__ == "__main__":
    main()
