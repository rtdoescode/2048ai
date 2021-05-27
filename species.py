import random
import parameters
import numpy
import globalvars
import genome

class Species(object):

    ALL_SPECIES = []
    
    def __init__(self):
        Species.ALL_SPECIES.append(self)
        self.founder = None
        self.genomes = []
        self.name = ""
        self.no_mutate = False
        self.set_random_name()
        self.max_fitness = 0
        self.last_fitness = 0
        self.avg_fitness = 0
        self.stale_count = 0

    def get_max_fitness(self):
        current_max = 0
        cumulative_fitness = 0
        tested_genomes = 0
        for g in self.genomes:
            if g.tested == True:
                tested_genomes += 1
                cumulative_fitness += g.fitness
                if g.fitness > current_max:
                    current_max = g.fitness

        if tested_genomes == 0:
            self.avg_fitness = 0
        else:
            self.avg_fitness = cumulative_fitness/tested_genomes
        return current_max

    def check_stale(self):
        self.last_fitness = self.get_max_fitness()
        if self.last_fitness > self.max_fitness:
            self.max_fitness = self.last_fitness
            self.stale_count = 0
            
        elif self.max_fitness*parameters.LowerFitnessAllowance > self.last_fitness:
            self.stale_count += 1

            if self.stale_count > parameters.StaleSpecies:
                print("species ", self.name, " became stale.")
                self.destroy_species()

    def check_has_genomes(self):
        if len(self.genomes) < 1:
            self.destroy_species()

    def destroy_species(self):

        if len(Species.ALL_SPECIES) > 1:
            del self.founder
            for g in self.genomes:
                g.destroy_genome()
            Species.ALL_SPECIES.remove(self)
            del self

    def checkSameSpecies(self,genome):

        if genome == self.founder:
            return True
        
        dd = parameters.DeltaDisjoint*genome.disjoint(self.founder)
        dw = parameters.DeltaWeights*genome.weight_dif(self.founder)
        return dd + dw < parameters.DeltaThreshold

    def check_species_after_mutation(self,child):
        
        child.update_species()

    def set_random_name(self):

        vowels = ["a","e","i","o","u"]
        consts = ["b","c","d","h","j","k","l","m","n","p","q","r","s","t","v","w","x","y","z"]

        n = 4
        while n > 0:
            rand = random.random()
            n -= 1
            if rand < 0.4:
                self.name += random.choice(consts)
                self.name += random.choice(vowels)
            elif rand < 0.8:
                self.name += random.choice(consts)
                self.name += random.choice(vowels)
            elif rand < 0.9:
                self.name += random.choice(vowels)
                self.name += random.choice(vowels)
            else:
                self.name += random.choice(consts)
                self.name += random.choice(consts)

    def add_to_species(self,child):

        if child == 0 or child is None:
            return

        if child.species == self:
            if not child in self.genomes:
                self.genomes.append(child)
            return

        #remove genome from any current species
        for s in Species.ALL_SPECIES:
            if child in s.genomes:
                s.genomes.remove(child)
                if len.s.genomes == 0:
                    s.destroy_species()
              
        #add genome to this species      
        child.species = self
        self.genomes.append(child)

        #make sure genome is in genepool
        if child in globalvars.get_genomepool():
            pass
        else:
            globalvars.get_genomepool().append(child)


    def display(self):
        print(self.name,": ", len(self.genomes), " genomes. Fitness: ",
              self.max_fitness, " historic, ",
              self.last_fitness, " max, ",
              self.avg_fitness, " average")

    def next_generation(self, reproductions):

        #Reset any genomes that were temporarily set to not mutate
        if(self.no_mutate == True):
            self.no_mutate = False
            return

        if len(self.genomes) < 1:
            self.destroy_species()
            return
        
        mutations = 0
        clones = 0
        breeds = 0

        while reproductions > 0:
            if random.random() < parameters.CrossoverChance:
                genome1 = random.choice(globalvars.get_genomepool())
                genome2 = random.choice(self.genomes)
                genome3 = genome1.create_offspring(genome2)
                genome3.createdvia = "crossover"
                self.add_to_species(genome3)
                breeds += 1
            elif random.random() < parameters.CloneChance:
                genome = random.choice(self.genomes)
                genome2 = genome.clone()
                genome2.createdvia = "clone"
                self.add_to_species(genome2)
                clones += 1
            else:
                genome1 = random.choice(self.genomes)
                genome2 = random.choice(self.genomes)
                genome3 = genome1.create_offspring(genome2)
                genome3.createdvia = "breeding"
                self.add_to_species(genome3)
                breeds += 1
                
            reproductions -= 1
        
        for g in self.genomes:
            
            if random.random() < parameters.NodeMutationChance:
                if len(g.neurons) < parameters.MaxNodes:
                    mutations += 1
                    g.mutate_new_neuron()
            if random.random() < parameters.ConnectionMutationChance:
                mutations += 1
                g.mutate_new_connection()
            if random.random() < parameters.WeightMutationChance:
                mutations += 1
                g.mutate_weight()
            if random.random() < parameters.DisableMutationChance:
                mutations += 1
                g.mutate_disable()
            if random.random() < parameters.EnableMutationChance:
                mutations += 1
                g.mutate_enable()
            if random.random() < parameters.BiasMutationChance:
                mutations += 1
                g.mutate_bias()


            self.check_species_after_mutation(g)
        
    def cull_half(self):
        fitnesses = []

        for g in self.genomes:
            fitnesses.append(g.fitness)

        cull_threshold = numpy.median(fitnesses)

        for judged in self.genomes:
            if judged.fitness < cull_threshold:

                    judged.destroy_genome()
        
