from glob import glob
import matplotlib.pyplot as plt
import random as rnd
import numpy as np
import math
from scipy.constants import golden as phi
import pandas as pd

circle = 8 # int(input('No of circles : '))
population_size = 60 

x_min=y_min=0

x_max = None
y_max = None

radiusOptions = ['random', 'fibonacci', 'gp']
roundsIterate = range(50,500,50)


def distance(c1, c2):
    return math.sqrt( (c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 )
 
def generateScoresPerChromosome(chromosomeSet):

    if (len(chromosomeSet)==circle) : chromosomeSet = [chromosomeSet]
    for index, row in enumerate(chromosomeSet):
        sum = 0
        for i in row:
            for j in row:
                if(i != j):
                    try:
                        sum = sum + distance( (i[0],i[1]), (j[0], j[1]) )
                    except:
                        None
                        # import pdb; pdb.set_trace()
        chromosomeSet[index].append(sum)
    if (len(chromosomeSet)==1) : chromosomeSet = chromosomeSet[0]
    return chromosomeSet

def moveX(circleConfig):
    global x_max
    radius = circleConfig[-1]
    x = circleConfig[-1]

    if (x-radius) <= 0: x += radius
    elif (x+radius) > x_max: x -= radius

    return x

def moveY(circleConfig):

    global y_max
    radius = circleConfig[-1]
    y = circleConfig[1]

    if (y-radius) <= 0: y += radius
    elif (y+radius) > x_max: y -= radius

    return y

def mutate(circleNetwork1, circleNetwork2):
    mutatChoice = np.random.random()
    if mutatChoice != 0:
        for i in range(circle):

            circleNetwork1[i][0] = moveX(circleNetwork1[i])
            circleNetwork1[i][1] = moveY(circleNetwork1[i])

            circleNetwork2[i][0] = moveX(circleNetwork2[i])
            circleNetwork2[i][1] = moveY(circleNetwork2[i])


    return circleNetwork1, circleNetwork2

def crossoverMutation(population):
    global  population_size, circle

    for i in range(int(population_size/2)  ):
        for j in range (int (population_size/2) , int(population_size - 1)):
            circleNetwork1 = []
            circleNetwork2 = []
            parent1 = population[i]
            parent2 = population[j]
            for k in range(int(circle/2)+1):
                circleNetwork1.append(parent1[k])
                circleNetwork2.append(parent2[k])

            for k in range(int(circle/2),circle-1):
                circleNetwork1.append(parent2[k])
                circleNetwork2.append(parent1[k])

            circleNetwork1, circleNetwork2 = mutate(circleNetwork1, circleNetwork2)
            

            if validateRadialProperty(circleNetwork1):
                if validateBoundaryCondition(circleNetwork1):
                    circleNetwork1 = generateScoresPerChromosome(circleNetwork1)
                    population.append(circleNetwork1)


            if validateRadialProperty(circleNetwork2):
                if validateBoundaryCondition(circleNetwork2):
                    circleNetwork2 = generateScoresPerChromosome(circleNetwork2)
                    population.append(circleNetwork2)
            
            # print ("O1" , circleNetwork1)
            # print ("O2" , circleNetwork2)
    return population

def fibonacciRadius(n):
    radius = phi**n - (-phi)**(-n)
    radius /= 5**0.5
    return np.round(radius,3)

def gpProgession(n, delta = 2, start = 1):
    return start*(delta**n)

def validateRadialProperty(chromosome):
    invalidFlag = False

    for index, i in enumerate(chromosome):
        if len (i) == 1: continue
        for j in chromosome[index+1:]:
            if len(j) == 0: continue
            circleCenterDistance =  distance(i,j) 
            if circleCenterDistance < i[-1] or circleCenterDistance < j[-1]:
                invalidFlag = True
                break

        if invalidFlag: break
            
    return invalidFlag

def validateBoundaryCondition(chromosome):
    validTag = True
    for i in chromosome:
        if len(i) == 1: continue
        if (i[0] < x_max and i[1] < y_max) and (i[0] > 0 and i[1] > 0) :
            validTag = True
        else:
            validTag= False
            break
    
    return validTag

def generateBoundaries(method='random'):
    global circle, x_max, y_max
    limit = None

    if method == 'random':
        radiusMax = 7
        limit = sum([radiusMax for i in range(0, circle)])

    if method == 'gp':
        limit = sum([gpProgession(i) for i in range(0, circle)])

    if method == 'fibonacci':
        limit = sum([fibonacciRadius(i) for i in range(0, circle)])

    x_max = y_max = 2 * limit

def initiateRandRop(mode = 'random'):
    population = []  # the 2d array
    global x_max, y_max
    for _ in range(0, population_size):
        circle_network = []
        for i in range(0, circle):
            if mode == 'random':
                r = np.random.randint(1, 7)  # random radius
            elif mode == 'fibonacci':
                r = fibonacciRadius(i)  # fibonacci radius
            elif mode == 'gp':
                r = gpProgession(i)  # geometric progession

            x = int(np.random.randint(r+1, x_max - r-1))
            y = int(np.random.randint(r+1, y_max - r-1))

            l = [x, y, r]
            circle_network.append(l)
        population.append(circle_network)
    
    return population

performanceDictionary = {}

for radiusInit in radiusOptions:
    generateBoundaries(radiusInit)
    performanceDictionary[radiusInit] = []
    for rounds in roundsIterate: 
        population = initiateRandRop(radiusInit)
        population = generateScoresPerChromosome(population)
        population = sorted(population, key=lambda x: x[-1], reverse=False)
        topFitness = []
        for round in range(rounds):
            population = crossoverMutation(population)
            population = sorted(population, key=lambda x: x[-1], reverse=False)
            population = population[:population_size]
            # print (f"===========================R{round+1}=====================================")
            # for x in population: print(x)
            topFitness.append(population[0][-1])

        maxFitness = max(topFitness)
        bestConfig =  population[topFitness.index(maxFitness)]
        performanceDictionary[radiusInit].append(bestConfig[-1])
        # print (f'{radiusInit} - iterations {rounds} done...', str(bestConfig))
        # open(f'./output/{radiusInit} - iterations {rounds}.txt', 'w').write(str(bestConfig))

perfDict = pd.DataFrame(performanceDictionary)
perfDict['rounds'] = roundsIterate

perfDict.index = perfDict.rounds
perfDict.plot()
plt.savefig('dump.png')