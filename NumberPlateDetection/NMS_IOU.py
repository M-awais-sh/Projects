import numpy as np
import matplotlib.pyplot as plt

def NMS(boxes, overlapThresh):
    if len(boxes) == 0:
        return []

    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    pick = []

    x1 = boxes[:, 0] # top left x pixel of all 10 boxes
    y1 = boxes[:, 1] # top left y pixel of all 10 boxes
    x2 = boxes[:, 2] # bottom right x pixel of all 10 boxes
    y2 = boxes[:, 3] # bottom right y pixel of all 10 boxes

    area = (x2 - x1 + 1) * (y2 - y1 + 1) # width * height of all 10 boxes
    idxs = np.argsort(y2)  #sort based on the bottom right y pixel of all 10 boxes

    while len(idxs) > 0: #10 times
        last = len(idxs) - 1 #index of the last box in the sorted list 9
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.maximum(x2[i], x2[idxs[:last]])
        yy2 = np.maximum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[:last]]

        idxs = np.delete(
            idxs, np.concatenate(([last], np.where(overlap > overlapThresh)[0]))
        )

    return boxes[pick]

def IoU(boxA, boxB):
    # boxA and boxB are in the format [x1, y1, x2, y2]
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # Compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    # Compute the area of both the prediction and ground-truth rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    # Compute the intersection over union by taking the intersection area and dividing it by the sum of prediction + ground-truth areas - the interesection area
    iou = float(interArea) / (float(boxAArea + boxBArea - interArea))

    return iou

if __name__ == "__main__":
    boxes = np.array([[12, 84, 140, 212],
                      [24, 84, 152, 212],
                      [36, 84, 164, 212],
                      [12, 96, 140, 224],
                      [24, 96, 152, 224],
                      [24, 108, 152, 236],
                      [12, 120, 140, 248],
                      [36, 120, 164, 248],
                      [24, 132, 152, 260],
                      [36, 132, 164, 260]])

    print("Original boxes:")
    print(boxes)

    nms_boxes = NMS(boxes, overlapThresh=0.3)
    print("\nBoxes after NMS:")
    print(nms_boxes)

    boxA = [12, 84, 140, 212]
    boxB = [24, 84, 152, 212]
    iou_value = IoU(boxA, boxB)
    print(f"\nIoU between boxA and boxB: {iou_value:.4f}")