import os
import numpy as np

def readFromFile():
    code_location = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(code_location, 'input.txt')
    i = 0
    totalCities = 0
    with open(input_file, 'r') as file:
        for line in file:
            if(totalCities == 0):
                totalCities = int(line.strip())
                cityList = np.zeros((totalCities, 3), dtype=int)
            else:
                x, y, z = map(int, line.split())
                cityList[i] = np.array([x, y, z])
                i += 1

    return totalCities, cityList 

totalBreedingPopulation = 100
MutationRate = 8
TotalGenerations = 1000
howManyParts = 2

totalCities, cityList = readFromFile()

halfGenePool = totalCities // howManyParts
greedyFlag = True
distance_lookup = {}

bestRank = 0
bestPath = np.zeros((totalCities, 3), dtype=int)

def tuningParameters(bpop, mr, gen):
    global totalBreedingPopulation, MutationRate, TotalGenerations
    if bpop:
        totalBreedingPopulation = int(bpop)
    if mr:
        MutationRate = int(mr)
    if gen: 
        TotalGenerations = int(gen)

if(totalCities <= 3):
    print("Not enough points given. All paths are the shortest path.")
    raise SystemExit
elif(totalCities <= 6):
    tuningParameters(5000, 1, 1)
elif(totalCities <= 50):
    tuningParameters(128, 8, 1500)
elif(totalCities <= 100):
    tuningParameters(128, 8, 1024)
elif(totalCities <= 200):
    tuningParameters(64, 8, 1024)
elif(totalCities <= 500):
    tuningParameters(64, 4, 512)
elif(totalCities <= 1000):
    tuningParameters(32, 4, 400)
elif(totalCities <= 2000):
    tuningParameters(32, 8, 256)
elif(totalCities <= 4000):
    tuningParameters(16, 8, 128)
    greedyFlag = False
elif(totalCities <= 6000):   
    tuningParameters(16, 8, 64)
    greedyFlag = False
elif(totalCities > 6000):
    tuningParameters(16, 8, 32)
    greedyFlag = False

for i in range(len(cityList)):
    for j in range(i + 1, len(cityList)):  
        point1 = tuple(cityList[i])  
        point2 = tuple(cityList[j]) 
        distance = np.linalg.norm(cityList[i] - cityList[j])
        forward_key = point1 + point2
        backward_key = point2 + point1
        distance_lookup[forward_key] = distance
        distance_lookup[backward_key] = distance

def write_output_to_file(bestRank, bestPath):
    code_location = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(code_location, 'output.txt')

    with open(output_file, 'w') as file:
        file.write(f"{int(bestRank[0])}\n")
        
        for city in bestPath:
            file.write(f"{city[0]} {city[1]} {city[2]}\n")
        
        start_city = bestPath[0]
        file.write(f"{start_city[0]} {start_city[1]} {start_city[2]}\n")

def greedyApproach(cityList):
    copyList = np.random.permutation(cityList)
    path = np.zeros((totalCities, 3), dtype=cityList.dtype)
    path[0] = copyList[0]
    copyList = np.delete(copyList, 0, axis=0)

    for i in range(1, totalCities):
        minDistance = float('inf')
        index = i
        for j in range(copyList.shape[0]):
            point1 = tuple(path[i-1])  
            point2 = tuple(copyList[j]) 
            key = point1 + point2
            distance = distance_lookup[key]
            if distance < minDistance:
                minDistance = distance
                index = j
        path[i] = copyList[index]
        copyList = np.delete(copyList, index, axis=0)
    return path

def CalculateFitness(inputPathsGiven, start=0, RankedScore=None):
    if RankedScore is None:
        RankedScore = np.zeros((totalBreedingPopulation, 1))
    else:
        RankedScore[start:] = 0

    for i in range(start, totalBreedingPopulation):
        sum = 0
        for j in range(2, totalCities):
            point1 = tuple(inputPathsGiven[i][j])  
            point2 = tuple(inputPathsGiven[i][j-1]) 
            sum += distance_lookup[point1 + point2]

        point1 = tuple(inputPathsGiven[i][totalCities-1])  
        point2 = tuple(inputPathsGiven[i][0]) 
        sum += distance_lookup[point1 + point2]
        RankedScore[i] = sum

    sortedIndices = np.argsort(RankedScore, axis=None)
    sorted_RankList = RankedScore[sortedIndices]
    sorted_listOfPaths = inputPathsGiven[sortedIndices]  

    return sorted_RankList, sorted_listOfPaths


def exhausutiveBruteForce(copyList):
    allPermutations = np.empty((totalBreedingPopulation, totalCities, 3), dtype=copyList.dtype)
    for i in range(totalBreedingPopulation):
        allPermutations[i] = np.random.permutation(copyList)
    orderedRank, orderedPaths = CalculateFitness(allPermutations)

    write_output_to_file(orderedRank[0], orderedPaths[0])
    raise SystemExit

if(totalCities <= 6):
    copyList = np.zeros((totalCities, 3), dtype=cityList.dtype) 
    copyList = np.array([cityList])
    exhausutiveBruteForce(copyList)

def CreateInitialPopulation(cityList):
    initial_population = np.zeros((totalBreedingPopulation, len(cityList), cityList.shape[1]), dtype=cityList.dtype)
    initial_population[0] = np.array([cityList])

    sortedIndices = np.lexsort((cityList[:, 2], cityList[:, 1], cityList[:, 0]))
    cityList = cityList[sortedIndices]
    initial_population[1] = np.array([cityList])
    
    sortedIndices = np.lexsort((cityList[:, 2], cityList[:, 0], cityList[:, 1]))
    cityList = cityList[sortedIndices]
    initial_population[2] = np.array([cityList])
    
    sortedIndices = np.lexsort((cityList[:, 1], cityList[:, 0], cityList[:, 2]))
    cityList = cityList[sortedIndices]
    initial_population[3] = np.array([cityList])
    
    sortedIndices = np.lexsort((cityList[:, 1], cityList[:, 2], cityList[:, 0])) 
    cityList = cityList[sortedIndices]
    initial_population[4] = np.array([cityList])
    
    sortedIndices = np.lexsort((cityList[:, 0], cityList[:, 2], cityList[:, 1])) 
    cityList = cityList[sortedIndices]
    initial_population[5] = np.array([cityList])
    
    sortedIndices = np.lexsort((cityList[:, 0], cityList[:, 1], cityList[:, 2])) 
    cityList = cityList[sortedIndices]
    initial_population[6] = np.array([cityList])

    if greedyFlag:
        initial_population[7] = np.array([greedyApproach(cityList)])
        initial_population[8] = np.array([greedyApproach(cityList)])
        initial_population[9] = np.array([greedyApproach(cityList)])
        preselected = 10
    else:
        preselected = 7

    for i in range(totalBreedingPopulation-preselected):
        cityList = np.random.permutation(cityList)
        initial_population[i+preselected] = np.array([cityList])

    return initial_population


listOfPaths = CreateInitialPopulation(cityList)

RankedScoreOfDistances, listOfPaths = CalculateFitness(listOfPaths)

ElitePopulation = totalBreedingPopulation // 2

bestPath = listOfPaths[0]
bestRank = RankedScoreOfDistances[0]

def reproduction(firstParent, secondParent, childStart, childEnd):  
    createdChild = np.zeros((totalCities, 3), dtype=cityList.dtype)

    for i in range(childStart, childEnd):
        createdChild[i] = firstParent[i]  
    
    parentTuple = [tuple(gene) for gene in secondParent]  
    childTuple = [tuple(gene) for gene in createdChild[childStart:childEnd]]

    leftOver = [gene for gene in parentTuple if gene not in childTuple]
    indexLeftover = 0
    for i in range(totalCities):
        if i < childStart or i >= childEnd:
            createdChild[i] = leftOver[indexLeftover]
            indexLeftover += 1

    return createdChild

def mutation(selectedPath, mutationRate):
    for i in range(totalCities-1):
        if np.random.randint(100) < mutationRate:
            selectedPath[[i, i+1]] = selectedPath[[i+1,i] ]
    if np.random.randint(20)%19 == 0:
        selectedPath[[0,totalCities-1]] = selectedPath[[totalCities-1,0]]
    return selectedPath


def NextGeneration():
    New_Population = np.zeros((totalBreedingPopulation, len(cityList), cityList.shape[1]), dtype=cityList.dtype)

    for i in range(ElitePopulation):
        New_Population[i] = listOfPaths[i]

    for i in range(ElitePopulation, totalBreedingPopulation):
        firstParent, secondParent = sorted(np.random.choice(range(ElitePopulation), 2, replace=False))
        firstSelected = New_Population[firstParent]  
        secondSelected = New_Population[secondParent]  

        childStart = np.random.randint(0, halfGenePool-1)
        childEnd = childStart + halfGenePool

        createdChild = reproduction(firstSelected, secondSelected, childStart, childEnd)    
        New_Population[i] = createdChild   

    for i in range(ElitePopulation, totalBreedingPopulation):
        New_Population[i] = mutation(New_Population[i], MutationRate)
    return New_Population

for i in range(TotalGenerations):
    listOfPaths = NextGeneration()
    RankedScoreOfDistances, listOfPaths = CalculateFitness(listOfPaths, ElitePopulation, RankedScoreOfDistances)

    if RankedScoreOfDistances[0] < bestRank:
        bestRank = RankedScoreOfDistances[0]
        bestPath = listOfPaths[0]

write_output_to_file(bestRank, bestPath)
