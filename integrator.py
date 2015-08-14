import numpy
import math
import properties
from scipy import interpolate

# constants
Ro = 1000
C = 4.1795
hTop = 33.3
hSide = 29.8

# settings
envTemp = 273+40 # K
startTemp = 273+5
totalVolume = 0.001 # m^3
dt = 0.01
drinkingTime = 15
steps = int(math.floor(drinkingTime / dt))
drinkingDiff = totalVolume / drinkingTime
dVolume = float(totalVolume) / float(properties.interPoints)

# defined time-dependent state
def volume(t): return totalVolume - drinkingDiff*t
def mass(t): return volume(t) * Ro

# differential of temperature loss for some time state and value state
def diff(timeState, valueState):
    ATop = timeState[0]
    ASide = timeState[1]
    dT  = valueState
    mass = timeState[2]

    return (hTop*ATop + hSide*ASide) * dT / (mass * C)
    
def rk4(timeState, valueState):
    values = [0]*steps
    values[0] = startTemp
    
    time = dt
    for i in range(1, len(values)):
        lastValue = values[i-1]
        
        k1 = diff(timeState(time), valueState(lastValue))
        k2 = diff(timeState(time + dt/2.0), valueState(lastValue + (dt/2)*k1))
        k3 = diff(timeState(time + dt/2.0), valueState(lastValue + (dt/2)*k2))
        k4 = diff(timeState(time + dt), valueState(lastValue + dt*k3))
        
        values[i] = lastValue + (dt/6.0) * (k1 + 2*k2 + 2*k3 + k4)  
        
        time  = i * dt
    
    values[-1] = values[-2]
    return values

def interFunc(ys, val, dx, caller):
    i = int(math.floor(val/dx))
    if i >= len(ys) and abs(i - len(ys)) < 100:
        i = len(ys)-1
        print i
    elif i >= len(ys): print i, val, caller
        
    return ys[i]

def interStates(c):
    datax = numpy.linspace(0, properties.glassHeight, num=properties.dataPoints)
    interx = numpy.linspace(0, properties.glassHeight, num=properties.interPoints)

    fi_radius_heightTck = interpolate.splrep(datax, c.radii, s=0)
    fi_radius_height = map(abs, interpolate.splev(interx, fi_radius_heightTck, der=0))
    
    fi_side_height = [0]*properties.interPoints
    for i in range(1, properties.interPoints):
        lastRadius = fi_radius_height[i-1]
        currentRadius = fi_radius_height[i]
        s = math.sqrt((lastRadius - currentRadius)**2 + properties.interDHeight**2)
        fi_side_height[i] = fi_side_height[i-1] + numpy.pi * (lastRadius + currentRadius) * s
        
    fi_volume_height = [0]*properties.interPoints
    for i in range(1, properties.interPoints):
        lastRadius = fi_radius_height[i-1]
        currentRadius = fi_radius_height[i]
        fi_volume_height[i] = fi_volume_height[i-1] + (1.0/3.0 * numpy.pi * properties.interDHeight) * (lastRadius**2 + lastRadius*currentRadius + currentRadius**2)
        
        if fi_volume_height[i] > totalVolume:
            #break
            pass
    
    volumex = numpy.linspace(0, fi_volume_height[-1], num=properties.interPoints)

    fi_height_volumeTck = interpolate.splrep(fi_volume_height, interx, s=0)
    fi_height_volume = map(lambda x: x if x > 0 else 0, interpolate.splev(volumex, fi_height_volumeTck, der=0))

    return fi_height_volume, fi_radius_height, fi_side_height, fi_volume_height

# TODO remove dt, use discrete ?
def meanTemp(c):
    fi_height_volume, fi_radius_height, fi_side_height, fi_volume_height = interStates(c)
    
    if fi_volume_height[-1] < totalVolume:
        print "removing, volume", fi_volume_height[-1]
        return envTemp+1000

    def topSurface(t):
        ht = interFunc(fi_height_volume, volume(t), dVolume, "fi_height_volume")
        return interFunc(fi_radius_height, ht, properties.interDHeight, "fi_radius_height")**2 * numpy.pi
    
    def sideSurface(t):
        ht = interFunc(fi_height_volume, volume(t), dVolume, "fi_height_volume")
        return interFunc(fi_side_height, ht, properties.interDHeight, "fi_side_height")
    
    temps = rk4(lambda t: (topSurface(t), sideSurface(t), mass(t)),
                lambda currentTemp: envTemp - currentTemp)
    
    c.temps = temps
    
    return numpy.mean(temps)
    
