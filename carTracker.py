import numpy as np
import cv2
import math


class car:
    def __init__(self, carID, location, start_frame):
        self.id = carID
        self.locations = [location]
        self.frame_last_seen = 0
        self.start_frame = start_frame
        self.speed = None
        # assign a random color for the car
        self.color = (np.random.randint(255), np.random.randint(255), np.random.randint(255))

    def last_location(self):
        return self.locations[-1]

    def add_location(self, new_location):
        self.locations.append(new_location)
        self.frame_last_seen = 0

    def estimateSpeed(self, frame_number):
        ppm = 9  # pixels per meter, regn ut på noe vis.
        dx = self.last_location()[1] - self.locations[0][1]
        dy = self.last_location()[1] - self.locations[0][1]
        distanceInPixels = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
        distanceInMeters = distanceInPixels / ppm
        time = frame_number - self.start_frame
        self.speed = distanceInMeters * time * 3.6

    def draw(self, outputImg):
        cv2.putText(outputImg, str(self.speed), self.last_location(), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))


class carArray:
    def __init__(self):
        self.max_unseen_frames = 10  # frames car has to be gone from the frame before removing
        self.cars = []
        self.nextCarID = 0

    def update_cars(car, carsInFrame):
        # Find if any of the matches fits this vehicle
        for i, match in enumerate(carsInFrame):
            contour, centroid = match
            print(centroid)
            if car.last_location() == centroid:
                car.add_location(centroid)

                return i
        # No matches fit
        # print('No matches found for vehicle %s' % vehicle.id)
        car.frame_last_seen += 1

        return None

    def register(self, centroid, start_frame):
        new_car = car(self.nextCarID, centroid, start_frame)
        self.cars.append(new_car)
        self.nextCarID += 1

    def update(self, carsInFrame, outputImg, frame_num):
        for car in self.cars:
            i = self.update_cars(car, carsInFrame)
            if i is not None:
                del carsInFrame[i]

        for matches in carsInFrame:
            contour, centroid = matches
            self.register(centroid, frame_num)

        if outputImg is not None:
            for car in self.cars:
                car.estimateSpeed(frame_num)
                car.draw(outputImg)

        self.cars[:] = [car for car in self.cars if car.frame_last_seen < self.max_unseen_frames]