import torch
import numpy as np
import joblib
import cnn_models
import albumentations
import cv2
from PIL import Image


def most_frequent(List):
    return max(set(List), key=List.count)


class DefaultExerciseDetection:
    def __init__(self, motionType):
        self.motionType = motionType.replace(" ", "").lower()
        self.status = 0
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.lb = joblib.load("models/default/" + motionType + "/lb_" + self.motionType + ".pkl")
        self.model = cnn_models.CustomCNN(self.lb)
        self.model.load_state_dict(torch.load("models/default/" + motionType + "/" + self.motionType + ".pth"))
        self.aug = albumentations.Compose([albumentations.Resize(224, 224)])
        self.model = self.model.eval().to(self.device)
        self.labels = []
        self.isPressed = False

    def detect(self, frame):
        with torch.no_grad():
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            pil_image = self.aug(image=np.array(pil_image))['image']
            pil_image = np.transpose(pil_image, (2, 0, 1)).astype(np.float32)
            pil_image = torch.tensor(pil_image, dtype=torch.float)
            pil_image = pil_image.unsqueeze(0)
            outputs = self.model(pil_image)
            _, preds = torch.max(outputs.data, 1)
        label = self.lb.classes_[preds]
        self.labels.append(label)
        if len(self.labels) == 6:
            label = most_frequent(self.labels)
            if int(label) == 1:
                self.status = 1
            else:
                self.status = 0
            self.labels.pop(0)
            return self.status
