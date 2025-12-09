
## This computes the gravitational accelerations on each body due to all others (further physics added here)


import math
from typing import List
from nbody.bodies import Body, G


def compute_accelerations(bodies: List[Body]): #called in solvers

    N = len(bodies)
    ax = [0.0] * N
    ay = [0.0] * N

    for i in range(N):
        bi = bodies[i]
        for j in range(N):
            if i == j:
                continue

            bj = bodies[j]
            dx = bj.x - bi.x
            dy = bj.y - bi.y
            dist2 = dx*dx + dy*dy

            # dist^{3/2} = (dist^2)^(3/2)
            dist32 = dist2 ** 1.5

            ax[i] += dx * bj.m * G / dist32
            ay[i] += dy * bj.m * G / dist32

    return ax, ay