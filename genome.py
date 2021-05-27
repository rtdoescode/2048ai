import numpy
import random
import parameters
import species
import globalvars
import copy

GenerationNewGenes = []
GenerationNewNeurons = []

class Genome(object):

    def __init__(self):
        self.genes = []
        self.neurons = []
        self.fitness = 0
        self.species = 0
        self.gid = 0
        self.moved_species = False
        self.tested = False
        self.createdvia = ""
        self.maxneuron = 0

    #Mutation that changes the weight of a random gene
    def mutate_weight(self):
        if random.random() > 1-parameters.PerturbChance:
            for g in self.genes:
                g.weight += parameters.StepSize * random.choice([-1,1])
        else:
            
            gene = random.choice(self.genes)
            offset = random.random()-0.5
            gene.weight += offset

    def destroy_genome(self):
        if self in globalvars.get_genomepool():
            globalvars.get_genomepool().remove(self)
        if self in self.species.genomes:
            self.species.genomes.remove(self)

        if self.species.founder == self:
            pass
        else:
            del self
        
        
    #Mutation that enables a random disabled gene
    def mutate_enable(self):

        disabled_genes = []
        for g in self.genes:
            if g.enabled == False:
                disabled_genes.append(g)

        if(len(disabled_genes) < 1):
            return

        gene = random.choice(disabled_genes)
        gene.enabled = True

    #Mutation that disables a random enabled gene
    def mutate_disable(self):

        enabled_genes = []
        for g in self.genes:
            if g.enabled == True:
                enabled_genes.append(g)

        if(len(enabled_genes) < 1):
            return

        gene = random.choice(enabled_genes)
        gene.enabled = False

    def display(self):
        inv = []
        for g in self.genes:
            inv.append(g.innovation)

        spec = ""
        if self.species != 0:
            spec = self.species.name
        
        print(self.gid, spec, inv)

    def mutate_bias(self):
        n = random.choice(self.neurons)
        n.bias += parameters.StepSize * random.choice([-1,1])
    
    def debug_display_innovations(self):
        print("genome ", self.gid)
        for g in self.genes:

            toggle = ""
            if not g.enabled:
                toggle = " (disabled)"
            
            print("gene ", g.innovation, " weight ",g.weight, toggle)
    
    #Mutation that creates a new gene    
    def mutate_new_connection(self):
        neuron_from = self.get_random_neuron(True)
        neuron_to   = self.get_random_neuron(False)

        new_connection = Connection(self)
        new_connection.weight = 1
        new_connection.next_node = neuron_to
        new_connection.previous_node = neuron_from
        self.assign_connection_innovation(new_connection)

        self.genes.append(new_connection)
        neuron_to.incoming.append(new_connection)
        neuron_from.outgoing.append(new_connection)

        GenerationNewGenes.append(new_connection)

    def create_offspring(self,genome2):

        main_parent = 0
        second_parent = 0
        
        if self.fitness > genome2.fitness:
            main_parent = self
            second_parent = genome2
        else:
            main_parent = genome2
            second_parent = self

        new_genome = Genome()

        #add matching genes
        for gene1 in main_parent.genes:
            for gene2 in second_parent.genes:
                if gene1.innovation == gene2.innovation:
                    #both parents have this gene, offspring always gets it
                    new_connection = Connection(new_genome)
                    new_genome.genes.append(new_connection)
                    new_connection.parent = new_genome
                    new_connection.weight = gene1.weight
                    new_connection.innovation = gene1.innovation
                    new_connection.enabled = gene1.enabled
                    new_connection.copy_next_node = gene1.next_node
                    new_connection.copy_prev_node = gene1.previous_node

        new_genome.create_network_from_genes()

        ##Add random disjoint genes

        for gene1 in main_parent.genes:
            gene_applicable = True

            #Random chance of not inheriting each disjoint gene            
            if random.random() < parameters.InheritDisjoint:
                continue

            #don't consider genes that are already in the new genome
            for existing_gene in new_genome.genes:
                if gene1.innovation == existing_gene.innovation:
                    gene_applicable = False

            if gene_applicable == False:
                continue

            #check if both previous and next node exist in the new genome
            next_valid = None
            prev_valid = None
            for check_neuron in new_genome.neurons:
                if check_neuron.id == gene1.next_node.id:
                    next_valid = check_neuron
                    
                if check_neuron.id == gene1.previous_node.id:
                    prev_valid = check_neuron

            #If required nodes are present, create a new connection between them
            if next_valid is not None:
                if prev_valid is not None:
                    disjoint_gene = Connection(new_genome)
                    disjoint_gene.parent = new_genome
                    disjoint_gene.weight = gene1.weight
                    disjoint_gene.innovation = gene1.innovation
                    disjoint_gene.enabled = gene1.enabled
                    
                    new_genome.genes.append(disjoint_gene)
                    
                    disjoint_gene.next_node = next_valid
                    next_valid.incoming.append(disjoint_gene)
                    
                    disjoint_gene.previous_node = prev_valid
                    prev_valid.outgoing.append(disjoint_gene)
                    
                    
        return new_genome

    def create_network_from_genes(self):
        for gene in self.genes:

            next_linked = False
            prev_linked = False

            for n in self.neurons:
                
                if n.id == gene.copy_next_node.id:
                    gene.next_node = n
                    n.incoming.append(gene)
                    next_linked = True
                elif n.id == gene.copy_prev_node.id:
                    gene.previous_node = n
                    n.outgoing.append(gene)
                    prev_linked = True

            if next_linked == False:
                gene.next_node = Neuron(self)
                self.neurons.append(gene.next_node)
                gene.next_node.incoming.append(gene)
                
                gene.next_node.id = gene.copy_next_node.id
                gene.next_node.parent = self
                gene.next_node.replaced_connection = gene.copy_next_node.replaced_connection
                gene.next_node.bias = gene.copy_next_node.bias
                gene.next_node.is_input = gene.copy_next_node.is_input
                gene.next_node.is_output = gene.copy_next_node.is_output
                gene.next_node.output_type = gene.copy_next_node.output_type
                gene.next_node.expecting_input = gene.copy_next_node.expecting_input
            if prev_linked == False:
                gene.previous_node = Neuron(self)
                self.neurons.append(gene.previous_node)
                gene.previous_node.outgoing.append(gene)
                
                gene.previous_node.id = gene.copy_prev_node.id
                gene.previous_node.parent = self
                gene.previous_node.replaced_connection = gene.copy_prev_node.replaced_connection
                gene.previous_node.bias = gene.copy_prev_node.bias
                gene.previous_node.is_input = gene.copy_prev_node.is_input
                gene.previous_node.is_output = gene.copy_prev_node.is_output
                gene.previous_node.output_type = gene.copy_prev_node.output_type
                gene.previous_node.expecting_input = gene.copy_prev_node.expecting_input

        gene.copy_prev_node = None
        gene.copy_next_node = None
        
    def clone(self):

    #this used to use copy.deepcopy but it gets *horribly* slow
        
##        tmp_species = self.species
##        self.species = 0
##        new_clone = copy.deepcopy(self)
##        new_clone.gid = 0
##        new_clone.tested = False
##        self.species = tmp_species
##        globalvars.get_genomepool().append(new_clone)
##        new_clone.createdvia = "clone"

        new_clone = self.create_offspring(self)
        
        return new_clone

    def validate_genome(self):
        if isinstance(self.next_node,Neuron):
            pass
        else:
            print("|||MALFORMED GENOME")
            traceback.print_exc()
            input("continue")
        if isinstance(self.previous_node,Neuron):
            pass
        else:
            print("|||MALFORMED GENOME")
            traceback.print_exc()
            input("continue")
    
    def disjoint(self,genome):
        disjoint = 0
        g1 = []
        g2 = []

        for gene1 in self.genes:
            g1.append(gene1.innovation)
        for gene2 in genome.genes:
            g2.append(gene2.innovation)

        disjoint = set(g1).symmetric_difference(set(g2))
        disjoint_amount = len(disjoint)
        
        n = max(len(self.genes),len(genome.genes))
        return disjoint_amount/n
    
    def weight_dif(self,genome):

        weightsum = 0
        coincident = 0
        
        for gene1 in self.genes:
            for gene2 in genome.genes:
                if gene1.innovation == gene2.innovation:
                    dif = gene1.weight - gene2.weight
                    weightsum += abs(dif)
                    coincident += 1

        if(coincident == 0):
            return 0
   
        return weightsum / coincident
    
    def get_random_neuron(self, allowInput):

        choices = []
        if allowInput == True:
            for n in self.neurons:
                if n.is_input == True:
                    choices.append(n)
        else:
            choices = self.neurons

        return random.choice(choices)

    #Mutates a new neuron/node.
    # A random connection is chosen, and is split in half with a new neuron
    # in the middle
    def mutate_new_neuron(self):
        split = random.choice(self.genes)
        split.enabled = False
        
        new_neuron = Neuron(self)
        new_neuron.replaced_connection = split.innovation
        
        new_in_connection = Connection(self)
        new_in_connection.previous_node = split.previous_node
        new_in_connection.next_node = new_neuron
        new_in_connection.weight = 1
        
        new_out_connection = Connection(self)
        new_out_connection.previous_node = new_neuron
        new_out_connection.next_node = split.next_node
        new_out_connection.weight = split.weight

        self.genes.append(new_out_connection)
        self.genes.append(new_in_connection)
        self.neurons.append(new_neuron)

        self.assign_neuron_innovation(new_neuron)
        self.assign_connection_innovation(new_in_connection)
        self.assign_connection_innovation(new_out_connection)

                
        GenerationNewGenes.append(new_in_connection)                
        GenerationNewGenes.append(new_out_connection)
        GenerationNewNeurons.append(new_neuron)
        
        split.next_node.incoming.append(new_out_connection)
        new_neuron.outgoing.append(new_out_connection)
        
        split.previous_node.outgoing.append(new_in_connection)
        new_neuron.incoming.append(new_in_connection)

        GenerationNewNeurons.append(new_neuron)
        GenerationNewGenes.append(new_in_connection)
        GenerationNewGenes.append(new_out_connection)

    def assign_neuron_innovation(self,new_neuron):

        self.maxneuron += 1
        new_neuron.id = self.maxneuron

    def assign_connection_innovation(self,new_conn):

        for n in GenerationNewGenes:

            if n == new_conn:
                continue
            
            if new_conn.is_identical_gene(n):
                new_conn.innovation = n.innovation

        new_conn.innovation = Connection.GlobalInnovation
        Connection.GlobalInnovation += 1
        

    #Creates a basic neural network with only neurons
    # for inputs and outputs, and simple connections between them 
    def make_basic_network(self):

        outputNeurons = []
        validOutputs = ["up","down","left","right"]
        inputnum = 0
        self.createdvia = "starter"

        #4 outputs
        for i in range(4):
            outputNeuron = Neuron(self)
            outputNeuron.is_output = True
            outputNeurons.append(outputNeuron)
            outputNeuron.output_type = validOutputs[i]
                
        #16 inputs
        for j in range(16):
            inputNeuron = Neuron(self)
            inputNeuron.is_input = True
            inputNeuron.expecting_input = inputnum
            inputnum += 1
            self.neurons.append(inputNeuron)
            self.assign_neuron_innovation(inputNeuron)
            
##            inputNeuron.id = Neuron.GlobalNeuronInnovation
##            Neuron.GlobalNeuronInnovation += 1

            for out_node in outputNeurons:
                new_connection = Connection(self)
                new_connection.weight = 1
                new_connection.next_node = out_node
                new_connection.previous_node = inputNeuron
                new_connection.innovation = Connection.GlobalInnovation
                Connection.GlobalInnovation += 1

                inputNeuron.outgoing.append(new_connection)
                out_node.incoming.append(new_connection)
                self.genes.append(new_connection)
                
        for n in outputNeurons:
            
            self.assign_neuron_innovation(n)
            
##            n.innovation = Connection.GlobalInnovation
##            Connection.GlobalInnovation += 1
            self.neurons.append(n)
##            n.id = Neuron.GlobalNeuronInnovation
##            Neuron.GlobalNeuronInnovation += 1


    def run_network(self, inputs):
        #First 16 neurons are always inputs
        for n in self.neurons:
            if n.expecting_input != 0:
                n.value = inputs[n.expecting_input]
                
        outputNeurons = []        
        for i in range(len(self.neurons)):
            if self.neurons[i].is_output == True:
                outputNeurons.append(self.neurons[i])

        #Evaluate each neuron recursively starting with output neurons
        for i in range(len(outputNeurons)):
            outputNeurons[i].output_value = outputNeurons[i].evaluate()
        return outputNeurons

    def update_species(self):
        #if the genome still belongs in it's current species, do nothing
        if isinstance(self.species,species.Species):
            if self.species.checkSameSpecies(self):
                return
                        
        for s in species.ALL_SPECIES:
            if s.checkSameSpecies(self):
                s.add_to_species(self)
                return
                
        #if no species are valid, make a new one
        self.new_species()

    def new_species(self):
        new_species = species.Species()
        new_species.founder = self
        new_species.no_mutate = True
        s.add_to_species(self)


class Connection(object):
    GlobalInnovation = 1
    def __init__(self, parent):
        self.innovation = 0
        self.parent = parent
        self.previous_node = 0
        self.next_node = 0
        self.weight = 0.0
        self.enabled = True

        self.target_next_node = None
        self.target_prev_node = None
        

    def is_identical_gene(self, other):

        prev_innovation = self.previous_node.id
        next_innovation = self.next_node.id

        other_prev_innovation = other.previous_node.id
        other_next_innovation = other.next_node.id

        if prev_innovation == other_prev_innovation:
            if other_next_innovation == next_innovation:
                return True
        return False

        
class Neuron(object):
    GlobalNeuronInnovation = 1
    def __init__(self, parent):
        self.id = 0
        self.parent = parent
        self.replaced_connection = 0
        self.value = 0
        self.bias = 0
        self.incoming = []
        self.outgoing = []
        self.is_input = False
        self.is_output = False
        self.output_value = 0
        self.output_type = 0
        self.expecting_input = 0

    def is_identical_neuron(self, other):

        prev_innovations = []
        next_innovations = []
        other_prev_innovations = []
        other_next_innovations = []

        for g in self.incoming:
            prev_innovations.append(g.innovation)

        for g in self.outgoing:
            next_innovations.append(g.innovation)

        for g in other.incoming:
            other_prev_innovations.append(g.innovation)

        for g in other.outgoing:
            other_next_innovations.append(g.innovation)

        if prev_innovations == other_prev_innovations:
            if other_next_innovations == next_innovations:
                return True
        return False

    def evaluate(self):
        if self.is_input == True:
            return self.value
        else:
            sum = 0
            for connection in self.incoming:
                if connection.enabled == True:
                    sum = sum + (connection.weight * connection.previous_node.evaluate()) 
            sum = sum + self.bias
            return sigmoid(sum)
        
def sigmoid(x):
    return (1 / (1 + numpy.exp(-x)))
        
