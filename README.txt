To start the NEAT algorithm, run "main.py".
To play 2048 without AI, run "game-noai.py".

"main.py" handles the main generational loop itself

"genome.py" contains most of the logic for the neural networks itself, as well as the components that make up each genome (connections, nodes)

"parameters.py" contains NEAT parameters which can be changed to affect how the algorithm performs.

"species.py" contains the species-level logic - comparing whether genomes are the same species and eliminating half of species each generation, for example.

"networkthread.py" contains are intermediate logic between the neural networks and the game itself, it handles the inputs and outputs.

"globalvars.py" contains global variables

"puzzle.py" and "logic.py" implement the actual 2048 game itself. 
	They were not written by me, except for minor edits to interface with the code from networkthread.py
	These files are available on github here https://github.com/yangshun/2048-python