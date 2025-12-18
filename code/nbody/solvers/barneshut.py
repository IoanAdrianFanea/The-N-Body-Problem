from code.nbody.solvers import Solver
from code.nbody.trees.octree import OctreeNode


class BarnesHutSolver(Solver):
    def __init__(self, theta=0.7):
        self.theta = theta

    def accelerations(self, bodies, cfg):
        N = len(bodies)

        ax = [0.0] * N
        ay = [0.0] * N
        az = [0.0] * N

        xs = [b.x for b in bodies] #build the bounding octree cube, used to caclulate center and size
        ys = [b.y for b in bodies]
        zs = [b.z for b in bodies]

        cx = 0.5 * (min(xs) + max(xs)) #calculate the center 
        cy = 0.5 * (min(ys) + max(ys))
        cz = 0.5 * (min(zs) + max(zs))

        size = max(  # calculate the size of the cube
            max(xs) - min(xs),
            max(ys) - min(ys),
            max(zs) - min(zs),
        )

        half_size = 0.5 * size + 1e-10  # small padding to avoid zero size

        root = OctreeNode((cx, cy, cz), half_size) #initial octree node

        for b in bodies: 
            root.insert(b)

        for i, b in enumerate(bodies):
            ax[i], ay[i], az[i] = root.compute_accelerations(
                b, self.theta, cfg.softening
            )

        return ax, ay, az