from __future__ import annotations

import math
import json
from pathlib import Path
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# Simple plot defaults (keeps plots readable without repeating sizes everywhere)
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})


def make_run_dir(outputs_dir: str | Path, scene: str, solver: str, integrator: str, n: int) -> Path:
    """Create a new folder inside outputs/ for this run."""
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"{timestamp}_{scene}_{solver}_{integrator}_N{n}"

    run_dir = outputs_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def plot_final_xy(bodies, filepath: str | Path, title: str | None = None, clip_quantile: float | None = None) -> None:
    """Save a final-position XY scatter plot. Optionally clip outliers for readability."""
    xs = [b.x for b in bodies]
    ys = [b.y for b in bodies]

    plt.figure(figsize=(6, 6))
    plt.scatter(xs, ys, s=8, alpha=0.8)
    plt.gca().set_aspect("equal", adjustable="box")

    if clip_quantile is not None and xs:
        rs = [math.hypot(x, y) for x, y in zip(xs, ys)]
        rs_sorted = sorted(rs)

        q = min(max(clip_quantile, 0.0), 1.0)
        k = int(q * (len(rs_sorted) - 1))
        r_lim = rs_sorted[k] if rs_sorted else 1.0

        lim = 1.05 * r_lim
        plt.xlim(-lim, lim)
        plt.ylim(-lim, lim)

    plt.xlabel("x")
    plt.ylabel("y")
    if title:
        plt.title(title)

    plt.savefig(filepath, dpi=200, bbox_inches="tight")
    plt.close()


def plot_energy_drift(energy_drift, filepath: str | Path, title: str | None = None) -> None:
    """Plot |energy drift| on a log scale (helps when drift spans many orders of magnitude)."""
    steps = list(range(len(energy_drift)))

    eps = 1e-16
    safe = [max(abs(v), eps) for v in energy_drift]

    plt.figure(figsize=(7, 4))
    plt.plot(steps, safe, linewidth=1.5)

    plt.xlabel("step")
    plt.ylabel("|relative energy drift| (log)")
    if title:
        plt.title(title)

    plt.grid(True, alpha=0.3)
    plt.yscale("log")

    plt.savefig(filepath, dpi=200, bbox_inches="tight")
    plt.close()


def save_metadata_json(metadata: dict, filepath: str | Path) -> None:
    """Write metadata to a JSON file (optional)."""
    filepath = Path(filepath)
    with filepath.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def save_stepc_outputs(sim, run_dir: Path, title_prefix: str | None = None) -> list[Path]:
    """Save plots for Step C (final XY + energy drift)."""
    saved: list[Path] = []

    final_full = run_dir / "final_xy_full.png"
    plot_final_xy(sim.state.bodies, final_full, title=f"{title_prefix} — Final XY (full)" if title_prefix else None)
    saved.append(final_full)

    final_zoom = run_dir / "final_xy_zoom.png"
    plot_final_xy(sim.state.bodies, final_zoom, title=f"{title_prefix} — Final XY (zoom)" if title_prefix else None, clip_quantile=0.95)
    saved.append(final_zoom)

    if getattr(sim, "energy_drift", None) is not None:
        energy_path = run_dir / "energy_drift.png"
        plot_energy_drift(sim.energy_drift, energy_path, title=f"{title_prefix} — Energy drift" if title_prefix else None)
        saved.append(energy_path)

    return saved


def animate_xy(
    frames,
    out_path: str | Path | None = None,
    interval: int = 20,
    title: str | None = None,
    show: bool = True,
) -> None:
    """
    Simple 2D animation (XY only).

    frames should look like: [ [(x,y,z), ...], [(x,y,z), ...], ... ]
    """
    if not frames:
        raise ValueError("No frames recorded (try --animate and check frame_every).")

    xy = np.array([[(p[0], p[1]) for p in frame] for frame in frames], dtype=float)
    T, N, _ = xy.shape

    # Set view from the first frame so late escapers don't ruin the scale
    x0 = xy[0, :, 0]
    y0 = xy[0, :, 1]
    lim = max(float(np.max(np.abs(x0))), float(np.max(np.abs(y0)))) * 3.0
    if lim <= 0:
        lim = 1.0

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    if title:
        ax.set_title(title)

    sc = ax.scatter(xy[0, :, 0], xy[0, :, 1], s=8, alpha=0.8)

    def update(i):
        sc.set_offsets(xy[i])
        return (sc,)

    anim = FuncAnimation(fig, update, frames=T, interval=interval, blit=True, repeat=False)

    if out_path is not None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        anim.save(out_path)

    if show:
        plt.show()
    else:
        plt.close(fig)