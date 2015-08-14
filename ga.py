import numpy
import math
import time
import random
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt

import integrator
import chromosome
import properties

perGeneration = 100
nThreads = 4

def randomGeneration(): return [chromosome.randomChromosome() for i in range(perGeneration)]
    
glassc = 0

def createNew(withFitness):
    global glassc
    ranked = map(lambda t: t[1], sorted(withFitness, key=lambda t: t[0]))
    best = ranked[:perGeneration/4]
    mutated = []
    
    ranked[0].toFile("saved/test" + str(glassc))
    glassc += 1
    
    for i in range(perGeneration - perGeneration/4):
        p1 = best[random.randint(0, len(best)-1)]
        p2 = best[random.randint(0, len(best)-1)]
        child1, child2 = chromosome.crossover(p1, p2)
        child1 = child1.mutated()
        child2 = child2.mutated()
        mutated.append(child1)
    
    return best + mutated
    
def fitness(c):
    meanTemp = integrator.meanTemp(c)
    driftTemp = meanTemp - integrator.startTemp
    return driftTemp
    
class Worker(Process):
    def __init__(self, group, queue):
        self.group = group
        self.queue = queue
        self.fs = None
        super(Worker, self).__init__(args=(queue,))

    def run(self):
        self.fs = map(fitness, self.group)
        self.queue.put(self.fs)
    
def gaGlass(nGenerations):
    newGeneration = randomGeneration()
    
    # TODO detect pletau ?
    for i in range(nGenerations):
        start = time.time()
        print i+1, "of", nGenerations

        work = []
        inThread = perGeneration / nThreads
        wontFit = perGeneration % nThreads
        for i in range(nThreads):
            group = newGeneration[inThread*i:inThread*(i+1)]
            work.append(group)
        
        if wontFit > 0: work[-1].extend(newGeneration[-wontFit:])

        queues = []
        workers = []
        
        for i in range(len(work)):
            queue = Queue()
            workers.append(Worker(work[i], queue))
            queues.append(queue)
        
        for worker in workers[1:]: worker.start()
        workers[0].run()
        for worker in workers[1:]: worker.join()
        
        doneWork = []
        
        for i in range(len(workers)):
            doneWork.append(queues[i].get())
        
        fs = sum(doneWork, [])
        best = min(fs)

        fitnessWithChromosomes = zip(fs, newGeneration)
        newGeneration = createNew(fitnessWithChromosomes)
        
        print "best:", best
        print "took", int(round(time.time() - start)), "seconds"
        print
    
    return newGeneration[0]

def plotTemps(c):
    integrator.meanTemp(c)
    vals = c.temps
    xtemps = numpy.linspace(0, integrator.drinkingTime, num=int(integrator.drinkingTime/integrator.dt))
    plt.plot(xtemps, vals)
    plt.xlabel("time / s")
    plt.ylabel("temperature / K")
    plt.show()    
    
def plotGlass(c):
    xradii = numpy.linspace(0, properties.glassHeight, num=properties.interPoints)
    fi_height_volume, fi_radius_height, fi_side_height, fi_volume_height = integrator.interStates(c)
    
    xvolume = integrator.interFunc(fi_height_volume, integrator.totalVolume, fi_volume_height[-1] / properties.interPoints, "fi_height_volume")
    yvolume = integrator.interFunc(fi_radius_height, xvolume, properties.interDHeight, "fi_radius_height")
    
    plt.plot(xradii, fi_radius_height, 'k', [xvolume], [yvolume], 'ro')
    plt.xlabel("height / m")
    plt.ylabel("radius / m")
    plt.show()
