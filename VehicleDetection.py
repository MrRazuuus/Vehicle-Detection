import cv2
from datetime import datetime
from carTracker import carArray

frameW = 1280
frameH = 720

cars_cascade = cv2.CascadeClassifier('cars.xml')


# Calculates and returns the centroid of the given inputs
def get_centroid(x, y, w, h):
    tx = x+(w//2)
    ty = y+(h//2)

    return tx, ty


def detectCar(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cars = cars_cascade.detectMultiScale(gray, 1.2, 5, 30)
    carsSeen = []
    for x, y, w, h in cars:
        if (w > 75) & (h > 75):
            tx, ty = get_centroid(x, y, w, h)
            cv2.rectangle(frame, (x, y), (x + w - 1, y + h - 1), (255, 0, 0), 2)
            carsSeen.append(((x, y, w, h), (tx, ty)))
    return carsSeen


def detectCar2(frame, frame_number):
    global first_frame;
    carsSeen = []
    if frame_number == 0: # Checks if its the first frame.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        print("hello")
        first_frame = gray

    else:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        cv2.imshow("binary", first_frame)
        diff_frame = cv2.absdiff(gray, first_frame)

        thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

        # Finding contour of moving object
        contours, _ = cv2.findContours(thresh_frame.copy(),
                                   cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for x, y, w, h in contours:
            if (w > 75) & (h > 75):
                tx, ty = get_centroid(x, y, w, h)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                carsSeen.append(((x, y, w, h), (tx, ty)))
    return carsSeen


def showStream(frame):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, ts, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
    cv2.imshow("Frame", frame)


def startTracker():
    # Change cv2.VideoCapture() input to either cam to use camera or carVid to get the Video given
    carVid = 'cars2.mp4'
    cam = 0
    vid = cv2.VideoCapture(carVid)
    frame_number = -1

    while True:
        # Capture the video frame by frame
        frame_number += 1
        ret, frame = vid.read()
        if type(frame) == type(None):
            break

        carArr = carArray()

        #carsInFrame = detectCar(frame)
        carsInFrame2 = detectCar2(frame, frame_number)

        carArr.update(carsInFrame2, frame, frame_number)

        #showStream(frame)

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
