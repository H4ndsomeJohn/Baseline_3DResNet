import os
import pickle
import random

import numpy as np
import torch
from sklearn.model_selection import KFold
from torch.utils.data import DataLoader, Dataset

import config


class Res3D_Dataset(Dataset):
    def __init__(self, data_type: str, fold_idx=0):
        super(Res3D_Dataset, self).__init__()
        subject_files = np.array(os.listdir(config.PATH))
        kf = KFold(n_splits=5, shuffle=True, random_state=config.SEED_DIVIDE)
        train_index, val_index, test_index = [], [], []
        for idx in range(5):
            _, files_index = list(kf.split(subject_files))[idx]
            if idx != fold_idx:
                train_index += list(files_index)
                if val_index == []:
                    val_index = files_index
            else:
                test_index = files_index

        if data_type == "train":
            train_index = np.array(train_index)
            input_list = subject_files[train_index]
        elif data_type == "val":
            input_list = subject_files[val_index]
        elif data_type == "test":
            input_list = subject_files[test_index]
        else:
            print("Wrong dataset type")
            exit()
        self.f = input_list

    def __len__(self):
        return len(self.f)

    def __getitem__(self, idx):
        with open(config.PATH + self.f[idx], "rb") as f:
            data = pickle.load(f)
        input = data["patch"] * data["mask"]
        input = input.reshape([1, *data["patch"].shape])
        return (
            torch.tensor(input, dtype=torch.float32),
            data["label"],
        )


def Res3D_Dataloader(bs=4, fold_idx=0, num_workers=8):
    dataset = {}
    type_list = ["train", "val", "test"]
    for item in type_list:
        dataset[item] = DataLoader(
            Res3D_Dataset(data_type=item, fold_idx=fold_idx),
            batch_size=bs,
            shuffle=True,
            num_workers=num_workers,
        )
    return dataset
