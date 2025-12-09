#allows interchangeable solver implementations

class Solver: 
    def accelerations(self, bodies, cfg): #returns the accelerations as a tuple of lists
        raise NotImplementedError()