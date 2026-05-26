import cv2 
import numpy as np
import pandas as pd
from sklearn.datasets import load_files
from lab17_NMS_IOU import IoU, NMS


def load_data():
    data = load_files('Used_cars/')
    filenames = np.array(data['filenames'])
    x = []
    y = []
    not_count = 0
    for name in filenames:
        if 'No' in name:
            not_count += 1
            if not_count < 2300:
                img = cv2.imread(name)
                x.append(img)
                y.append(0)
            else:
                pass
        else:
            img = cv2.imread(name)
            x.append(img)
            y.append(1)
    x = np.asarray(x)
    y = np.asarray(y)
    return x, y

if __name__ == "__main__":
    data = pd.read_csv('numberplates/annotations.csv')
    allnames = data.iloc[:,[0]].values
    box_list = data.iloc[:,[3,4,5,6]]
    allnames = np.ndarray.flatten(allnames)
    print(allnames)
    print(box_list)

    car_save_path = 'Used_cars/plate/'
    no_car_save_path = 'Used_cars/no_plate/'

    total_car = 0
    total_no_car = 0

    for i in range(len(allnames)): #50 images
        file = allnames[i] #car0.png
        ss = cv2.ximgproc.segmentation.createSelectiveSearchSegmentation()
        img = cv2.imread('numberplates/' + file)
        img_copy = img.copy()
        ss.setBaseImage(img)
        ss.switchToSelectiveSearchFast()
        results = ss.process() # RoI proposals (x1, y1, w, h)
        car_count = 0
        no_car_count = 0
        total_counted = 0
        for box in results: #for every RoI proposal
            found_box_use = [box[0], box[1], box[0]+box[2], box[1]+box[3]] #x1, y1, x2, 
            image_roi = img_copy[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
            iou = IoU(found_box_use, box_list.iloc[i].values)
            if iou > 0.7 and car_count < 16:
                image_roi_use = cv2.resize(image_roi, (128, 128))
                image_roi_use = image_roi_use.reshape((128, 128, 3))
                cv2.imwrite(car_save_path + 'Plate' + str(total_car) + '.png', image_roi_use)
                car_count += 1
                total_car += 1
            elif iou < 0.3 and no_car_count < 16:
                image_roi_use = cv2.resize(image_roi, (128, 128))
                image_roi_use = image_roi_use.reshape((128, 128, 3))
                cv2.imwrite(no_car_save_path + 'No_Plate' + str(total_no_car) + '.png', image_roi_use)
                no_car_count += 1
                total_no_car += 1
            if total_counted > 999:
                break
            total_counted += 1
            #32 * 50 = 1600
    x, y = load_data()
    print(x.shape)
    print(y.shape)
