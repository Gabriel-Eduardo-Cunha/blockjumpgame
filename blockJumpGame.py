from graphics import GraphWin, Rectangle, Point, color_rgb, Text
import time
import random

class BlockJumpGame(GraphWin):
    def __init__(self, maxFrameRate = 80, screenSize = [800, 600], initialGameSpeed = 20, playerStartinPoint = [70, 540], playerSize = 50):
        GraphWin.__init__(self, 'Block-Jump-Game', screenSize[0], screenSize[1])
        self.gameConfig = {
            'maxFrameRate' : maxFrameRate,
            'screenSize' : screenSize,
            'initialGameSpeed' : initialGameSpeed,
            'playerStartingPoint' : playerStartinPoint,
            'playerSize' : playerSize
        }
        self.player = Rectangle(Point(playerStartinPoint[0], playerStartinPoint[1]), Point(
            playerStartinPoint[0] + playerSize, playerStartinPoint[1] + playerSize))
        self.player.setFill(color_rgb(255, 0, 0))
        self.player.setOutline(color_rgb(0, 0, 0))
        self.player.draw(self)
        self.playerSpeed = 0
        self.initialGameSpeed = initialGameSpeed
        self.gameSpeed = initialGameSpeed
        self.groundLevel = self.getHeight() - 7
        self.obstacle = None
        self.createObstacle()

        self.points = 0
        self.maxFrameRate = maxFrameRate

        self.pointsText = Text(Point(
            0 + screenSize[0] / 10, 0 + screenSize[0] / 50), 'Points: ' + str(self.points))
        self.pointsText.draw(self)

        self.playerStatus = 'nothing'

        self.timeWhenGameStarted = time.time()
        self.gameEnd = False
        self.start()

    def start(self):
        while self.gameEnd == False:
            self.render()

    def render(self):
        self.checkPoints()
        self.refreshHUD()
        self.checkObstacle()
        self.detectInput()
        self.moveObjects()
        self.playerFall()
        self.addPoints()
        self.checkColisions()
        time.sleep(1/self.maxFrameRate)

    def checkColisions(self):
        if self.obstacle != None:
            if self.player.getP2().getX() > self.obstacle.getP1().getX() and self.player.getP1().getX() < self.obstacle.getP1().getX() or self.player.getP2().getX() > self.obstacle.getP2().getX() and self.player.getP1().getX() < self.obstacle.getP2().getX() or self.player.getP2().getX() > self.obstacle.getCenter().getX() and self.player.getP1().getX() < self.obstacle.getCenter().getX():
                if self.player.getP2().getY() > self.obstacle.getP1().getY():
                    self.gameOver()

    def gameOver(self):
        self.player.undraw()
        self.gameOverText = Text(
            Point(self.getWidth() / 2, self.getHeight() / 2), 'Game Over\nPress R to restart\nor press any key to quit')
        self.gameOverText.draw(self)
        key = self.getKey()
        self.gameEnd = True
        print('XXXXXXXXXXXXXXXXXXXXXXXXX')
        print('------Game Status------')
        print('Points: ' + str(round(self.points)))
        print('Played for: ' + str(round(time.time() - self.timeWhenGameStarted)) + ' seconds')
        print('XXXXXXXXXXXXXXXXXXXXXXXXX')
        if key == 'r':
            self.restart()
        else:
            self.close()

    def refreshHUD(self):
        self.pointsText.setText('Points: ' + str(round(self.points)))

    def checkPoints(self):
        if int(self.points / 10) - (self.gameSpeed - self.initialGameSpeed) == 1:
            self.gameSpeed += 1

    def addPoints(self):
        self.points += 1/self.maxFrameRate * self.gameSpeed/10

    def detectInput(self):
        input = self.checkKey()
        if input == 'Up' and self.playerStatus == 'nothing':
            self.playerJump()
            self.playerStatus = 'jumping'
        if input == 'Down' and self.playerStatus == 'jumping':
            if self.playerSpeed < 0:
                self.playerSpeed = 0
            self.playerStatus = 'fastfall'

    def checkObstacle(self):
        if self.obstacle != None:
            if self.obstacle.getCenter().getX() < - self.obstacleWidth + 10:
                self.obstacle.undraw()
                self.obstacle = None
                self.createObstacle()

    def createObstacle(self):
        height = random.randint(75, 150)
        if self.gameSpeed > 50:
            width = random.randint(150,400)
        elif self.gameSpeed > 30: 
            width = random.randint(100,300) 
        else:
            width = random.randint(75,150)
        self.obstacleHeight = height 
        self.obstacleWidth = width
        self.obstacle = Rectangle(Point(
            self.getWidth(), self.getHeight() - self.obstacleHeight), Point(self.getWidth() + self.obstacleWidth, self.getHeight()))
        self.obstacle.setFill(color_rgb(random.randint(
            0, 255), random.randint(0, 255), random.randint(0, 255)))
        self.obstacle.draw(self)

    def moveObjects(self):
        self.player.move(0, round(self.playerSpeed/self.maxFrameRate, 1))
        if self.player.getP2().getY() >= self.groundLevel:
            self.player.move(0, self.groundLevel - self.player.getP2().getY())
            self.playerSpeed = 0
            self.playerStatus = 'nothing'

        if self.obstacle != None:
            self.obstacle.move(-self.gameSpeed*10/self.maxFrameRate, 0)

    def playerJump(self):
        if self.playerStatus == 'nothing':
            self.playerSpeed = -480

    def playerFall(self):
        if self.playerStatus == 'jumping':
            self.playerSpeed += round(480/self.maxFrameRate,1)
        if self.playerStatus == 'fastfall':
            self.playerSpeed += round(4800/self.maxFrameRate,1)

    def restart(self):

        self.player = Rectangle(Point(self.gameConfig['playerStartingPoint'][0], self.gameConfig['playerStartingPoint'][1]), Point(
            self.gameConfig['playerStartingPoint'][0] + self.gameConfig['playerSize'], self.gameConfig['playerStartingPoint'][1] + self.gameConfig['playerSize']))
        self.player.setFill(color_rgb(255, 0, 0))
        self.player.setOutline(color_rgb(0, 0, 0))
        self.player.draw(self)
        self.playerSpeed = 0
        self.gameSpeed = self.initialGameSpeed
        self.groundLevel = self.getHeight() - 7
        self.obstacle.undraw()
        self.gameOverText.undraw()
        self.obstacle = None
        self.createObstacle()

        self.points = 0
        
        self.pointsText.undraw()
        self.pointsText = Text(Point(
            0 + self.getWidth() / 10, 0 + self.getWidth() / 50), 'Points: ' + str(self.points))
        self.pointsText.draw(self)

        self.playerStatus = 'nothing'

        self.timeWhenGameStarted = time.time()
        self.gameEnd = False
        self.start()
            

