
## Contains class for body and a SystemState used to store a list of bodies 


from typing import List
import math

# Gravitational constant in AU^3 / (M_sun * yr^2)
G = 4 * (math.pi)**2


class Body:
    def __init__(self, m, x, y, z= 0.0, vx=0.0, vy=0.0, vz=0.0):
        self.m = m     # mass
        self.x = x     # position x
        self.y = y     # position y
        self.z = z
        self.vx = vx   # velocity x
        self.vy = vy   # velocity y
        self.vz = vz  # velocity z

    def squareDist(self, other):
        return (self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2

    def __str__(self):
        return f"Body({self.m},{self.x},{self.y},{self.z},{self.vx},{self.vy},{self.vz})"

    def __repr__(self):
        return str(self)

    def asTuple(self):
        return (self.m, self.x, self.y, self.z, self.vx, self.vy, self.vz)


class SystemState:

    def __init__(self, bodies: List[Body], accel=None):
        self.bodies = bodies
        # accel is (ax, ay, az) computed at these bodies positions
        self.accel = accel

    def copy(self):
        # deep copy of system state
        new_state = SystemState([
            Body(b.m, b.x, b.y, b.z, b.vx, b.vy, b.vz)
            for b in self.bodies
        ])
        if self.accel is not None: 
            ax, ay, az = self.accel
            new_state.accel = (ax[:], ay[:], az[:])
        return new_state