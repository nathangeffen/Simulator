#!/usr/bin/env python

import random
from math import exp, log

MINUTE = 1
HOUR = 60
DAY = 24*HOUR
MONTH =(365.25/12)*DAY 
YEAR = 365.25*DAY

DEFAULT_POPULATION_SIZE = 10000
DEFAULT_SIMULATIONS = 10
DEFAULT_ITERATIONS = 70

def state_incrementor():
    counter = -1
    while True:
        counter += 1
        yield counter

state_increment = state_incrementor().__next__ 

class StateName:
    
    def __init__(self, label): 
        self._index = state_increment()
        self._label = label

    def get_index(self):
        return self._index

    def get_label(self):
        return self._label

    def get_key(self):
        return (self._index, self)
            
    index = property(get_index)
    label = property(get_label)
    key = property(get_key)

def passes_filters(states, filters):
    for _filter in filters:
        if not _filter[1](states[_filter[0].key].value):
            return False
    return True
    

class State:    
    
    def __init__(self, 
                 value, transition_function=None, 
                 filters=[], 
                 parameters={}):
        
        import types 
        
        if isinstance(value, types.FunctionType):
            self.value = value()
        else:
            self.value = value
        
        if not transition_function:
            self.transition_function = State.default_transition_function
        else:
            self.transition_function = transition_function
        self.filters = filters
        self.parameters = parameters

    def passes_filters(self, states):
        return passes_filters(states, self.filters)
    
    def transition(self, individuals, index):
        if self.passes_filters(individuals[index].states):        
            self.value = self.transition_function(self.value, 
                                                  individuals[index].states,
                                                  individuals, 
                                                  index,
                                                  self.parameters)

    @staticmethod
    def default_transition_function(value,
                                    states, 
                                    individuals,   
                                    index,
                                    parameters): # index of this state's individual
        if value:
            if random.random() < \
                parameters['TRANSITION_BACK_PROBABILITY']:
                return False
            else:
                return True
        else:
            if random.random() < \
                parameters['TRANSITION_PROBABILITY']:
                return True
            else:
                return False
            
    def __str__(self):
        return str(self.value)

class Individual:

    def __init__(self, 
                 state_class=State,
                 initial_states={}):
        self.states = {}
        for state_descriptor in initial_states.items():
            self.add_state(state_descriptor)

    def add_state(self, state):
        try: 
            filters = state[1]['filters']
        except KeyError: 
            filters=[]
            
        self.states[state[0].key] = State(state[1]['value'],
                                          state[1]['transition_function'], 
                                          filters,
                                          state[1] \
                                          ['normalised_transition_parameters'])

    
    def process_iteration(self, individuals, index):
        for state in self.states.values():
            state.transition(individuals, index)

    def __str__(self):
        output = ''
        for state in self.states.values():
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
        
    def __init__(self, 
                 population_size=DEFAULT_POPULATION_SIZE,
                 individual_class=Individual,
                 state_class=State,
                 initial_states={},
                 iterations=DEFAULT_ITERATIONS,
                 analysis_function=None,
                 analysis_descriptor=(True, []),
                 time_period=YEAR):
        
        self.default_state = StateName('default')
        
        try:
            self.simulation_dictionary
        except:
            self.simulation_dictionary = {self.default_state : {
                                'value': False, 
                                'transition_function': None,
                                'filters' : [],
                                'transition_parameters' : {
                                        "TRANSITION_PROBABILITY" : 
                                            (0.009, YEAR),
                                        "TRANSITION_BACK_PROBABILITY" : 
                                            (0.7, YEAR),        
                                        },
                                },
                        }
                                      
        self.population_size = population_size
        self.iterations = iterations
                             
        if initial_states:
            self.initial_states = initial_states
        else:
            self.initial_states = self.simulation_dictionary

        self.time_period = time_period
        for state in self.simulation_dictionary.values():
            try:
                state['normalised_transition_parameters'] = self._normalise(
                                                state['transition_parameters'])
            except KeyError:
                state['normalised_transition_parameters'] = {}
            
        self.population = [individual_class(state_class, self.initial_states)
                      for i in range(0,population_size)]

        if not analysis_function:
            self.analyse = self.default_analysis_function
        
        self.analysis_descriptor = analysis_descriptor


    def _normalise(self, parameters):
        parameter_dict = {}
        for parameter in parameters.items():
            time_period_from = parameter[1][1]
            if time_period_from != self.time_period:
                print("HERE: ", time_period_from, self.time_period)
                time_period_to = self.time_period
                n = time_period_from / time_period_to
                c = parameter[1][0] + 1.0 
                # x^n = c ; we must solve for x
                # n*ln(x) = ln(c)
                # ln(x) = ln(c)/n
                # x = exp(ln(c)/n)   
                # Finally subtract the 1 that was added in the previous statement 
                parameter_dict[parameter[0]] = exp(log(c)/n) - 1
            else:
                print("NO HERE: ", time_period_from, self.time_period)
                parameter_dict[parameter[0]] = parameter[1][0] 
            print ("DEBUG: ", parameter, parameter_dict[parameter[0]])
        return parameter_dict

    def add_state(self, *args, **kwargs):
        for individual in self.population:
            state_index = individual.add_state(self, args, kwargs)
        return state_index
             
    def simulate(self):
        for i in range(0,self.iterations):
            for individual in range(0,self.population_size):
                self.population[individual]. \
                    process_iteration(self.population, 
                                            individual)
                                            

    @staticmethod
    def summation(values):
        return ("sum", sum(values))

    @staticmethod
    def proportion(values):
        return ("proportion", 
                len(list(filter(lambda x: x, values))) / len(values))
        
    @staticmethod
    def mean(values):
        return ("mean", 
                sum(values) / len(values) )
    
    @staticmethod
    def median(values):
        values = sorted(values)
        length = len(values)
        
        if length == 0:
            raise ValueError("median() arg is an empty sequence")
        elif length == 1:
            output = values[0]
        elif length % 2 == 0:
            output = (values[length//2] + values[length//2+1]) / 2
        else:
            output = values[length // 2 + 1]
        return ("median", output)
        
    def _default_analysis(self):

        # Creates a dictionary with state names as the key

        output = {}

        # Sum the states set to true for every state and insert in dictionary
        for individual in self.population:
            for state in individual.states.items():
                value = state[1].value
                if type(value)==bool:
                    if value:
                        output[state[0][1].label] = \
                            output.get(state[0][1].label, 0) + 1
                else: 
                    output[state[0][1].label] = \
                            output.get(state[0][1].label, 0) + value
                
        output['population']  = len(self.population)
        return output
        

    def _specialised_analysis(self):
        analysis = {}
        for descriptor in self.analysis_descriptor[1]:
            filtered_values = [individual.states[descriptor[0].key].value 
                             for individual in 
                             filter(lambda individual: 
                                   passes_filters(individual.states, 
                                                descriptor[1]['filters']), 
                                   self.population)]
            for calculation in descriptor[1]['calcs']:
                if len(filtered_values):
                    calc  = calculation(filtered_values)
                    analysis[descriptor[1]['label'] + ':' + calc[0]] = calc[1] 
                
        return analysis


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

        if (self.analysis_descriptor[0]):            
            default_output = self._default_analysis()
        else:
            default_output = {}

        if (self.analysis_descriptor[1]):
            calculated_output = self._specialised_analysis()
        else:
            calculated_output = {}
        
        return (default_output, calculated_output)

if __name__ == '__main__': 
    
    #default_simulations = DEFAULT_SIMULATIONS

    random.seed(0)
    

    s = Simulation(time_period=MONTH, iterations=70*12)
    print ("Start of simulation: ", "\n", 
               [(k, v) for k, v in s.analyse()[0].items()], "\n",
               [(k, v) for k, v in s.analyse()[1].items()])
    s.simulate()
    print ("End of simulation: ", "\n", 
               [(k, v) for k, v in s.analyse()[0].items()], "\n",
               [(k, v) for k, v in s.analyse()[1].items()])


        
