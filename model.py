# -*- coding: utf-8 -*-
import configparser
import random
import argparse
import matplotlib.pyplot as plt
import os


class model(object):
    """ocean model class"""

    PREDATORS_PROP = u'predators'
    VICTIMS_PROP = u'victims'
    BARRIERS_PROP = u'barriers'
    OCEAN_SIZE_PROP = u'ocean.size'
    REPRODUCTION_FREQ_PROP = u'reproduction.frequency'
    PREDATOR_HUNGER_THRESHOLD_PROP = u'predator.hunger.threshold'
    BASE_CONFIGS_SECTION_NAME = u'base-configs'
    CONFIG_FILEPATH_PARAM = u'c'
    ITERATIONS_PARAM = u'i'
    OUTPATH_PARAM = u'o'

    def __init_ocean(self, predators, victims, barriers):
        ocean_cells = set()
        for i in xrange(self.__ocean_size):
            for j in xrange(self.__ocean_size):
                ocean_cells.add((i, j))

        # select random cells for all 3 types of occupied cells
        selected_cells_count = sum([predators, victims, barriers])
        assert selected_cells_count <= len(ocean_cells)
        selected_cells = random.sample(ocean_cells, selected_cells_count)

        # split random sample
        predator_cells = selected_cells[:predators]
        victim_cells = selected_cells[predators:predators + victims]
        barrier_cells = selected_cells[predators + victims:]

        # init maps
        self.__predator_map.update(zip(predator_cells,
                                       [(0, 0)] * len(predator_cells)))
        self.__victim_map.update(zip(victim_cells,
                                     [0] * len(victim_cells)))
        self.__barrier_map.update(zip(barrier_cells,
                                      [0] * len(barrier_cells)))

    def __init__(self, config=dict()):
        self.__iterations = config[self.ITERATIONS_PARAM]
        self.__outpath = config[self.OUTPATH_PARAM]

        predators = int(config[self.PREDATORS_PROP])
        victims = int(config[self.VICTIMS_PROP])
        barriers = int(config[self.BARRIERS_PROP])

        self.__ocean_size = int(config[self.OCEAN_SIZE_PROP])
        self.__reproduction_freq = int(config[self.REPRODUCTION_FREQ_PROP])
        self.__predator_hunger_threshold = \
            int(config[self.PREDATOR_HUNGER_THRESHOLD_PROP])

        self.__predator_map = dict()
        self.__victim_map = dict()
        self.__barrier_map = dict()
        self.__iterations_info = list()
        self.__init_ocean(predators, victims, barriers)
        self.__current_iteration = 0

    def __reproduce_or_die(self):
        # reproduce and kill predators
        for (x_coord, y_coord) in self.__predator_map.keys():
            (dinner_iteration, reproduce_iteration) = \
                self.__predator_map[(x_coord, y_coord)]
            if (self.__current_iteration - dinner_iteration >=
                    self.__predator_hunger_threshold):
                del self.__predator_map[(x_coord, y_coord)]
            elif (self.__current_iteration - reproduce_iteration >=
                    self.__reproduction_freq):
                free_cells = self.__get_free_neighbours(x_coord, y_coord)
                if len(free_cells) > 0:
                    index = random.randrange(0, len(free_cells))
                    free_cell = free_cells[index]
                    self.__predator_map[(free_cell[0], free_cell[1])] = \
                        (dinner_iteration, self.__current_iteration)

        for (x_coord, y_coord) in self.__victim_map.keys():
            reproduce_iteration = self.__victim_map[(x_coord, y_coord)]
            if (self.__current_iteration - reproduce_iteration >=
                    self.__reproduction_freq):
                free_cells = self.__get_free_neighbours(x_coord, y_coord)
                if len(free_cells) > 0:
                    index = random.randrange(0, len(free_cells))
                    free_cell = free_cells[index]
                    self.__victim_map[(free_cell[0], free_cell[1])] = \
                        self.__current_iteration

    def __check_coord(self, coord):
        if (coord >= 0) & (coord < self.__ocean_size):
            return True
        else:
            return False

    def __is_free(self, x_coord, y_coord):
        if self.__check_coord(x_coord) & self.__check_coord(y_coord):
            key = (x_coord, y_coord)
            return not ((key in self.__predator_map) |
                        (key in self.__victim_map) |
                        (key in self.__barrier_map))
        else:
            return False

    def __is_victim(self, x_coord, y_coord):
        if self.__check_coord(x_coord) & self.__check_coord(y_coord):
            return (x_coord, y_coord) in self.__victim_map
        else:
            return False

    def __get_free_neighbours(self, x_coord, y_coord):
        free_cells = list()
        for dx in xrange(-1, 2):
            for dy in xrange(-1, 2):
                if self.__is_free(x_coord + dx, y_coord + dy):
                    free_cells.append((x_coord + dx, y_coord + dy))
        return free_cells

    def __get_victim_neighbours(self, x_coord, y_coord):
        victim_cells = list()
        for dx in xrange(-1, 2):
            for dy in xrange(-1, 2):
                if self.__is_victim(x_coord + dx, y_coord + dy):
                    victim_cells.append((x_coord + dx, y_coord + dy))
        return victim_cells

    def __make_step(self, x_coord, y_coord):
        free_cells = self.__get_free_neighbours(x_coord, y_coord)
        if len(free_cells) > 0:
            index = random.randrange(0, len(free_cells))
            cell = free_cells[index]
            self.__move(x_coord, y_coord, cell[0], cell[1])

    def __move(self, x_coord, y_coord, dx_coord, dy_coord):
        if (x_coord, y_coord) in self.__predator_map:
            self.__predator_map[(dx_coord, dy_coord)] = \
                self.__predator_map[(x_coord, y_coord)]
            del self.__predator_map[(x_coord, y_coord)]
            if (dx_coord, dy_coord) in self.__victim_map:
                (dinner_iteration, reproduce_iteration) = \
                    self.__predator_map[(dx_coord, dy_coord)]
                self.__predator_map[(dx_coord, dy_coord)] = \
                    (self.__current_iteration, reproduce_iteration)
                del self.__victim_map[(dx_coord, dy_coord)]
        elif (x_coord, y_coord) in self.__victim_map:
            self.__victim_map[(dx_coord, dy_coord)] = \
                self.__victim_map[(x_coord, y_coord)]
            del self.__victim_map[(x_coord, y_coord)]

    def __make_step_or_eat(self, x_coord, y_coord):
        victim_cells = self.__get_victim_neighbours(x_coord, y_coord)
        if len(victim_cells) > 0:
            index = random.randrange(0, len(victim_cells))
            victim_coords = victim_cells[index]
            self.__move(x_coord, y_coord, victim_coords[0], victim_coords[1])
        else:
            free_cells = self.__get_free_neighbours(x_coord, y_coord)
            if len(free_cells) > 0:
                index = random.randrange(0, len(free_cells))
                free_coords = free_cells[index]
                self.__move(x_coord, y_coord, free_coords[0], free_coords[1])

    def __run_iteration(self):
        self.__current_iteration += 1
        for x in xrange(self.__ocean_size):
            for y in xrange(self.__ocean_size):
                    if (x, y) in self.__predator_map:
                        self.__make_step_or_eat(x, y)
                    elif (x, y) in self.__victim_map:
                        self.__make_step(x, y)
                        break

        self.__reproduce_or_die()

    def run(self):
        for iteration in xrange(int(self.__iterations)):
            self.__run_iteration()
            print 'passing ', self.__current_iteration, 'th iteration'
            self.__iterations_info.append((iteration,
                                           len(self.__predator_map),
                                           len(self.__victim_map)))

    def plot(self):
        info = zip(*self.__iterations_info)
        plt.plot(info[0], info[1], 'r')
        plt.show()
        plt.plot(info[0], info[2], 'b')
        plt.show()

    def report(self):
        f = open(self.__outpath, 'w')
        for iteration, predators, victims in self.__iterations_info:
            f.write(unicode(iteration) +
                    '\t' + unicode(predators) +
                    '\t' + unicode(victims) +
                    os.linesep)
        f.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', metavar='path',
                        type=int, help='number of iterations')
    parser.add_argument('-c', metavar='size',
                        type=str, help='config file path')
    parser.add_argument('-o', metavar='depth',
                        type=str, help='results file path')

    params = dict()
    try:
        params = vars(parser.parse_args())
        print params
    except (Exception):
        parser.print_help()

    configPath = params[model.CONFIG_FILEPATH_PARAM]
    for name, value in params.items():
        print name, type(name), value
    configParser = configparser.ConfigParser()
    configParser.read(configPath)
    params.update(configParser.items('base-configs'))

    ocean_model = model(params)
    ocean_model.run()
    ocean_model.report()
    ocean_model.plot()

if __name__ == '__main__':
    main()
