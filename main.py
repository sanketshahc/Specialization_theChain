import gerrychain
import geopandas
import pandas as pd
import json
import networkx
import matplotlib.pyplot as plt
import random
import dictionary
import numpy as np
import csv

# THE MEAT
#####################
# Import Data

# brining in 69 columns ehre, incdluding geometry column
# Data = geopandas.read_file("./nyc_shapes/gerrychain_blocks.shp")
# Data = geopandas.read_file("./PA-shapefiles/PA.shp")
Data = geopandas.read_file("./acs_blocks_water/acs_blocks_water.shp")
dg = gerrychain.Graph.from_geodataframe(Data)
# The Dual Graph. Nodes are districts, whose edges are bordering districts. think of one part of
# the dual graph as a conventional map, where the face between lines are districts, and nodes are
# the corners...the other part of the dual is when nodes are the center of the district,
# and edges connect to centers of other districts...

asgn = Data["COUNCIL_D"]
labels = Data.select_dtypes(include=['int','float']).columns.values.tolist()
# labels.remove("geometry")
# Assignment Dict
# maps node ids / (census blocks) to voting districts..
# todo fix this.

# VALIDATORS AND UPDATORS
################################
# each is a list / dictionary (list of validators, dict of updators) that is evaluated every
# partition state (chain iteration). There are builtins of each, but can also write
# custom...validators are like boolean checks, updators are like studies of whatever we're
# analyzing for each proposal....Updaters Dict. The updators return directly to the partition
# object, and that is where the data can be accessed later, if needed. Additionally, it can be
# written to a file as well. take partition as input....accessible later through partition[
# "label"]. Validators are like the policy, updators are like the evaluation or metric of
# success/study.

## Pop by Race Studies
## Flagging concentrated wealth or poverty....need overal median income, median per district (per
# block)
## num hood cuts per state.

# partition_updaters = {
#     # "population": gerrychain.updaters.Tally("VAP", "population", dtype=int),
#     # "black_pop": gerrychain.updaters.Tally("BVAP", "black_pop", dtype=int),
#     # "asian_pop": gerrychain.updaters.Tally("ASIANVAP", "asian_pop", dtype=int),
#     # "white_pop": gerrychain.updaters.Tally("WVAP", "white_pop", dtype=int),
#     # "hisp_pop": gerrychain.updaters.Tally("HVAP", "hisp_pop", dtype=int),
#     # "amin_pop": gerrychain.updaters.Tally("AMINVAP", "amin_pop", dtype=int),
#     # "hp_pop": gerrychain.updaters.Tally("NHPIVAP", "hp_pop", dtype=int),
#     # "other_pop": gerrychain.updaters.Tally("OTHERVAP", "other_pop", dtype=int)
# }

special = ['MED_HH_INC', 'MDRENT_TOT', 'MED_VALUE', 'MED_AGE',
'MED_AGE_M','MED_AGE_F','COMM_D']

partition_updaters = {

}

def mean_calcs(part):
    results = {}
    for key,value in gerrychain.updaters.Tally(label, label, dtype=float)(part).items():
        results.update({key:value/51})
    return results

for label in labels:
    if label not in special:
        partition_updaters.update({label: gerrychain.updaters.Tally(label, label, dtype=float)})
    elif label == "COMM_D":
        partition_updaters.update({label: gerrychain.updaters.county_splits(
            "COUNCIL_D","COMM_D")})
    else:
        # print(label)
        partition_updaters.update(
            {label: mean_calcs}
        )

# todo median of medians instead?
# todo, number of plurality districts per race.
# Ideal Pop Object (in initial state)
pop_tot = {
    "TOTAL10": gerrychain.updaters.Tally("TOTAL10", "TOTAL10", dtype=int),
}
pop_partition_object = gerrychain.partition.Partition(
    dg, asgn, pop_tot
)

# dummy validator (everything is valid)
def dummy(c):
    print(c)
    return True
# another constrin can be contiguity.
# contiguous = gerrychain.constraints.single_flip_contiguous
visible = gerrychain.constraints.no_vanishing_districts
within = gerrychain.constraints.within_percent_of_ideal_population(
    pop_partition_object, .25,pop_key = "TOTAL10")
# todo compactness, builtin, must us geographic partition tpe object.
# todo, neighborhood splits

# lis of bool fnns
valid = gerrychain.constraints.Validator([visible, within])


# PARTITION, PROPOSAL, AND CHAIN
#################################

# Pulling COPY of PROPOSAL fn in directly Because weird bug
def propose_random_flip(partition):
    """Proposes a random boundary flip from the partition.

    :param partition: The current partition to propose a flip from.
    :return: a proposed next `~gerrychain.Partition`
    """
    if len(partition["cut_edges"]) == 0:
        return partition
    edge = random.choice(tuple(partition["cut_edges"]))
    index = random.choice((0, 1))
    flipped_node, other_node = edge[index], edge[1 - index]
    flip = {flipped_node: partition.assignment[other_node]}
    return partition.flip(flip)


# Partition Object (in initial state)
partition_object = gerrychain.partition.Partition(
    dg, asgn, partition_updaters
)

# Markov Object
chain = gerrychain.MarkovChain(
    propose_random_flip,
    valid,
    lambda x: True,
    partition_object,
    1000
)

# notes: the proposal function defines how to step through a chain's 'links', which are the states
# of the partition object. the partition object's state is entirely defined by the
# assignmnet dictionary, which is what is modulated by the proposal function, in effect. The
# favored proposal mechanism is boundary flips, although other techniques such as merge and
# splits can also be used....the updaters are essentially what 'is being studied', whereas the
# validators/constraints/acceptance criteria are checks on each chain state. Acceptance criteria
# is only distinct from validation constraints when using Metropolis Hastings.

# note that in this example we are both writing to file as well as partition object...however,
# in practice would prop only use one....

# no the updaters are only storing per state, so whatever they tabulate gets removed with each new
# step....so the loop strips out the updator outptu each step....
threshold = .15  # for threshold count
# populations_race = open('./outputs/populations_by_race.csv', "a")
# pluralities_race = open('./outputs/pluralities_by_race.csv', "a")
# threshold_race = open('./outputs/threshold_by_race.csv', "a")
master_tally = open('./outputs/master_tally.csv',"a")
# comm_tally = open('./outputs/comm_tally.csv',"a")
# desired_columns = [
#     'population', 'black_pop', 'asian_pop', 'white_pop', 'hisp_pop', 'amin_pop', 'hp_pop',
#     'other_pop'
# ]

# initiate with index names (multi index)
# Initial State, empty table
# NOTE: updater fns not functioning....gerychain bug?
# names = ['Chain-State', 'District']
# for name, _ in partition_object.updaters.items():
#     # updater functions not longer working,
#     # so calling them manually!
#     if name in desired_columns:
#         names.append(name)
names = ['chain-State', 'district'] + labels

# names_pops = names.copy()
# names_pops.remove('population')
# race_table = (
#     pd.DataFrame(columns=names_pops)
#         .set_index(['Chain-State', 'District'])
# )
master_table = (
    pd.DataFrame(columns=names)
        .set_index(['chain-State', 'district'])
)
# comm_table = (
#     pd.DataFrame(columns=['chain-State', 'comm','split', 'nodes', 'districts'])
#         .set_index(['chain-State', 'comm'])
# )

# names_stats = names.copy()
# names_stats.remove('District')
# # names_stats.remove('population')
# plurality_table = (
#     pd.DataFrame(columns=names_stats)
#         .set_index(['Chain-State'])
# )
# threshold_table = (
#     pd.DataFrame(columns=names_stats)
#         .set_index(['Chain-State'])
# )
master_table.to_csv(master_tally)
# comm_table.to_csv(comm_tally)

# race_table.to_csv(populations_race)
# plurality_table.to_csv(pluralities_race, index = False)
# threshold_table.to_csv(threshold_race, index = False)


k=0
for state in chain:
    k += 1
    concat_this = []
    print(k)
    if k % 500 == 0:
        print(f" {500 * k} flips, computing stats") if k % 5000 == 0 else None
        for name, fn in state.updaters.items(): # change to dict
            if name in names:
                # print(name)
                # updater functions no longer working,
                # so calling them manually!
                if name == "COMM_D":
                    continue
                    # com = pd.DataFrame(fn(state)).transpose()
                    # magical bug that disappears the updater results, also prevents the
                    # count_split function from running....since it references it's parents
                    # property...which doesn't exist....so will have to manually write the
                    # function....
                else:
                    x = fn(state)
                    col = (
                        pd.DataFrame(x.values(), index=x.keys())
                            .sort_index()
                            .rename(columns={0: name})
                    )
                    concat_this.append(col)

        _table = pd.concat(concat_this, axis=1)
        _table = _table.set_index(
            [
                pd.Index([(k/500) for _ in range(51)]),
                _table.index
            ]
        )
        # com = com.set_index(
        #     [
        #         pd.Index([(k / 500) for _ in range(51)]),
        #         com.index
        #     ]
        # )
        # comm_table = pd.concat([comm_table, com])
        master_table = pd.concat([master_table, _table])
        # _totals = pd.DataFrame(_table['population'])
        # _table = _table.drop('population', axis=1)
        # percent_table = (_table / _totals.values)
        # plurality_counts = (pd.DataFrame(
        #     pd.value_counts(
        #         percent_table.idxmax(axis=1),
        #         dropna=False # not working....keeps on dropping nans...
        #     )).transpose() )
        # plurality_counts.fillna(0, inplace=True)
        # threshold_counts = pd.DataFrame(
        #     (percent_table > threshold).sum()
        # )
        # threshold_counts = threshold_counts.transpose()
        # race_table = pd.concat([race_table, percent_table])
        # plurality_table = (
        #     pd.concat([plurality_table, plurality_counts], ignore_index=True)
        # )
        # threshold_table = (
        #     pd.concat([threshold_table, threshold_counts], ignore_index=True)
        # )
        print("500 flips: dumping stats to csv, resetting buffer")
        master_table.to_csv(master_tally,header=False)
        # comm_table.to_csv(comm_tally,header=False)
        master_table = master_table.iloc[0:0]
        # comm_table = comm_table.iloc[0:0]
        # race_table.to_csv(populations_race, header=False)
        # plurality_table.to_csv(pluralities_race, header=False, index=False)
        # threshold_table.to_csv(threshold_race, header=False, index=False)
        # race_table = race_table.iloc[0:0]
        # plurality_table = plurality_table.iloc[0:0]
        # threshold_table = threshold_table.iloc[0:0]
master_tally.close()
# comm_tally.close()
# populations_race.close()
# pluralities_race.close()
# threshold_race.close()
# MAIN FUNCTION
#################
