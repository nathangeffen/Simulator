import random
from simulation import simulator
from simulation import simutils

active_tb = simulator.StateName('active tb')
ever_had_tb = simulator.StateName('ever had tb')
alive = simulator.StateName('alive')
dead_with_tb = simulator.StateName('dead with tb')
age = simulator.StateName('age')

class TBState(simulator.State):
    
    @staticmethod
    def ever_had_tb_transition(value,
                               states,
                               individuals,
                               index,
                               parameters): 
        if states[active_tb.key].value:
            return True
        return value
    
    @staticmethod    
    def tb_transition(value,
                      states,
                      individuals,
                      index,
                      parameters): 
    
        if value: # Individual has TB
            if random.random() < parameters['PROBABILITY_TB_CURE']:
                return False
            else:
                return True
        else: # Individual has not got TB
            if random.random() < parameters['PROBABILITY_TB']:
                return True
            else:
                return False
    
    @staticmethod    
    def alive_transition(value,
                         states,
                         individuals,
                         index,
                         parameters):
        if states[active_tb.key].value:
            if random.random() < parameters['PROBABILITY_DEATH_WITH_TB']:
                return False
            else:
                return True
        else:
            if random.random() < parameters['PROBABILITY_DEATH']:
                return False
            else:
                return True

    @staticmethod    
    def dead_with_tb_transition(value,
                                states,
                                individuals,
                                index,
                                parameters):
    
        if states[active_tb.key].value and \
            not states[alive.key].value:
            return True
        return False
    
    @staticmethod
    def age_transition(value,
            states,
            individuals,
            index,
            parameters):
        if states[alive.key]:
            return (value + parameters["AGE_INCREMENT"])   

class TBSimulation(simulator.Simulation):

    simulation_dictionary = \
        {    
         active_tb : 
                    {
                       'value': False, 
                       'transition_function': TBState.tb_transition,
                       'filters' : [(alive, lambda x: x)],
                       'transition_parameters' : {
                            "PROBABILITY_TB_CURE" :  
                                (0.7, simulator.YEAR, simutils.ncp),
                            "PROBABILITY_TB" : 
                                (0.01, simulator.YEAR, simutils.ncp),
                            },
                    },

         ever_had_tb : {
                    'value': False,
                    'transition_function': TBState.ever_had_tb_transition,
                    'filters' : [(alive, lambda x: x), 
                                 (ever_had_tb, lambda x: not x)] 
                    },
         
         alive: { 
                    'value': True, 
                    'transition_function': TBState.alive_transition,
                    'filters' :[(alive, lambda x: x,)],
                    'transition_parameters' : {
                            "PROBABILITY_DEATH" :  
                                (1.0 / 70.0, simulator.YEAR, simutils.ncp),
                            "PROBABILITY_DEATH_WITH_TB" : 
                                (0.03, simulator.YEAR, simutils.ncp),
                            },                    
                    },
         
         dead_with_tb : {
                    'value': False,
                    'transition_function': TBState.dead_with_tb_transition,
                    'filters' : [(dead_with_tb, lambda x: not x,)]
                    },
         age : {
                'value' : lambda: random.randint(0,100),
                'transition_function': TBState.age_transition,
                'filters' : [(alive, lambda x: x)],
                'transition_parameters' : {
                        "AGE_INCREMENT" : 
                            (1, simulator.YEAR, simutils.nlp)
                 }
            }
        }

    analysis_descriptor = \
                (True,
                [(age,      {'filters' : [(alive, lambda x: not x)],
                           'label' : 'average age at death',
                           'type' : int,
                           'calcs' : [simulator.Simulation.mean,]}),
                (active_tb,{'filters' : [(alive, lambda x: x)],
                           'label' : 'alive with tb',
                           'type' : bool,
                           'calcs' : [simulator.Simulation.summation, 
                                      simulator.Simulation.proportion,]
                           }),
                 ],)

    def __init__(self, 
                 population_size=simulator.DEFAULT_POPULATION_SIZE,
                 individual_class=simulator.Individual,
                 state_class=TBState,
                 initial_states=simulation_dictionary,
                 iterations=simulator.DEFAULT_ITERATIONS,
                 analysis_function=None,
                 analysis_descriptor=analysis_descriptor,
                 time_period=simulator.YEAR):

        super().__init__(population_size, 
                         individual_class,
                         state_class,
                         initial_states, 
                         iterations,
                         analysis_function,
                         analysis_descriptor,
                         time_period)

        
if __name__ == '__main__': 

    random.seed(0)
    

    s = TBSimulation(time_period=simulator.MONTH, iterations=70*12)
    print ("Start of simulation: ", "\n", 
               [(k, v) for k, v in s.analyse()[0].items()], "\n",
               [(k, v) for k, v in s.analyse()[1].items()])
    s.simulate()
    print ("End of simulation: ", "\n", 
               [(k, v) for k, v in s.analyse()[0].items()], "\n",
               [(k, v) for k, v in s.analyse()[1].items()])


        
