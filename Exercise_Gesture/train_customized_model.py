import torch
import torch.nn as nn
import numpy as np
import joblib
import albumentations
import torch.optim as optim
import os
import cnn_models
import matplotlib
import matplotlib.pyplot as plt
import time
import pandas as pd
import PIL.Image
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

matplotlib.style.use('ggplot')

# This code is based on this tutorial with some modifications:
# https://debuggercafe.com/action-recognition-in-videos-using-deep-learning-and-pytorch/

class ImageDataset(Dataset):
    def __init__(self, images, labels=None, tfms=None):
        self.X = images
        self.y = labels
        self.aug = albumentations.Compose([albumentations.Resize(224, 224, always_apply=True)])

    def __len__(self):
        return (len(self.X))

    def __getitem__(self, i):
        image = PIL.Image.open(self.X[i])
        image = image.convert('RGB')
        image = self.aug(image=np.array(image))['image']
        image = np.transpose(image, (2, 0, 1)).astype(np.float32)
        label = self.y[i]
        return torch.tensor(image, dtype=torch.float), torch.tensor(label, dtype=torch.long)

class CustomizedModel:
    def __init__(self, motionType):
        self.motionType = motionType
        self.prepare_data()
        self.lr = 1e-3
        self.batch_size = 32
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.lb = joblib.load('models/customized/' + self.motionType + '/outputs/lb_' + self.motionType + '.pkl')
        self.model = cnn_models.CustomCNN(self.lb).to(self.device)

        self.epochs = 75
        self.epoch = 0

        df = pd.read_csv('models/customized/' + self.motionType + '/input/data_' + self.motionType + '.csv')
        X = df.image_path.values
        y = df.target.values
        (xtrain, xtest, ytrain, ytest) = train_test_split(X, y, test_size=0.10, random_state=42)
        print(f"Training instances: {len(xtrain)}")
        print(f"Validation instances: {len(xtest)}")

        self.train_data = ImageDataset(xtrain, ytrain, tfms=1)
        self.test_data = ImageDataset(xtest, ytest, tfms=0)

        self.trainloader = DataLoader(self.train_data, batch_size=self.batch_size, shuffle=True)
        self.testloader = DataLoader(self.test_data, batch_size=self.batch_size, shuffle=False)

        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"{total_params:,} total parameters.")
        total_trainable_params = sum(
            p.numel() for p in self.model.parameters() if p.requires_grad)
        print(f"{total_trainable_params:,} training parameters.")

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

        self.criterion = nn.CrossEntropyLoss()

        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            patience=5,
            factor=0.5,
            min_lr=1e-6,
            verbose=True
        )

    def prepare_data(self):
        all_paths = os.listdir('models/customized/' + self.motionType + '/input/')
        folder_paths = [x for x in all_paths if os.path.isdir('models/customized/' + self.motionType + '/input/' + x)]
        print(f"Folder paths: {folder_paths}")
        print(f"Number of folders: {len(folder_paths)}")

        create_labels = ['0', '1']

        data = pd.DataFrame()

        image_formats = ['jpg']
        labels = []
        counter = 0
        for i, folder_path in tqdm(enumerate(folder_paths), total=len(folder_paths)):
            if folder_path not in create_labels:
                continue
            image_paths = os.listdir('models/customized/' + self.motionType + '/input/' + folder_path)
            label = folder_path

            for image_path in image_paths:
                if image_path.split('.')[-1] in image_formats:
                    data.loc[
                        counter, 'image_path'] = f"models/customized/" + self.motionType + f"/input/{folder_path}/{image_path}"
                    labels.append(label)
                    counter += 1

        labels = np.array(labels)
        lb = LabelBinarizer()
        labels = lb.fit_transform(labels)

        if len(labels[0]) == 1:
            for i in range(len(labels)):
                index = labels[i]
                data.loc[i, 'target'] = int(index)
        elif len(labels[0]) > 1:
            for i in range(len(labels)):
                index = np.argmax(labels[i])
                data.loc[i, 'target'] = int(index)

        data = data.sample(frac=1).reset_index(drop=True)
        print(f"Number of labels or classes: {len(lb.classes_)}")
        print(f"The first one hot encoded labels: {labels[0]}")
        print(f"Mapping the first one hot encoded label to its category: {lb.classes_[0]}")
        print(f"Total instances: {len(data)}")

        data.to_csv('models/customized/' + self.motionType + '/input/data_' + self.motionType + '.csv', index=False)

        print('Saving the binarized labels as pickled file')
        joblib.dump(lb, 'models/customized/' + self.motionType + '/outputs/lb_' + self.motionType + '.pkl')

        print(data.head(5))

    def fit(self):
        print('Training')
        self.model.train()
        train_running_loss = 0.0
        train_running_correct = 0
        for i, data in tqdm(enumerate(self.trainloader), total=int(len(self.train_data) / self.trainloader.batch_size)):
            data, target = data[0].to(self.device), data[1].to(self.device)
            self.optimizer.zero_grad()
            outputs = self.model(data)
            loss = self.criterion(outputs, target)
            train_running_loss += loss.item()
            _, preds = torch.max(outputs.data, 1)
            train_running_correct += (preds == target).sum().item()
            loss.backward()
            self.optimizer.step()

        train_loss = train_running_loss / len(self.trainloader.dataset)
        train_accuracy = 100. * train_running_correct / len(self.trainloader.dataset)

        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_accuracy:.2f}")

        return train_loss, train_accuracy

    def validate(self):
        print('Validating')
        self.model.eval()
        val_running_loss = 0.0
        val_running_correct = 0
        with torch.no_grad():
            for i, data in tqdm(enumerate(self.testloader),
                                total=int(len(self.test_data) / self.testloader.batch_size)):
                data, target = data[0].to(self.device), data[1].to(self.device)
                outputs = self.model(data)
                loss = self.criterion(outputs, target)

                val_running_loss += loss.item()
                _, preds = torch.max(outputs.data, 1)
                val_running_correct += (preds == target).sum().item()

            val_loss = val_running_loss / len(self.testloader.dataset)
            val_accuracy = 100. * val_running_correct / len(self.testloader.dataset)
            print(f'Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.2f}')

            return val_loss, val_accuracy

    def train(self):
        train_loss, train_accuracy = [], []
        val_loss, val_accuracy = [], []
        start = time.time()
        for self.epoch in range(self.epochs):
            print(f"Epoch {self.epoch + 1} of " + str(self.epochs))
            train_epoch_loss, train_epoch_accuracy = self.fit()
            val_epoch_loss, val_epoch_accuracy = self.validate()
            train_loss.append(train_epoch_loss)
            train_accuracy.append(train_epoch_accuracy)
            val_loss.append(val_epoch_loss)
            val_accuracy.append(val_epoch_accuracy)
            self.scheduler.step(val_epoch_loss)
        end = time.time()
        print(f"{(end - start) / 60:.3f} minutes")

        plt.figure(figsize=(10, 7))
        plt.plot(train_accuracy, color='green', label='train accuracy')
        plt.plot(val_accuracy, color='blue', label='validataion accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.savefig('models/customized/' + self.motionType + '/outputs/accuracy_' + self.motionType + '.png')

        plt.figure(figsize=(10, 7))
        plt.plot(train_loss, color='orange', label='train loss')
        plt.plot(val_loss, color='red', label='validataion loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.savefig('models/customized/' + self.motionType + '/outputs/loss_' + self.motionType + '.png')

        print('Saving model...')
        torch.save(self.model.state_dict(),
                   'models/customized/' + self.motionType + '/outputs/' + self.motionType + '.pth')

        print('TRAINING COMPLETE')
