from __future__ import annotations

import math
import json
from pathlib import Path
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter



# Simple plot defaults (keeps plots readable without repeating sizes everywhere)
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

# Visual styles 
BODY_COLOR = "#FFFFFF"    # clean white for bodies (contrasts well with space background)
  
BODY_ALPHA = 1.0       
STAR_COUNT = 450
STAR_ALPHA = 0.6
STAR_SIZE = 1
STAR_SEED = 123


def make_run_dir(outputs_dir: str | Path, scene: str, solver: str, integrator: str, n: int) -> Path:
    """Create a new folder inside outputs/ for this run."""
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"{timestamp}_{scene}_{solver}_{integrator}_N{n}"

    run_dir = outputs_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def save_metadata_json(metadata: dict, filepath: str | Path) -> None:
    """Write metadata to a JSON file (optional)."""
    filepath = Path(filepath)
    with filepath.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def apply_space_style(ax, lim: float, *, hide_axes: bool = True) -> None:
    """Black background + static starfield."""
    ax.figure.set_facecolor("black")
    ax.set_facecolor("black")

    rng = np.random.default_rng(STAR_SEED)
    sx = rng.uniform(-lim, lim, size=STAR_COUNT)
    sy = rng.uniform(-lim, lim, size=STAR_COUNT)
    ax.scatter(
        sx, sy,
        s=STAR_SIZE,
        c="white",
        alpha=STAR_ALPHA,
        linewidths=0,
        zorder=0,
    )

    if hide_axes:
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)


def _robust_lim_from_frames(xy: np.ndarray, *, percentile: float = 99.0, padding: float = 2.0) -> float:
    """Stable camera bounds: robust to a few escapers but avoids edge-clipping."""
    x_all = xy[..., 0].ravel()
    y_all = xy[..., 1].ravel()

    mask = np.isfinite(x_all) & np.isfinite(y_all)
    x_all = x_all[mask]
    y_all = y_all[mask]

    if x_all.size == 0 or y_all.size == 0:
        return 1.0

    r = np.maximum(np.abs(x_all), np.abs(y_all))
    lim = float(np.percentile(r, percentile)) * padding
    if not np.isfinite(lim) or lim <= 0:
        lim = 1.0
    return lim


def plot_final_xy(
    bodies,
    filepath: str | Path,
    title: str | None = None,
    clip_quantile: float | None = None,
) -> None:
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


def save_stepc_outputs(sim, run_dir: Path, title_prefix: str | None = None) -> list[Path]:
    """Save plots for Step C (final XY + energy drift)."""
    saved: list[Path] = []

    final_full = run_dir / "final_xy_full.png"
    plot_final_xy(
        sim.state.bodies,
        final_full,
        title=f"{title_prefix} — Final XY (full)" if title_prefix else None,
    )
    saved.append(final_full)

    final_zoom = run_dir / "final_xy_zoom.png"
    plot_final_xy(
        sim.state.bodies,
        final_zoom,
        title=f"{title_prefix} — Final XY (zoom)" if title_prefix else None,
        clip_quantile=0.95,
    )
    saved.append(final_zoom)

    if getattr(sim, "energy_drift", None) is not None:
        energy_path = run_dir / "energy_drift.png"
        plot_energy_drift(
            sim.energy_drift,
            energy_path,
            title=f"{title_prefix} — Energy drift" if title_prefix else None,
        )
        saved.append(energy_path)

    return saved



def animate_xy(
    frames,
    out_path: str | Path | None = None,
    interval: int = 20,
    title: str | None = None,
    show: bool = True,
    fps: int = 30
) -> Path |None:
    """
    2D animation (XY only), with a built-in space theme.

    frames: [ [(x,y,z), ...], [(x,y,z), ...], ... ]
    """

    if not frames:
        raise ValueError("No frames recorded (try --animate and check frame_every).")

    xy = np.array([[(p[0], p[1]) for p in frame] for frame in frames], dtype=float)
    T, N, _ = xy.shape

    main_xy = xy

    if N <= 5:
        BODY_SIZE = 250        
    elif N <= 50:
        BODY_SIZE = 100
    elif N <= 200:
        BODY_SIZE = 25
    else:
        BODY_SIZE = 10


    lim = _robust_lim_from_frames(xy, percentile=99.0, padding=2.0)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)

    if title:
        ax.set_title(title)

    apply_space_style(ax, lim, hide_axes=True)
    if title:
        ax.title.set_color("white")

    # Main disk particles
    sc = ax.scatter(
        main_xy[0, :, 0], main_xy[0, :, 1],
        s=BODY_SIZE,
        c=BODY_COLOR,
        alpha=1.0,
        linewidths=0,
        zorder=3,
    )

    

    def update(i: int):
        sc.set_offsets(main_xy[i])
        return (sc, )

    anim = FuncAnimation(fig, update, frames=T, interval=interval, blit=True, repeat=False)

    saved = None

    if out_path is not None:
        saved = save_animation(anim, out_path=out_path, fps=fps)

    if show:
        plt.show()
    else:
        plt.close(fig)

    return saved





def save_animation(anim, out_path: str | Path, fps: int = 30):
    """
    Save a matplotlib FuncAnimation to GIF/MP4 depending on extension.

    - .gif uses PillowWriter (pure Python, usually easiest)
    - .mp4 requires ffmpeg which is available on system
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    ext = out_path.suffix.lower()
    if ext == ".gif":
        anim.save(str(out_path), writer=PillowWriter(fps=fps))
        return out_path

    if ext == ".mp4":
        # ffmpeg required
        from matplotlib.animation import FFMpegWriter
        anim.save(str(out_path), writer=FFMpegWriter(fps=fps))
        return out_path

    raise ValueError(f"Unsupported extension '{ext}'. Use .gif or .mp4")