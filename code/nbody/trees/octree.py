from code.nbody.bodies import Body
from code.nbody.bodies import G
import math

class OctreeNode:
    def __init__(self, center, half_size):
        self.total_mass = 0.0
        self.center_of_mass = (0.0, 0.0, 0.0)
        self.half_size = half_size
        self.center = center    
        self.body = None
        self.children = None 


    def insert(self, body_to_insert: Body):
        if self.body is None and self.children is None:
            self.body = body_to_insert

        elif self.children is None and self.body is not None:
            self.subdivide()
            temp = self.body
            self.body = None
            self._insert_into_child(temp)
            self._insert_into_child(body_to_insert)

        else:
            position = self.cube_to_insert(body_to_insert)
            self.children[position].insert(body_to_insert)
            
        self._update_mass_and_com(body_to_insert) #this runs once per visit of node


    def subdivide(self): #remember that this breaks when body has same position as another
        quarter = self.half_size / 2
        offsets = [(-quarter, -quarter, -quarter), (quarter, -quarter, -quarter),
                   (-quarter, quarter, -quarter), (quarter, quarter, -quarter),
                   (-quarter, -quarter, quarter), (quarter, -quarter, quarter),
                   (-quarter, quarter, quarter), (quarter, quarter, quarter)]
        
        self.children = []
        for dx, dy, dz in offsets:
            new_center = (self.center[0] + dx,
                          self.center[1] + dy,
                          self.center[2] + dz)
            self.children.append(OctreeNode(new_center, quarter))


    def cube_to_insert(self, body: Body):
        index = 0
        if body.x >= self.center[0]:
            index |= 1
        if body.y >= self.center[1]:
            index |= 2
        if body.z >= self.center[2]:
            index |= 4
        return index
    
    def _insert_into_child(self, body: Body):
        position = self.cube_to_insert(body)
        self.children[position].insert(body)


    def _update_mass_and_com(self, body: Body):
        m = body.m
        x, y, z = body.x, body.y, body.z

        M = self.total_mass

        if M == 0.0:
            self.center_of_mass = (x, y, z)
            self.total_mass = m
        else:
            new_M = M + m
            cx, cy, cz = self.center_of_mass

            self.center_of_mass = (
                (cx * M + x * m) / new_M,
                (cy * M + y * m) / new_M,
                (cz * M + z * m) / new_M,
            )
            self.total_mass = new_M


    def compute_accelerations(self, body: Body, theta: float, softening: float):
        total_mass = self.total_mass
        children = self.children

        if total_mass == 0.0 or (self.body is body and children is None):
            return (0.0, 0.0, 0.0)

        bx, by, bz = body.x, body.y, body.z
        cx, cy, cz = self.center_of_mass

        dx = cx - bx
        dy = cy - by
        dz = cz - bz

        soft2 = softening * softening
        dist2 = dx*dx + dy*dy + dz*dz + soft2
        if dist2 == 0.0:
            return (0.0, 0.0, 0.0)

        sqrt = math.sqrt
        dist = sqrt(dist2)

        s = self.half_size * 2.0

        if children is None or (s / dist) < theta:
            inv_dist = 1.0 / dist
            inv_dist3 = inv_dist / dist2
            factor = G * total_mass * inv_dist3
            return (factor * dx, factor * dy, factor * dz)

        ax = ay = az = 0.0
        for child in children:
            if child.total_mass > 0.0:
                cax, cay, caz = child.compute_accelerations(body, theta, softening)
                ax += cax
                ay += cay
                az += caz

        return (ax, ay, az)


        
