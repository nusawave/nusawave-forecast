#!/usr/bin/env python3
"""Generate placeholder logo for the frontend (does not touch staticmap.png)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt

ICONS_DIR = ROOT / "assets" / "icons"


def generate_logo():
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    out = ICONS_DIR / "nusawave-logo.png"

    fig, ax = plt.subplots(figsize=(2, 2), dpi=100)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(plt.Circle((0.5, 0.5), 0.42, color="#1a6fb5", zorder=1))
    ax.text(
        0.5, 0.5, "NW",
        ha="center", va="center",
        fontsize=28, fontweight="bold", color="white",
        fontfamily="sans-serif",
    )
    plt.savefig(out, format="png", bbox_inches="tight", pad_inches=0.05, transparent=True)
    plt.close(fig)
    print(f"[INFO] Wrote {out}")


if __name__ == "__main__":
    generate_logo()
