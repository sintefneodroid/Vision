#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 19/07/2020
           """

import torch
from neodroidvision.segmentation import dice_loss
from neodroidvision.segmentation.fully_convolutional import FCN
from torch.optim import Adam

if __name__ == "__main__":
    def a():
        img_size = 224
        in_channels = 5
        n_classes = 2
        metrics = dice_loss

        if n_classes == 1:
            # loss = 'binary_crossentropy'
            loss = torch.nn.BCELoss()
            final_act = torch.nn.Sigmoid()
        elif n_classes > 1:
            # loss = 'categorical_crossentropy'
            loss = torch.nn.CrossEntropyLoss()
            final_act = torch.nn.LogSoftmax(1)  # across channels

        model = FCN(in_channels, n_classes, final_act=final_act)
        optimizer = Adam(model.parameters(), 1e-4)

        pred = model(torch.ones((4, in_channels, img_size, img_size)))
        print(pred)

    a()
