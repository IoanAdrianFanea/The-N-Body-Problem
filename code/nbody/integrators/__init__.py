## this is an interface for different integrators to implement

class Integrator:

    #step(snapshot_of_universe, simulation_settings, function_that_computes_acceleration) 

    def step(self, state, cfg, accel_fn):

        raise NotImplementedError() #raisies error if called directly and not by subclass
    



    #: is used to describe what the variable should be (only hint) i.e. method(x: int, y: str):
    # -> it indicates the return type of the function (only hint) i.e. method(x,y) -> list: