import gerrychain
import geopandas
import pandas as pd
import json
import networkx
import matplotlib.pyplot as plt
import random
import numpy as np
import csv

# THE MEAT
#####################
# Import Data

# brining in 69 columns ehre, incdluding geometry column
Data = geopandas.read_file("./nyc_shapes/gerrychain_blocks.shp")
# Data = geopandas.read_file("./PA-shapefiles/PA.shp")


# The Dual Graph. Nodes are districts, whose edges are bordering districts. think of one part of
# the dual graph as a conventional map, where the face between lines are districts, and nodes are
# the corners...the other part of the dual is when nodes are the center of the district,
# and edges connect to centers of other districts...
dg = gerrychain.Graph.from_geodataframe(Data)

# Assignment Dict
# maps node ids / (census blocks) to voting districts..
asgn = Data["CD"]
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

partition_updaters = {
    "population": gerrychain.updaters.Tally("VAP", "population", dtype=int),
    "black_pop": gerrychain.updaters.Tally("BVAP", "black_pop", dtype=int),
    "asian_pop": gerrychain.updaters.Tally("ASIANVAP", "asian_pop", dtype=int),
    "white_pop": gerrychain.updaters.Tally("WVAP", "white_pop", dtype=int),
    "hisp_pop": gerrychain.updaters.Tally("HVAP", "hisp_pop", dtype=int),
    "amin_pop": gerrychain.updaters.Tally("AMINVAP", "amin_pop", dtype=int),
    "hp_pop": gerrychain.updaters.Tally("NHPIVAP", "hp_pop", dtype=int),
    "other_pop": gerrychain.updaters.Tally("OTHERVAP", "other_pop", dtype=int)
}

# todo, number of plurality districts per race.
# Ideal Pop Object (in initial state)
pop_partition_object = gerrychain.partition.Partition(
    dg, asgn, partition_updaters
)
# dummy validator (everything is valid)
def dummy(c):
    print(c)
    return True
# another constrin can be contiguity.
# contiguous = gerrychain.constraints.contiguous
visible = gerrychain.constraints.no_vanishing_districts
within = gerrychain.constraints.within_percent_of_ideal_population(pop_partition_object, .25)
# todo compactness, builtin, must us geographic partition tpe object.
# todo, neighborhood splits

# lis of bool fnns
valid = gerrychain.constraints.Validator([dummy])


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
    5
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
populations_race = open('./outputs/populations_by_race.csv', "a")
pluralities_race = open('./outputs/pluralities_by_race.csv', "a")
threshold_race = open('./outputs/threshold_by_race.csv', "a")
desired_columns = [
    'population', 'black_pop', 'asian_pop', 'white_pop', 'hisp_pop', 'amin_pop', 'hp_pop',
    'other_pop'
]

# initiate with index names (multi index)
# Initial State, empty table
# NOTE: updater fns not functioning....gerychain bug?
names = ['Chain-State', 'District']
for name, _ in partition_object.updaters.items():
    # updater functions not longer working,
    # so calling them manually!
    if name in desired_columns:
        names.append(name)

names_pops = names.copy()
names_pops = names.remove('population')
race_table = (
    pd.DataFrame(columns=names_pops)
        .set_index(['Chain-State', 'District'])
)
race_table = race_table.drop('population', axis=1)
names_stats = names.copy()
names_stats.remove('District')
names_stats.remove('population')
plurality_table = (
    pd.DataFrame(columns=names_stats)
        .set_index(['Chain-State'])
)
threshold_table = (
    pd.DataFrame(columns=names_stats)
        .set_index(['Chain-State'])
)

for k, state in enumerate(chain):
    k += 1
    concat_this = []
    for name, fn in partition_object.updaters.items():
        if name in names:
            # updater functions not longer working,
            # so calling them manually!
            col = (
                pd.DataFrame(fn(partition_object).values(), index=fn(partition_object).keys())
                    .sort_index()
                    .rename(columns={0: name})
            )
            concat_this.append(col)

    _table = pd.concat(concat_this, axis=1)
    _table = _table.set_index(
        [
            pd.Index([k for _ in range(51)]),
            _table.index
        ]
    )
    _totals = pd.DataFrame(_table['population'])
    _table = _table.drop('population', axis=1)
    percent_table = _table / _totals.values
    plurality_counts = (pd.DataFrame(
        pd.value_counts(
            percent_table.idxmax(axis=1),
            dropna=False
        ).fillna(0)
        ).transpose()
                        )
    threshold_counts = pd.DataFrame(
        (percent_table > threshold).sum()
    )
    threshold_counts = threshold_counts.transpose()
    race_table = pd.concat([race_table, percent_table])
    plurality_table = (
        pd.concat([plurality_table, plurality_counts], ignore_index=True)
    )
    threshold_table = (
        pd.concat([threshold_table, threshold_counts], ignore_index=True)
    )

    if k % 100 == 0:
        race_table.to_csv(populations_race, header=False)
        plurality_table.to_csv(pluralities_race, header=False)
        threshold_table.to_csv(threshold_race, header=False)
        race_table = race_table.iloc[0:0]  # slicing works but not indexing...
        plurality_table = plurality_table.iloc[0:0]
        threshold_table = threshold_table.iloc[0:0]

populations_race.close()
pluralities_race.close()
threshold_race.close()
# MAIN FUNCTION
#################
# pops = []
# count = 0
# for each in chain:
#     count += 1
#     print(count)
#     pops.append(each["population"])
#     if count % 100 == 0:
#         with open("log.txt", "w") as f:
#             f.write(str(pops))
# in this example, not resseting data bc only 1000.

# VISUALIZE IT
##########################
# all data is attached to the state....so for instance, we can record the average ethnic breakdown or something.
# essentially visualize the updator returned lists.
# N_points = 100000
# n_bins =
#
# # Generate a normal distribution, center at x=0 and y=5
# x = np.random.randn(N_points)
# y = .4 * x + np.random.randn(100000) + 5
#
# fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)

# We can set the number of bins with the `bins` kwarg
# axs[0].hist(x, bins=n_bins)

plurality_data = pd.read_csv("outputs/pluralities_by_race.csv")

ax = plurality_data.plot(kind='bar', stacked=True, figsize=(10, 6))
ax.set_ylabel('Districts (51 total)')
ax.set_xlabel('Distribution Space')
plt.legend(title='Pluralities', bbox_to_anchor=(1.0, 1), loc='upper left')
# plt.savefig('stacked.png')  # if needed
plt.show()

threshold_data = pd.read_csv("outputs/threshold_by_race.csv.csv")
ax.set_ylabel('Districts (51 total)')
ax.set_xlabel('Distribution Space')

# hist = threshold_data.hist(bins=250)
# threshold_data.hist(by=np.random.randint(0, 4, 1000), figsize=(6, 4));
threshold_data["white"].hist()
# threshold_data[]
# threshold_data[]
# threshold_data[]
# threshold_data[]
# threshold_data[]
# plurality_data.hist
## Histograms

# For # districts  < > (x)median
# MSE of median incomes to total median income?

# For Population, per race, % of districts where race > x%
# Per race, std across each states (across distrsicts)

## STacked Bar Charts
# Stacked bar chart of # of districts where each race has plurality, per state....

#     print(count)
#     # pops.append(each["population"])
#     # if count % 100 == 0:
#         # with open("log.txt", "w") as f:
#             # f.write(pops)
#             # in this example, not reseting data bc only 1000.
#
# # can write data to file every so often if needed.
#
# # Visualization
#
# # all data is attached to the state....so for instance, we can record the average ethnic breakdown or something.
# # seems can do this with updater functions as well as the markove iterator?
#
