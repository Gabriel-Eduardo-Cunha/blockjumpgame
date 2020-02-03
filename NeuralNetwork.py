import math
import random
import time
import json
import os

# The Network Class by itself


class Network:

    # Construct
    def __init__(self, jsonOrModel = True, loadJson = False):
        if jsonOrModel == True:
            self._i_nodes = 1
            self._h_nodes = 2
            self._o_nodes = 1

            self._bias_ih = Matrix.randomMatrix(self._h_nodes, 1)
            self._bias_ho = Matrix.randomMatrix(self._o_nodes, 1)

            self._weights_ih = Matrix.randomMatrix(
                self._h_nodes, self._i_nodes)
            self._weights_ho = Matrix.randomMatrix(
                self._o_nodes, self._h_nodes)

            self._learningRate = 0.1

            self._data = {'inputs': [], 'outputs': [], 'meanings': []}
        elif loadJson:
            self.loadJson(jsonOrModel)   
        else:
            self.loadModel(jsonOrModel)
                  

    # public Methods

    def insertData(self, input, output, meaning):

        self.getData()['inputs'].append(input)
        self.getData()['outputs'].append(output)
        self.getData()['meanings'].append(meaning)

        newO_nodes = self.getO_nodes()
        for i in range(len(self.getData()['outputs'])):
            if len(self.getData()['outputs'][i]) > newO_nodes:
                newO_nodes = len(self.getData()['outputs'][i])

        newI_nodes = self.getI_nodes()
        for i in range(len(self.getData()['inputs'])):
            if len(self.getData()['inputs'][i]) > newI_nodes:
                newI_nodes = len(self.getData()['inputs'][i])
        newH_nodes = self.getH_nodes()

        if newI_nodes > self.getI_nodes():
            for i in range(len(self.getData()['inputs'])):
                if self.getI_nodes() > len(self.getData()['inputs'][i]):
                    newArray = [0 for x in range(
                        self.getI_nodes() - len(self.getData()['inputs'][i]))]
                    for j in range(len(newArray)):
                        newArray[j] = 0
                    newArray.extend(self.getData()['inputs'][i])
                    self._data['inputs'][i] = newArray
        if newO_nodes > self.getO_nodes():
            for i in range(len(self.getData()['outputs'])):
                if self.getO_nodes() > len(self.getData()['outputs'][i]):
                    newArray = [0 for x in range(
                        self.getO_nodes() - len(self.getData()['outputs'][i]))]
                    for j in range(len(newArray)):
                        newArray[j] = 0
                    newArray.extend(self.getData()['outputs'][i])
                    self._data['outputs'][i] = newArray

        self._changeSize(newI_nodes, newH_nodes, newO_nodes)

    def insertWord(self, input, meaning):
        if(not meaning in self.getData()['meanings']):
            self.getData()['meanings'].append(meaning)

        self.getData()['inputs'].append(input)
        self.getData()['outputs'].append(list(int(x)
                                              for x in bin(self.getData()['meanings'].index(meaning))[2:]))

        biggestOutput = 0
        for i in range(len(self.getData()['outputs'])):
            if len(self.getData()['outputs'][i]) > biggestOutput:
                biggestOutput = len(self.getData()['outputs'][i])

        newO_nodes = biggestOutput
        newI_nodes = 1
        for i in range(len(self.getData()['inputs'])):
            if len(self.getData()['inputs'][i]) > newI_nodes:
                newI_nodes = len(self.getData()['inputs'][i])
        newH_nodes = self.getH_nodes()

        self._changeSize(newI_nodes, newH_nodes, newO_nodes)

        for i in range(len(self.getData()['inputs'])):
            if self.getI_nodes() > len(self.getData()['inputs'][i]):
                newArray = [0 for x in range(
                    self.getI_nodes() - len(self.getData()['inputs'][i]))]
                for j in range(len(newArray)):
                    newArray[j] = 0
                newArray.extend(self.getData()['inputs'][i])
                self._data['inputs'][i] = newArray
        for i in range(len(self.getData()['outputs'])):
            if self.getO_nodes() > len(self.getData()['outputs'][i]):
                newArray = [0 for x in range(
                    self.getO_nodes() - len(self.getData()['outputs'][i]))]
                for j in range(len(newArray)):
                    newArray[j] = 0
                newArray.extend(self.getData()['outputs'][i])
                self._data['outputs'][i] = newArray

    def train(self, attempts, randomizeNetwork = False):
        if randomizeNetwork:
            cnt = 0
            smallestMSE = self.getMSE()
            smallestMSEJson = self.toJson()
            while cnt < 1000:
                self.randomizeNetwork()
                if self.getMSE() < smallestMSE:
                    print('Smallest MSE found: ' + str(smallestMSE))
                    smallestMSE = self.getMSE()
                    smallestMSEJson = self.toJson()
                cnt += 1
            self.__init__(smallestMSEJson, True)
        cnt = 0
        while cnt < attempts:
            self._practiceData()
            cnt += 1
        self.saveModel()

    def trainToMSE(self, targetMSE):
        startTime = time.time()
        cnt = 0
        while(self.getMSE() > targetMSE):
            self._practiceData()
            cnt += 1
        totalTime = round(time.time() - startTime, 3)
        self.saveModel()
        return 'Trained Succesfully to MSE: ' + str(self.getMSE()) + ', Taked: ' + str(totalTime) + ' seconds, after: ' + str(cnt) + ' attempts'

    def guess(self, input):
        try:
            outputIndex = self.getData()['outputs'].index(self._predict(input))
        except:
            return 'None'

        return self.getData()['meanings'][outputIndex]

    def guessWord(self, sentence):
        guess = self._predict(Network._stringToBinaryArray(sentence))
        index = int(''.join(str(x) for x in guess), 2)
        return self.getData()['meanings'][index]

    def teachWord(self, word):
        self.insertWord(Network._stringToBinaryArray(word), word)

    def toJson(self):
        dict = {
            '_i_nodes': self.getI_nodes(),
            '_h_nodes': self.getH_nodes(),
            '_o_nodes': self.getO_nodes(),

            '_bias_ih': self.getBias_ih().getArray(),
            '_bias_ho': self.getBias_ho().getArray(),

            '_weights_ih': self.getWeights_ih().getArray(),
            '_weights_ho': self.getWeights_ho().getArray(),

            '_learningRate': self.getLearningRate(),
            '_data': self.getData()
        }
        return json.dumps(dict)

    def randomizeNetwork(self):
        self._bias_ih = Matrix.randomMatrix(self._h_nodes, 1)
        self._bias_ho = Matrix.randomMatrix(self._o_nodes, 1)

        self._weights_ih = Matrix.randomMatrix(
            self._h_nodes, self._i_nodes)
        self._weights_ho = Matrix.randomMatrix(
            self._o_nodes, self._h_nodes)

    def printNetworkStatus(self):
        print('MSE: ' + str(self.getMSE()))
        print('Errors: ' + str(self.getErrors()))

    def saveModel(self, modelName='lastModel'):
        path = os.path.dirname(os.path.abspath(__file__)) + '\\models'

        if not os.path.exists(path):
            os.makedirs(path)
        
        f = open(os.path.join(path, modelName + '.txt'), 'w+')
        f.write(self.toJson())
        f.close

    def loadModel(self, modelName):
        path = os.path.dirname(os.path.abspath(__file__)) + '\\models'
        f = open(os.path.join(path, modelName + '.txt'), 'r')
        jsonStr = f.read()
        self.loadJson(jsonStr)

    def loadJson(self, jsonStr):
        dict = json.loads(jsonStr)
        self._i_nodes = dict['_i_nodes']
        self._h_nodes = dict['_h_nodes']
        self._o_nodes = dict['_o_nodes']

        self._bias_ih = Matrix(dict['_bias_ih'])
        self._bias_ho = Matrix(dict['_bias_ho'])

        self._weights_ih = Matrix(dict['_weights_ih'])
        self._weights_ho = Matrix(dict['_weights_ho'])

        self._learningRate = dict['_learningRate']

        self._data = dict['_data']

    # protected Methods

    def _feedForward(self, input):
        input = Matrix(input)

        # Input -> Hidden
        hidden = self.getWeights_ih().mult(input).add(self.getBias_ih()).map(sigmoid)

        # Hidden -> Output
        output = self.getWeights_ho().mult(hidden).add(self.getBias_ho()).map(sigmoid)

        return {'input': input, 'hidden': hidden, 'output': output}

    def _backPropagation(self, feedForward, target):
        target = Matrix(target)

        # Output -> Hidden
        outputError = target.subtract(feedForward['output'])
        d_output = feedForward['output'].map(d_sigmoid)

        gradient_o = outputError.hadamardMult(d_output)
        gradient_o = gradient_o.scaleMult(self.getLearningRate())

        # Bias_ho Adjust
        self._bias_ho = self._bias_ho.add(gradient_o)

        # Weights_ho Adjust
        hidden_t = feedForward['hidden'].transpose()
        weights_ho_deltas = gradient_o.mult(hidden_t)
        self._weights_ho = self._weights_ho.add(weights_ho_deltas)

        # Hidden -> Input
        weights_ho_t = self.getWeights_ho().transpose()
        hiddenError = weights_ho_t.mult(outputError)
        d_hidden = feedForward['hidden'].map(d_sigmoid)

        gradient_h = hiddenError.hadamardMult(d_hidden)
        gradient_h = gradient_h.scaleMult(self.getLearningRate())

        # Bias_ih Adjust
        self._bias_ih = self._bias_ih.add(gradient_h)

        # Weights_ih Adjust
        input_t = feedForward['input'].transpose()
        weights_ih_deltas = gradient_h.mult(input_t)
        self._weights_ih = self._weights_ih.add(weights_ih_deltas)

    def _practice(self, input, target):
        self._backPropagation(self._feedForward(input), target)

    def _practiceData(self):
        for i in range(len(self.getData()['inputs'])):
            self._practice(self.getData()['inputs']
                           [i], self.getData()['outputs'][i])

    def _changeSize(self, i_nodes, h_nodes, o_nodes):
        self._i_nodes = i_nodes
        self._h_nodes = h_nodes
        self._o_nodes = o_nodes

        self._bias_ih = Matrix.randomMatrix(self._h_nodes, 1)
        self._bias_ho = Matrix.randomMatrix(self._o_nodes, 1)

        self._weights_ih = Matrix.randomMatrix(
            self._h_nodes, self._i_nodes)
        self._weights_ho = Matrix.randomMatrix(
            self._o_nodes, self._h_nodes)

    def _predict(self, input):
        array = self._feedForward(input)['output'].getArray()
        binaryArray = []
        for i in range(len(array)):
            binaryArray.append(round(array[i][0]))
        return binaryArray

    # Static Methods

    @staticmethod
    def _stringToBinaryArray(string):
        binaryArray = []
        for i in range(len(string)):
            binaryArray.extend(list(int(x)
                                    for x in bin(ord(string[i:i + 1]))[2:]))
        return binaryArray

    # Getters

    def getMSE(self):
        mse = 0
        for i in range(len(self.getData()['inputs'])):
            for j in range(len(self.getData()['outputs'][i])):
                mse += (self.getData()['outputs'][i][j] - self._feedForward(
                    self.getData()['inputs'][i])['output'].getArray()[j][0])**2
        return round(mse, 5)

    def getErrors(self):
        errors = 0
        for i in range(len(self.getData()['inputs'])):
            for j in range(len(self.getData()['outputs'][i])):
                if self._predict(self.getData()['inputs'][i])[j] != self.getData()['outputs'][i][j]:
                    errors += 1
        return errors

    def getI_nodes(self):
        return self._i_nodes

    def getH_nodes(self):
        return self._h_nodes

    def getO_nodes(self):
        return self._o_nodes

    def getWeights_ih(self):
        return self._weights_ih

    def getWeights_ho(self):
        return self._weights_ho

    def getBias_ih(self):
        return self._bias_ih

    def getBias_ho(self):
        return self._bias_ho

    def getLearningRate(self):
        return self._learningRate

    def getData(self):
        return self._data

    # Setters

    def setLearningRate(self, learningRate):
        self._learningRate = learningRate

    def setH_nodes(self, numH_nodes):
        self._changeSize(self.getI_nodes(), numH_nodes, self.getO_nodes())

# Essencial Class for the Network calculation


class Matrix:

    # Construct
    def __init__(self, array):
        if type(array[0]) == int:
            array = Matrix._arrUniToBi(array)

        self.__array = array
        self.__rows = len(array)
        self.__cols = len(array[0])

    # Normal Methods

    def add(self, matrix):
        array1 = self.getArray()
        array2 = matrix.getArray()

        for i in range(self.getRows()):
            for j in range(self.getCols()):
                array1[i][j] += array2[i][j]

        return Matrix(array1)

    def subtract(self, matrix):
        array1 = self.getArray()
        array2 = matrix.getArray()

        for i in range(self.getRows()):
            for j in range(self.getCols()):
                array1[i][j] -= array2[i][j]

        return Matrix(array1)

    def hadamardMult(self, matrix):
        array1 = self.getArray()
        array2 = matrix.getArray()

        for i in range(self.getRows()):
            for j in range(self.getCols()):
                array1[i][j] *= array2[i][j]

        return Matrix(array1)

    def mult(self, matrix):

        array1 = self.getArray()
        array2 = matrix.getArray()
        if self.getCols() >= matrix.getRows():
            smallestInternal = matrix.getRows()
        else:
            smallestInternal = self.getCols()

        resultArray = [[0 for x in range(matrix.getCols())]
                       for x in range(self.getRows())]

        for i in range(self.getRows()):
            for j in range(matrix.getCols()):
                for internal in range(smallestInternal):
                    resultArray[i][j] += array1[i][internal] * \
                        array2[internal][j]
        return Matrix(resultArray)

    def scaleMult(self, number):
        array1 = self.getArray()

        for i in range(self.getRows()):
            for j in range(self.getCols()):
                array1[i][j] *= number

        return Matrix(array1)

    def transpose(self):
        array = self.getArray()
        transposedArray = [
            [0 for x in range(self.getRows())] for x in range(self.getCols())]

        for i in range(self.getRows()):
            for j in range(self.getCols()):
                transposedArray[j][i] = array[i][j]
        return Matrix(transposedArray)

    def map(self, function):
        return Matrix.mapMatrix(self, function)

    # Static Methods

    @staticmethod
    def _arrUniToBi(array):
        biArray = [[0 for x in range(1)] for x in range(len(array))]
        for i in range(len(array)):
            biArray[i][0] = array[i]
        return biArray

    @staticmethod
    def mapMatrix(matrix, function):
        array = matrix.getArray()
        for i in range(matrix.getRows()):
            for j in range(matrix.getCols()):
                array[i][j] = function(array[i][j])
        return Matrix(array)

    @staticmethod
    def randomArray(rows, cols):
        array = [[0 for x in range(cols)] for x in range(rows)]

        for i in range(rows):
            for j in range(cols):
                array[i][j] = random.randint(-10, 10) / 10
        return array

    @staticmethod
    def randomMatrix(rows, cols):
        return Matrix(Matrix.randomArray(rows, cols))

    # Getters

    def getArray(self):
        return self.__array

    def getRows(self):
        return self.__rows

    def getCols(self):
        return self.__cols

    # Setter
    def setMatrix(self, array):
        if type(array[0]) == int:
            array = Matrix._arrUniToBi(array)

        self.__array = array
        self.__rows = len(array)
        self.__cols = len(array[0])

# Math functions for the Network


def sigmoid(val):
    if val < -705:
        val = -705
    return 1 / (1 + math.exp(-val))


def d_sigmoid(val):
    return val * (1 - val)
