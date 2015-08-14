import ga
import time

ga.nThreads = 4

perHour = 6
hours = 9

ga.gaGlass(100, "asdf")

for i in range(perHour*hours):
    ga.gaGlass(500, "exp_" + str(i) + "_")
    
