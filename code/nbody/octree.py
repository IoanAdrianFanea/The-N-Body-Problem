from code.nbody.bodies import Body

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
            
        self._update_mass_and_com(body_to_insert)