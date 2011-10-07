import random
import simulator

PROBABILITY_OF_TB = 0.01
PROBABILITY_OF_CURE = 0.7
PROBABILITY_OF_DEATH = 1.0 / 70.0
PROBABILITY_OF_DEATH_WITH_TB = 0.3

def ever_had_tb_transition(value,
                           individuals,
                           index): 
    if individuals[index].states['0000_active_tb'].value:
        return True
    return value

def tb_transition(value,
                  individuals,
                  index, 
                  probability_of_tb=PROBABILITY_OF_TB,
                  probability_of_cure=PROBABILITY_OF_CURE):

    if value: # Individual has TB
        if random.random() < probability_of_cure:
            return False
        else:
            return True
    else: # Individual has not got TB
        if random.random() < probability_of_tb:
            return True
        else:
            return False

def alive_transition(value,
                     individuals,
                     index, 
                     death_without_tb_probability=PROBABILITY_OF_DEATH,
                     death_with_tb_probability=PROBABILITY_OF_DEATH_WITH_TB):
    if individuals[index].states['0000_active_tb'].value:
        if random.random() < death_with_tb_probability:
            return False
        else:
            return True
    else:
        if random.random() < death_without_tb_probability:
            return False
        else:
            return True

def dead_with_tb_transition(value,
                     individuals,
                     index):

    if individuals[index].states['0000_active_tb'].value and \
        not individuals[index].states['0020_alive'].value:
        return True
    return False  

class TBSimulation(simulator.Simulation):

    default_dictionary = \
        {    
        '0000_active_tb': {
                       'value': False, 
                       'transition_function': tb_transition,
                       'filters' : [('0020_alive', lambda x: x)]
                      },

        '0010_ever_tb' : {
                    'value': False,
                    'transition_function': ever_had_tb_transition,
                    'filters' : [('0020_alive', lambda x: x), 
                                 ('0010_ever_tb', lambda x: not x)] 
                    },
         
        '0020_alive': { 
                    'value': True, 
                    'transition_function': alive_transition,
                    'filters' :[('0020_alive', lambda x: x,)]
                    },
         
         '0030_dead_with_tb' : {
                    'value': False,
                    'transition_function': dead_with_tb_transition,
                    'filters' : [('0030_dead_with_tb', lambda x: not x,)]
                    }
         }

    def __init__(self, 
                 population_size=simulator.DEFAULT_POPULATION_SIZE,
                 individual_class=simulator.Individual,
                 state_class=simulator.State,
                 initial_states=default_dictionary,
                 iterations=simulator.DEFAULT_ITERATIONS,
                 analysis_function=None):

        super().__init__(population_size, 
                         individual_class,
                         state_class,
                         initial_states, 
                         iterations,
                         analysis_function)




if __name__ == '__main__': 

    random.seed(0)
    

    s = TBSimulation()
    print ("Start of simulation: ", 
               [(k, v) for k, v in s.analyse().items()])
    s.simulate()
    print ("End of simulation: ", 
               [(k, v) for k, v in s.analyse().items()])


        
