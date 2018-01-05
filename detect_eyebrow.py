# import the necessary packages
from imutils.video import VideoStream
from imutils import face_utils
import math
import datetime
import argparse
import imutils
import time
import dlib
import cv2

shape_predictor = "./predictor/shape_predictor_68_face_landmarks.dat"

#Class to keep the direction of the eyebrow movment
class Eyebrow(object):
	"""docstring for Eyebrow"""
	def __init__(self):
		self.direction = 0
	
	def defineDirection(self,direction):
		self.direction = direction

	def getDirection(self):
		return self.direction	

# Define class that will contain the direction of the eyebrow
eyebrow = Eyebrow()

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor)

# initialize the video stream and allow the cammera sensor to warmup
print("[INFO] camera sensor warming up...")
vs = VideoStream(0).start()
time.sleep(2.0)


# grab the indexes of the facial landmarks for the left and
# right eyebrows, respectively
(lbStart, lbEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eyebrow"]
(rbStart, rbEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eyebrow"]

#Get the indexes of the nose line
(nStart, nEnd) = face_utils.FACIAL_LANDMARKS_IDXS["nose"]

#Get the mid indexes of the facial landmarks
lbMid = int((lbStart + lbEnd)/2)
rbMid = int((rbStart + rbEnd)/2)
nMid = int((nStart + nEnd)/2)

# Define variables that will contain the euclidean distances
rightEyebrowToNose = 0
leftEyebrowToNose = 0

# Defining variables to control if the face got closer or further away
oldNosePosition = (0,0)
currentNosePosition = 0

def distance(A, B):
	(ax,ay) = A
	(bx,by) = B
	return math.sqrt((ax-bx)**2 + (ay-by)**2)

def eyebrowDetection():
	global lbMid, rbMid, nMid, rightEyebrowToNose, leftEyebrowToNose, oldNosePosition, currentNosePosition
	# loop over the frames from the video stream
	while True:
		# grab the frame from the threaded video stream, resize it to
		# have a maximum width of 400 pixels, and convert it to
		# grayscale
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# detect faces in the grayscale frame
		rects = detector(gray, 0)

	    # loop over the face detections
		for rect in rects:
			# determine the facial landmarks for the face region, then
			# convert the facial landmark (x, y)-coordinates to a NumPy
			# array
			shape = predictor(gray, rect)
			shape = face_utils.shape_to_np(shape)

			# Get the positions of the 
			leftEyebrowCoordinates = shape[lbMid]
			rightEyebrowCoordinates = shape[rbMid]
			currentNosePosition = midPointNoseCoordinates = shape[nMid]

			currentRightEyebrowDistance = distance(rightEyebrowCoordinates,midPointNoseCoordinates)
			currentLeftEyebrowDistance = distance(leftEyebrowCoordinates,midPointNoseCoordinates)

			if (rightEyebrowToNose == 0) or (leftEyebrowToNose == 0):
			    rightEyebrowToNose = distance(rightEyebrowCoordinates,midPointNoseCoordinates)
			    leftEyebrowToNose = distance(leftEyebrowCoordinates,midPointNoseCoordinates)
			elif (currentRightEyebrowDistance > rightEyebrowToNose) or (currentLeftEyebrowDistance > leftEyebrowToNose):
				eyebrow.defineDirection(1)
				print ("[RESULT] UP")
			else:
				eyebrow.defineDirection(-1)
				print ("[RESULT] DOWN")

			# If the person moved(the nose postion moved), calculates the distance between it's old postion
			# and the new one. If it's bigger than '8' define the new standard positions
			# the smaller the number the more precise the algorithm gets
			movementDistanceOfNose = distance(currentNosePosition , oldNosePosition)

			if movementDistanceOfNose > 5:
				oldNosePosition = currentNosePosition
				print("[INFO] Nose position updated")
				rightEyebrowToNose = distance(rightEyebrowCoordinates,midPointNoseCoordinates)
				leftEyebrowToNose = distance(leftEyebrowCoordinates,midPointNoseCoordinates)	

			print ("[INFO] Normal left 2 Nose Disance: %d\n[INFO] Normal nose position: (%d,%d)" % (leftEyebrowToNose,midPointNoseCoordinates[0],midPointNoseCoordinates[1]))

			# loop over the (x, y)-coordinates for the facial landmarks
			# and draw them on the image
			for (x, y) in leftEyebrowCoordinates,rightEyebrowCoordinates,midPointNoseCoordinates:
				cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

		# show the frame
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			closeDetectionWindows()
			break

def closeDetectionWindows():
	# do a bit of cleanup
	cv2.destroyAllWindows()
	vs.stop()
