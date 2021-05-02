##The Partition Class
Input: graph, assignment dict, updater funcs dict  
Output: partition class

1. Dual Graph
2. Dictionary mapping nodes of graph to districts
3. Updaters which record the 'statics' of interest

? What is the Dual Graph again? nodes are census blocks or districts or what?

## The Dual Graph

Can make manually with networkX
adjacency information, but also attrs like area / perimeter for each node...

alternatively, directly from shapefile, gerrychain makes from geodataframe (geopandas)

## Markov Chain Iterator that returns a partition object ^^ generated at each step of the chain. 
Input: proposal?, acceptance criteria, initia state (current map), number of steps
Output: iterator object

## Starting Plans (states)
Can start with existing or prior proposed plan, or consider a fresh seed, in case the initial
does not satisfy hypothetical constraints we wish to study. Gerrychain includes classes
/functions to build intitial seed states.
 
## Updaterse
input: partition
output: anything, write to object, file, etc.

Callables called every iteration of chain. Updaters are building block helpers, used in propsals??
and also validity / acceptance checks. 

consists simply of a string that tells partition (where it's passed in) what to call (binding) 
and the callable....returns to store into partition class itself...

cut edges????

for instance, Tally returns dicstionary of population totals per district.
there is an updater module with prebuilt funcs

This function can also be picked up on the dor loop over the chain, if needed.

## splitting rules for counties possible

## In addition to Updater helpers, there are boolean 'binary constraints' to pass into partition object, for instance,
input: partition
output: boolean.
it's a list of functions passed in....likely with boolean returns
contiguity also possible constraint, specific conditions, bounds etc

## Proposals
input: partition object
output: assignment dictionary for new partition

This is the 'master' function. 

boundary flip is typical...


## next steps:
Evaluation function as updater
validation criteria
distribution of evaluation criteria over the chain
plot it.....

Work in NYC data, get a couple of trivial things generated, throw in an evaluation function as an
 updater, add validation criteria, generate a distribution, 





