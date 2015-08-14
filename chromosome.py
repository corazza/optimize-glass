import math
import random
import numpy
import cPickle as pickle
from scipy import interpolate

import properties
import integrator

mutationRate = 0.05
crossoverRate = 0.1
mutationRadiusMax = 0.02

class Chromosome():
    def __init__(self, radii):
        self.radii = radii
        
    def getVolume(self):
        _, _, _, fi_volume_height = integrator.interStates(self)
        return fi_volume_height[-1]

    def scaled(self):
        volume = self.getVolume()
        scaler = math.sqrt(float(integrator.totalVolume) / volume)
        newRadii = map(lambda r: r*scaler, self.radii)
        return Chromosome(newRadii)
    
    def mutated(self):
        newRadii = []
        for r in self.radii:
            newR = r + (mutationRadiusMax * (2*random.random() - 1) if random.random() < mutationRate else 0)
            if newR > properties.minWidth and newR < properties.maxWidth: newRadii.append(newR)
            else: newRadii.append(r)
        
        return Chromosome(newRadii)
        
    def toFile(self, fname):
        pckl_file = file(fname, "w")
        pickle.dump(self.radii, pckl_file)
        pckl_file.close()
        
def crossover(c1, c2):
    if random.random() < 1 - crossoverRate: return c1, c2
    n = random.randint(0, properties.dataPoints)
    newRadii1 = c1.radii[:n] + c2.radii[n:]
    newRadii2 = c2.radii[:n] + c1.radii[n:]
    return Chromosome(newRadii1), Chromosome(newRadii2)

def randomChromosome():
    x = numpy.linspace(0, properties.glassHeight, num=4)
    radiix = numpy.linspace(0, properties.glassHeight, num=properties.dataPoints)
    y = [properties.minWidth + random.random()*(properties.maxWidth - properties.minWidth) for i in range(4)]

    splradiiTck = interpolate.splrep(x, y, s=0)
    splradii = map(abs, interpolate.splev(radiix, splradiiTck, der=0))

    return Chromosome(splradii)

def circularChromosome():
    radii = [0]*properties.dataPoints
    for i in range(0, properties.dataPoints):
        radii[i] = (properties.glassHeight/2.0)*math.sin(math.acos(1 - (i+1)/26.0))
    return Chromosome(radii)

def constantChromosome():
    radii = [0.1]*properties.dataPoints
    return Chromosome(radii)

def fromFile(fname):
    pckl_file = file(fname, "r")
    data = pickle.load(pckl_file)
    pckl_file.close()
    return Chromosome(data)

