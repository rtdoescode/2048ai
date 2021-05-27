from threading import Thread
from time import sleep
import puzzle
import threading

class network_thread(threading.Thread):

    NET_SPEED = 0.000000001
    
    def __init__(self,genome,game):
        self.genome = genome
        self.game = game
        self.previous_inputs = 0
        threading.Thread.__init__(self)
        self.start()
        
        self.last_action = None
        self.invalid_inputs = []

    def run(self):
        while True:
            sleep(network_thread.NET_SPEED)
            if self.game.ready == True:
                if self.game.queued_action != None:
                    print("Warning: Ready with queued action")
                else:

                    inputs = self.game.get_inputs()
                        
                    if self.game.game_is_over():
                        self.finish()
                        return
                    else:

                        if inputs == self.previous_inputs:
                            self.invalid_inputs.append(self.last_action)
                        else:
                            self.invalid_inputs = []
                            
                        self.previous_inputs = inputs
                        self.game.ready = False
                        
                        self.last_action = self.decide()
                        self.game.queued_action = self.last_action
                    

    def calculate_score(self):
        fitness = 0
        inputs = self.game.get_inputs()
        for i in range(len(inputs)):
            fitness = fitness + calc_tilescore(inputs[i])
        return fitness

    def finish(self):
        #print("same inputs detected, thread finishing")
        self.genome.fitness = self.calculate_score()
        self.game.thread_done = True

    def decide(self):
        inputs = self.game.get_inputs()
        outputs = self.genome.run_network(inputs)

        #print(inputs)

        maxOutputValue = None
        maxOutputKey = None
        
       # print(self.invalid_inputs)
            
        for output in outputs:
            #print("considering",output.output_type,output.output_value)

            associatedKey = None
            
            if output.output_type == "up":
                associatedKey = "'w'"
            elif output.output_type == "down":
                associatedKey = "'s'"
            elif output.output_type == "right":
                associatedKey = "'d'"
            elif output.output_type == "left":
                associatedKey = "'a'"

            if not associatedKey in self.invalid_inputs:
                #print(output.output_type," is valid")
            
                if maxOutputValue == None:
                    maxOutputValue = output.output_value
                    maxOutputKey = output.output_type
                
                elif output.output_value > maxOutputValue:
                    maxOutputValue = output.output_value
                    maxOutputKey = output.output_type
            #else:
            #    print(output.output_type," has invalid set true")

            
        if maxOutputKey == "up":
            #print("firing w")
            return "'w'"
        elif maxOutputKey == "down":
            #print("firing s")
            return "'s'"
        elif maxOutputKey == "right":
            #print("firing d")
            return "'d'"
        elif maxOutputKey == "left":
            #print("firing a")
            return "'a'"
        else:
            print("invalid output: ",maxOutputKey)

        
            
def calc_tilescore(val): 
    tilescore = 0
    multiplier = 1

    if val <= 2:
        return 0
    else:
        tilescore += val
        tilescore += calc_tilescore(val/2)
        tilescore += calc_tilescore(val/2)

    return int(tilescore)

        

            
