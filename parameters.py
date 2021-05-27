#NEAT parameters:
#Total number of genomes
Population = 30

#Max number of neurons (nodes) in an individual neural network
MaxNodes = 750

#generations of no improvement after which a species is killed
StaleSpecies = 12

#The lowest percentage of it's historic maximum
# fitness a species must achieve to not become stale
LowerFitnessAllowance = 0.95

#Coefficient for how much difference in neurons affects species differentation
DeltaDisjoint = 1

#Coefficient for how much difference in weights affects species differentation
DeltaWeights = 1

#Coefficient for calculating overall value for species differentation
# (Lower = more distinct species)
DeltaThreshold = 100000000

#Chance of genomes breeding outside of their species whenever they breed 
CrossoverChance = 0.02

#Chance of genomes breeding being cloned whenever they breed 
CloneChance = 0.5

#Chance of genome inheriting disjoint genes from parents 
InheritDisjoint = 0.5

#Amount to increment bias and weight values by on mutation
StepSize = 0.1

#Chances for different types of mutations per genome per generation
ConnectionMutationChance = 0.3
WeightMutationChance = 0.5
NodeMutationChance = 0.35
BiasMutationChance = 0.1
PerturbChance = 0.25
DisableMutationChance = 0.075
EnableMutationChance = 0.05

