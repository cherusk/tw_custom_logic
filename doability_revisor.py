#!/usr/bin/env python

import argparse
import os
import yaml
import json
import collections as c
from collections import defaultdict
from ascii_graph import Pyasciigraph
import sys


LOGIC_RESIDE = os.path.dirname(__file__)
CNFG_DIR = os.path.join(LOGIC_RESIDE, 'cnfg')


class Depictor:

    def __init__(self):
        pass

    def conjure(self, scenario):
        label = "Scenario (durations in weeks)"

        data = [tuple([k, v]) for k, v in
                sorted(scenario.items(), key=lambda v: v[1])]

        graph = Pyasciigraph(
                             line_length=100,
                             min_graph_length=50,
                             separator_length=10,
                             multivalue=False,
                             human_readable='si',
                             graphsymbol="*",
                             float_format='{0:,.0f}')

        for line in graph.graph(label=label, data=data):
            print(line)

class Revisor():

    folded_projects = defaultdict(int)

    def __init__(self, cnfg, tasks):
        self._cnfg = cnfg['root']
        self.effort_uda = self._cnfg['uda_name']
        self.accrue_per_project(tasks)
        self.perform()

    def accrue_per_project(self, tasks):
        for task in tasks:
            project = task['project']
            self.folded_projects[project] = sum((self.folded_projects[project],
                                                task[self.effort_uda]))

    def perform(self):
        scenario = {}
        capacity = self._cnfg['week_capacity']

        for project, chunking in self._cnfg['chunking_scenario']['projects'].items():
            capacity -= chunking

            if capacity >= 0:
                pass
            else:
                cease(rc=1, msg="exceeding capacity")

            effort = self.folded_projects[project]
            duration = (effort / chunking) + (effort % chunking)
            scenario[project] = duration

        return scenario

def setup_args():
    parser = argparse.ArgumentParser(description="Assisiting logic for bulk assessing timewise \
                                                  projections and approach scenario election.")
    parser.add_argument('-t', '--tasks', help="exported tasks file")
    parser.add_argument('-p', '--param_file', help="parameter cnfg file")
    args = parser.parse_args()
    return args


def load(_file, logic=None):
    with open(_file, "r") as fp:
        return logic(fp)

def cease(rc=0, msg=""):
    print(msg)
    sys.exit(rc)

def run():
    args = setup_args()
    cnfg = load(os.path.join(CNFG_DIR, 'param.yml'),
                logic=yaml.load)
    tasks = load(args.tasks,
                 logic=json.load)

    scenario = Revisor(cnfg, tasks).perform()
    Depictor().conjure(scenario)

if __name__ == "__main__":
    run()
