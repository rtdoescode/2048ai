genomepool = []
generationNumber = 1

def get_genomepool():
    return genomepool

def get_generation_number():
    return generationNumber

def increment_generation():
    global generationNumber
    generationNumber += 1

def current_population():
    return len(genomepool)

#TODO:
# bias- done
# disjoint genes in offspring- done
