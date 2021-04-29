import cv2
from datetime import datetime
import time

import imutils as imutils
import numpy as np

location1 = []
location2 = []
speeds = []

# Amount of cars detected
carsCounted = 0

time1 = 0
time2 = 0


frameW = 1280
frameH = 720


# Start- and end-points for lines on image
start1 = (frameW//4, 0)
end1 = (frameW//4, frameH)
start2 = ((frameW//4)*3, 0)
end2 = ((frameW//4)*3, frameH)


# Calculates and returns the centroid of the given inputs
def get_centroid(x, y, w, h):
    tx = x+(w//2)
    ty = y+(h//2)

    return tx, ty


def estimateSpeed():
    t1, x1 = location1[-1]
    t2, x2 = location2[-1]

    # Distance from one side of the frame to the other in m
    distance = 25

    ppm = frameW/distance

    # Delta time in frames
    d_t = abs(t2 - t1)

    # Delta x in pixels
    d_x = abs(x2 - x1)

    # Pixels per frame
    ppf = (d_x/d_t)
    # ppf -> Meters per frame
    mpf = (ppf/ppm)
    # mpf -> Meters per second (multiply by framerate)
    mps = mpf*30
    # mps -> kmt
    kmt = mps*3.6

    speeds.append(int(kmt))
    print(speeds[-1])


def storeCentroid(tx, ty, frame_number):
    global carsCounted
    global time1
    global time2
    if 0 < tx < frameW//4:
        if time.time() >= (time1 + 1):
            if len(location1) == carsCounted:
                location1.append((frame_number,tx))
                time1 = time.time()
                carsCounted = carsCounted + 1
            elif len(location2) > len(location1):
                location1.append((frame_number,tx))
                time1 = time.time()
                estimateSpeed()

    elif (frameW//4)*3 < tx < frameW:
        if time.time() >= (time2 + 1):
            if len(location2) == carsCounted:
                location2.append((frame_number,tx))
                time2 = time.time()
                carsCounted = carsCounted + 1
            elif len(location1) > len(location2):
                location2.append((frame_number,tx))
                time2 = time.time()
                estimateSpeed()


def detectCar2(frame, first_frame, frame_number):
    # Grey image of the current frame
    gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Performs gaussian blur on the frame
    gray2 = cv2.GaussianBlur(gray1, (21, 21), 0)

    # Absolute difference from the first image and the current frame
    diff_frame = cv2.absdiff(gray2, first_frame)

    # Binary image of the absolute difference
    thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # Finding contour of object
    contours, _ = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        if cv2.contourArea(contour)<5000:
            continue

        # Get centroid of the object
        tx , ty = get_centroid(x, y, w, h)
        cv2.rectangle(frame, (x, y), (x + w - 1, y + h - 1), (255, 0, 0), 2)
        storeCentroid(tx, ty, frame_number)


def showStream(frame):
    # Draw lines for speed estimation
    cv2.line(frame, start1, end1, (255,0,0), 2)
    cv2.line(frame, start2, end2, (255,0,0), 2)

    #Add text to image
    if len(speeds) > 0:
        speed = ("Last recorded speed was: ", str(speeds[-1]), " km/t")
        speedStr = "".join(speed)
        cv2.putText(frame, speedStr, (0, 60), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0))
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, ts, (0, 25), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0))
    cv2.imshow("Frame", frame)


def startTracker():
    # Change cv2.VideoCapture() input to either cam to use camera or carVid to get the Video given
    global time1, time2
    time1 = time.time()
    time2 = time.time()
    carVid = 'cars3.mp4'
    cam = 0
    vid = cv2.VideoCapture(carVid)
    frame_number = -1
    first_frame = None
    time.sleep(1)
    while True:
        # Capture the video frame by frame
        frame_number += 1
        _, frame = vid.read()

        if type(frame) == type(None):
            break

        frame = cv2.resize(frame, (frameW, frameH))

        # Stores the first frame of the video
        if first_frame is None:
            f1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            f1b = cv2.GaussianBlur(f1, (21, 21), 0)
            first_frame = f1b

        detectCar2(frame, first_frame, frame_number)

        showStream(frame)

        # Quits when the q button is pressed.
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    print('Closing video capture..')
    vid.release()
    cv2.destroyAllWindows()
    print('Done.')


if __name__ == '__main__':
    startTracker()
