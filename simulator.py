#!/usr/bin/env python

import random

DEFAULT_POPULATION_SIZE = 10000
DEFAULT_SIMULATIONS = 10
DEFAULT_ITERATIONS = 70
DEFAULT_TRANSITION_PROBABILITY = 0.009
DEFAULT_TRANSITION_BACK_PROBABILITY = 0.7

def default_transition_function(value, 
                                individuals,   
                                index, # index of this state's individual 
                                transition_probability=
                                    DEFAULT_TRANSITION_PROBABILITY,
                                transition_back_probability=
                                    DEFAULT_TRANSITION_BACK_PROBABILITY):

    if value:
        if random.random() < transition_back_probability:
            return False
        else:
            return True
    else:
        if random.random() < transition_probability:
            return True
        else:
            return False




class State:    
    
    def __init__(self, value, transition_function=None, filters=[]):
        self.value = value
        
        if not transition_function:
            self.transition_function = default_transition_function
        else:
            self.transition_function = transition_function
        self.filters = filters

    def passes_filters(self, states):
        for _filter in self.filters:
            if not _filter[1](states[_filter[0]].value):
                return False
        return True
    
    def transition(self, individuals, index):
        if self.passes_filters(individuals[index].states):        
            self.value = self.transition_function(self.value, individuals, index)
            
    def __str__(self):
        return str(self.value)

class Individual:

    def __init__(self, 
                 state_class=State,
                 initial_states={'default' : {
                                              'value': 0, 
                                              'transition_function': None,
                                              'filters' : [] }
                                              },
                 ):

        self.states = {}
        for state in initial_states.items():
            self.states[state[0]] = State(state[1]['value'],
                                          state[1]['transition_function'], 
                                          state[1]['filters'])

    def process_iteration(self, individuals, index):
        for state in self.states.values():
            state.transition(individuals, index)

    def __str__(self):
        output = ''
        for state in self.states:
            output += str(state) + ' '
        return output


class Simulation:
    ''' This is the base class controlling simulations. This class itself only
    performs a very simple simulation. It is almost always its children and not 
    this class itself that are instantiated.

    A simulation consists of a population of individuals, each containing 
    multiple states.
        
    The simulate method iterates over the population a specified number of 
    times. On each iteration it processes all the individuals, updating their 
    states  according to specified state functions.
    '''
    
    default_dictionary = {'default': {
                                'value': 0, 
                                'transition_function': None,
                                 'filters' : [] },
                          }
                          
    
    
    def __init__(self, 
                 population_size=DEFAULT_POPULATION_SIZE,
                 individual_class=Individual,
                 state_class=State,
                 initial_states=default_dictionary,
                 iterations=DEFAULT_ITERATIONS,
                 analysis_function=None):

        self.population_size = population_size
        self.iterations = iterations                     
        self.initial_states = initial_states
        self.population = [individual_class(state_class, self.initial_states)
                      for i in range(0,population_size)]

        if not analysis_function:
            self.analyse = self.default_analysis_function

    def simulate(self):
        for i in range(0,self.iterations):
            for individual in range(0,self.population_size):
                self.population[individual].process_iteration(self.population, 
                                                              individual)

    def default_analysis_function(self):
        '''This simple analysis function counts the number of individuals in 
        a population in each state. It returns a dictionary containing 
        the number of people in each state.
        
        For example, if there is a state called "tb" which is either true or 
        false, it counts the number of individuals set to true and inserts this
        into the dictionary.
        
        An example of the output could be:
        {'tb': 537, 'HIV': 271, 'AIDS': 31} 
        
        '''

        # Creates a dictionary with state names as the key
        
        output = {}

        # Sum the states set to true for every state and insert in dictionary
        for individual in self.population:
            for state in individual.states.items():
                if state[1].value:
                    output[state[0]] = output.get(state[0], 0) + 1
                
        output['population']  = len(self.population)

        return output

if __name__ == '__main__': 
    
    #default_simulations = DEFAULT_SIMULATIONS

    random.seed(0)
    

    s = Simulation()
    print ("Start of simulation: ",
            [(k, v) for k, v in s.analyse().items()])
    s.simulate()
    print ("End of simulation: ", 
            [(k, v) for k, v in s.analyse().items()])
