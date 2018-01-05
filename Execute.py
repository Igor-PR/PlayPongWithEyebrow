from threading import *

import pong 
import detect_eyebrow as eyebrowDetection

class GameThread(Thread):	
	def run(self):
		pong.startGame()

class EyebrowDetectionThread(Thread):
	def run(self):
		eyebrowDetection.eyebrowDetection()

gameThread = GameThread()
gameThread.deamon = True
detection = EyebrowDetectionThread()

detection.start()
gameThread.start()

while (detection.isAlive()):
	pong.playerMovement(eyebrowDetection.eyebrow.getDirection())

pong.DetectionEnded = True