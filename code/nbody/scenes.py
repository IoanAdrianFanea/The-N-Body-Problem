import math
import random
from typing import List

from code.nbody.bodies import Body, G
from code.nbody.physics import compute_kinetic_energy, compute_potential_energy


def two_body(separation: float = 1.0, mass: float = 1.0, v: float | None = None):
    """
    Two bodies set up to orbit each other.

    If v isn't given, I pick a reasonable orbit speed for my units (G = 4*pi^2).
    """
    if v is None:
        v = math.sqrt(G * mass / (2.0 * separation))

    x = separation / 2.0
    return [
        Body(mass, -x, 0.0, 0.0, 0.0, -v, 0.0),
        Body(mass,  x, 0.0, 0.0, 0.0,  v, 0.0),
    ]


def three_body(scale: float = 1.0, mass: float = 1.0) -> List[Body]:
    """
    Figure-eight three-body setup (good for demos).

    The standard values assume G=1, so I scale velocities to match my G.
    """
    vfac = math.sqrt(G)

    # Standard figure-eight initial condition (for G=1)
    x1, y1 = -0.97000436,  0.24308753
    x2, y2 =  0.97000436, -0.24308753
    x3, y3 =  0.0,         0.0

    vx1, vy1 =  0.4662036850,  0.4323657300
    vx2, vy2 =  0.4662036850,  0.4323657300
    vx3, vy3 = -0.9324073700, -0.8647314600

    return [
        Body(mass, scale * x1, scale * y1, 0.0, vfac * vx1, vfac * vy1, 0.0),
        Body(mass, scale * x2, scale * y2, 0.0, vfac * vx2, vfac * vy2, 0.0),
        Body(mass, scale * x3, scale * y3, 0.0, vfac * vx3, vfac * vy3, 0.0),
    ]


def random_cluster(
    n: int,
    seed: int = 0,
    radius: float = 1.0,
    mass_min: float = 1e-3,
    mass_max: float = 1e-2,
    softening: float = 1e-2,
    v_scale: float = 0.05,
    virialize: bool = True,
) -> List[Body]:
    """
    Random cloud of bodies.

    If virialize=True, rescale velocities so it stays roughly bound (more cluster-like).
    """
    rng = random.Random(seed)
    bodies: List[Body] = []

    for _ in range(n):
        x = rng.uniform(-radius, radius)
        y = rng.uniform(-radius, radius)
        z = rng.uniform(-radius, radius)

        vx = rng.uniform(-v_scale, v_scale)
        vy = rng.uniform(-v_scale, v_scale)
        vz = rng.uniform(-v_scale, v_scale)

        m = rng.uniform(mass_min, mass_max)
        bodies.append(Body(m, x, y, z, vx, vy, vz))

    if virialize:
        class _Cfg:
            def __init__(self, softening: float):
                self.softening = softening

        cfg = _Cfg(softening)
        K = compute_kinetic_energy(bodies)
        U = compute_potential_energy(bodies, cfg)

        if K > 0.0 and U != 0.0:
            # Aim for 2K ~= |U| by scaling velocities
            s = math.sqrt(abs(U) / (2.0 * K))
            for b in bodies:
                b.vx *= s
                b.vy *= s
                b.vz *= s

    return bodies


def disk(
    n: int,
    seed: int = 0,
    radius: float = 5.0,
    mass: float = 5e-2,
    v_scale: float = 0.18,
    thickness: float = 0.05,
) -> List[Body]:
    """
    Simple rotating disk for demos.

    Positions start in a flat disk, and velocities are tangential so it spins.
    """
    rng = random.Random(seed)
    bodies: List[Body] = []

    for _ in range(n):
        r = radius * math.sqrt(rng.random())
        theta = rng.uniform(0.0, 2.0 * math.pi)

        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = rng.uniform(-thickness, thickness)

        speed = v_scale / math.sqrt(r + 0.1)
        vx = -speed * math.sin(theta)
        vy =  speed * math.cos(theta)

        bodies.append(Body(mass, x, y, z, vx, vy, 0.0))


    return bodies


def benchmark_cluster(
    n: int = 2500,
    seed: int = 123,
    radius: float = 5.0,
    mass_min: float = 1e-3,
    mass_max: float = 1e-2,
    v_scale: float = 0.06,
    virialize: bool = True,
):
    """
    Large-N cluster intended for performance comparisons.
    Default parameters aim for a roughly bound system (good for stable demos).
    """
    return random_cluster(
        n=n,
        seed=seed,
        radius=radius,
        mass_min=mass_min,
        mass_max=mass_max,
        v_scale=v_scale,
        virialize=virialize,
    )


def list_scenes() -> List[str]:
    return ["two_body", "three_body", "random_cluster", "disk", "benchmark_cluster"]


