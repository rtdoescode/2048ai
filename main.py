import puzzle
import networkthread
import copy
import time
import genome
import species
import globalvars
import parameters
import numpy

def test(genome, i):
    game = puzzle.GameGrid(genome)
    genome.tested = True

    msg = "Gen: {0} #{1}. (Species: {2}) Genes: {3} Fitness: {4}".format(
        globalvars.get_generation_number(), i,
        genome.species.name,
        len(genome.genes),
        genome.fitness)
    
    print(msg)

def generation():

    #Test each genome
    for i in range(globalvars.current_population()):
        genome = globalvars.get_genomepool()[i]
        genome.gid = i
        test(genome,i)

    #Check if species are stale
    for s in species.Species.ALL_SPECIES:
        s.check_stale()

    #For each species cull genomes with lowest fitness
    for s in species.Species.ALL_SPECIES:
        s.cull_half()

    #Calculate how many times each species should reproduce
    target_reproductions = (parameters.Population - len(globalvars.get_genomepool()))/len(species.Species.ALL_SPECIES)
    actual_reproductions = 0
    expected_reproductions = 0
    
    #Process evolution for each species
    for s in species.Species.ALL_SPECIES:
        reproductions = 0
        if actual_reproductions < expected_reproductions:
            reproductions = numpy.floor(target_reproductions)
        else:
            reproductions = numpy.ceil(target_reproductions)
        actual_reproductions += reproductions
        expected_reproductions += target_reproductions
        
        s.next_generation(reproductions)

    #display info per species
    for s in species.Species.ALL_SPECIES:
        s.display()

    #check if any species have no surviving genomes
    for s in species.Species.ALL_SPECIES:
        s.check_has_genomes()
        
    #reset tested status
    for g in globalvars.get_genomepool():
        g.tested = False

    genome.GenerationNewGenes = []
    genome.GenerationNewNeurons = []

#Make basic network template
g = genome.Genome()
g.make_basic_network()
globalvars.get_genomepool().append(g)

first_species = species.Species()
first_species.founder = g

first_species.next_generation(0)

#Copy template to populate gene pool
for i in range(parameters.Population-1):
    ng = copy.deepcopy(g)
    globalvars.get_genomepool().append(ng)

#Set species of all initial genomes
for g in globalvars.get_genomepool():
    #first_species.genomes.append(g)
    #g.species = first_species
    first_species.add_to_species(g)

while True:

    gens = input("How many generations?")
    gens = int(gens)

    while gens > 0:
        gens -= 1
        generation()
        globalvars.increment_generation()

