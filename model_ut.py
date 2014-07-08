# -*- coding: utf-8 -*-
import unittest
from model import model


class test_model(unittest.TestCase):
    """simple tests for ocean model"""

    def setUp(self):
        self.__params = \
            {model.ITERATIONS_PARAM: 1000,
             model.CONFIG_FILEPATH_PARAM: 'config.txt',
             model.OUTPATH_PARAM: 'result.txt'}

    def test_model_generation(self):
        print 'testing model generation...'
        # make sure the shuffled sequence does not lose any elements
        params = {model.ITERATIONS_PARAM: 1000,
                  model.CONFIG_FILEPATH_PARAM: 'config.txt',
                  model.OUTPATH_PARAM: 'result.txt',
                  model.PREDATORS_PROP: 100,
                  model.VICTIMS_PROP: 0, model.BARRIERS_PROP: 0,
                  model.OCEAN_SIZE_PROP: 100,
                  model.PREDATOR_HUNGER_THRESHOLD_PROP: 11,
                  model.REPRODUCTION_FREQ_PROP: 10}
        ocean_model = model(params)
        predators = params[model.PREDATORS_PROP]
        victims = params[model.VICTIMS_PROP]
        barriers = params[model.BARRIERS_PROP]
        predators_map = ocean_model._model__predator_map
        victims_map = ocean_model._model__victim_map
        barriers_map = ocean_model._model__barrier_map
        self.assertEqual(len(predators_map), predators)
        self.assertEqual(len(victims_map), victims)
        self.assertEqual(len(barriers_map), barriers)

    # testing predators lifecycle
    def test_check_predators_lifecycle(self):
        print 'testing predators...'
        params = {model.ITERATIONS_PARAM: 1000,
                  model.CONFIG_FILEPATH_PARAM: 'config.txt',
                  model.OUTPATH_PARAM: 'result.txt',
                  model.PREDATORS_PROP: 100,
                  model.VICTIMS_PROP: 0,
                  model.BARRIERS_PROP: 0,
                  model.OCEAN_SIZE_PROP: 100,
                  model.PREDATOR_HUNGER_THRESHOLD_PROP: 11,
                  model.REPRODUCTION_FREQ_PROP: 10}
        ocean_model = model(params)
        self.assertEqual(len(ocean_model._model__predator_map), 100)
        for i in xrange(9):
            ocean_model._model__run_iteration()
        self.assertEqual(len(ocean_model._model__predator_map), 100)
        ocean_model._model__run_iteration()
        self.assertEqual(len(ocean_model._model__predator_map), 200)
        ocean_model._model__run_iteration()
        self.assertEqual(len(ocean_model._model__predator_map), 0)

    def test_check_victims_lifecycle(self):
        print 'testing victims...'
        params = {model.ITERATIONS_PARAM: 1000,
                  model.CONFIG_FILEPATH_PARAM: 'config.txt',
                  model.OUTPATH_PARAM: 'result.txt',
                  model.PREDATORS_PROP: 0,
                  model.VICTIMS_PROP: 100,
                  model.BARRIERS_PROP: 0,
                  model.OCEAN_SIZE_PROP: 100,
                  model.PREDATOR_HUNGER_THRESHOLD_PROP: 0,
                  model.REPRODUCTION_FREQ_PROP: 10}
        ocean_model = model(params)
        self.assertEqual(len(ocean_model._model__victim_map), 100)
        for i in xrange(9):
            ocean_model._model__run_iteration()
        self.assertEqual(len(ocean_model._model__victim_map), 100)
        ocean_model._model__run_iteration()
        self.assertEqual(len(ocean_model._model__victim_map), 200)

if __name__ == '__main__':
    unittest.main()
