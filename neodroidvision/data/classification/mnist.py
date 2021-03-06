#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 25/03/2020
           """

from pathlib import Path
from typing import Sequence, Tuple

import numpy
import torch
from matplotlib import pyplot
from torch.utils.data import Subset
from torch.utils.data.sampler import SubsetRandomSampler
from torchvision import datasets, transforms

from torchvision.datasets import MNIST

from draugr.torch_utilities import Split, SplitByPercentage, SupervisedDataset

__all__ = ["MNISTDataset", "MNISTDataset2"]




class MNISTDataset2(SupervisedDataset):
  """

"""

  @property
  def response_shape(self) -> Tuple[int, ...]:
    """

:return:
:rtype:
"""
    return (len(self.categories),)

  @property
  def predictor_shape(self) -> Tuple[int, ...]:
    """

:return:
:rtype:
"""
    return self._resize_shape

  def __init__(
      self,
      dataset_path: Path,
      split: Split = Split.Training,
      validation: float = 0.3,
      resize_s: int = 28,
      seed: int = 42,
      download=True,
      ):
    """
:param dataset_path: dataset directory
:param split: train, valid, test
"""
    super().__init__()

    if not download:
      assert dataset_path.exists(), f"root: {dataset_path} not found."

    self._resize_shape = (1, resize_s, resize_s)

    train_trans = transforms.Compose(
        [
            transforms.RandomResizedCrop(resize_s),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            ]
        )
    val_trans = transforms.Compose(
        [
            transforms.Resize(resize_s),
            # transforms.CenterCrop(resize_s),
            transforms.ToTensor(),
            ]
        )

    if split == Split.Training:
      mnist_data = MNIST(
          str(dataset_path), train=True, download=download, transform=train_trans
          )
    elif split == Split.Validation:
      mnist_data = MNIST(
          str(dataset_path), train=True, download=download, transform=val_trans
          )
    else:
      mnist_data = MNIST(
          str(dataset_path), train=False, download=download, transform=val_trans
          )

    if split != Split.Testing:
      torch.manual_seed(seed)
      train_ind, val_ind, test_ind = SplitByPercentage(
          len(mnist_data), validation=validation, testing=0.0
          ).shuffled_indices()
      if split == Split.Validation:
        self.mnist_data_split = Subset(mnist_data, val_ind)
      else:
        self.mnist_data_split = Subset(mnist_data, train_ind)
    else:
      self.mnist_data_split = mnist_data

    self.categories = mnist_data.classes

  def __len__(self):
    return len(self.mnist_data_split)

  def __getitem__(self, index):
    return self.mnist_data_split.__getitem__(index)


class MNISTDataset(SupervisedDataset):
  """

"""

  trans = transforms.Compose(
      [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
      )

  def __init__(self, data_dir: Path, split: Split = Split.Training):
    super().__init__()
    if split == Split.Training:
      self._dataset = datasets.MNIST(
          str(data_dir), train=True, download=True, transform=self.trans
          )
    else:
      self._dataset = datasets.MNIST(
          str(data_dir), train=False, download=True, transform=self.trans
          )

  def __getitem__(self, index):
    return self._dataset.__getitem__(index)

  def __len__(self):
    return self._dataset.__len__()

  @property
  def predictor_shape(self) -> Tuple[int, ...]:
    """

:return:
:rtype:
"""
    return 1, 28, 28

  @property
  def response_shape(self) -> Tuple[int, ...]:
    """

:return:
:rtype:
"""
    return (10,)

  @staticmethod
  def get_train_valid_loader(
      data_dir: Path,
      batch_size: int,
      random_seed: int,
      *,
      valid_size: float = 0.1,
      shuffle: bool = True,
      num_workers: int = 4,
      pin_memory: bool = False,
      using_cuda: bool = True,
      ) -> Tuple[torch.utils.data.DataLoader, torch.utils.data.DataLoader]:
    """Train and validation data loaders.

If using CUDA, num_workers should be set to 1 and pin_memory to True.

Args:
data_dir: path directory to the dataset.
batch_size: how many samples per batch to load.
random_seed: fix seed for reproducibility.
valid_size: percentage split of the training set used for
    the validation set. Should be a float in the range [0, 1].
    In the paper, this number is set to 0.1.
shuffle: whether to shuffle the train/validation indices.
show_sample: plot 9x9 sample grid of the dataset.
num_workers: number of subprocesses to use when loading the dataset.
pin_memory: whether to copy tensors into CUDA pinned memory. Set it to
    True if using GPU.
    :param data_dir:
    :type data_dir:
    :param batch_size:
    :type batch_size:
    :param random_seed:
    :type random_seed:
    :param valid_size:
    :type valid_size:
    :param shuffle:
    :type shuffle:
    :param num_workers:
    :type num_workers:
    :param pin_memory:
    :type pin_memory:
    :param using_cuda:
    :type using_cuda:
"""
    error_msg = "[!] valid_size should be in the range [0, 1]."
    assert (valid_size >= 0) and (valid_size <= 1), error_msg

    if using_cuda:
      assert num_workers == 1
      assert pin_memory == True

    dataset = MNISTDataset(data_dir)
    num_train = len(dataset)
    indices = list(range(num_train))
    split = int(numpy.floor(valid_size * num_train))

    if shuffle:
      numpy.random.seed(random_seed)
      numpy.random.shuffle(indices)

    train_idx, valid_idx = indices[split:], indices[:split]

    train_sampler = SubsetRandomSampler(train_idx)
    valid_sampler = SubsetRandomSampler(valid_idx)

    train_loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        sampler=train_sampler,
        num_workers=num_workers,
        pin_memory=pin_memory,
        )

    valid_loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        sampler=valid_sampler,
        num_workers=num_workers,
        pin_memory=pin_memory,
        )

    return train_loader, valid_loader

  @staticmethod
  def get_test_loader(
      data_dir: Path,
      batch_size: int,
      *,
      num_workers: int = 4,
      pin_memory: bool = False,
      using_cuda: bool = True,
      ) -> torch.utils.data.DataLoader:
    """Test datalaoder.

If using CUDA, num_workers should be set to 1 and pin_memory to True.

Args:
data_dir: path directory to the dataset.
batch_size: how many samples per batch to load.
num_workers: number of subprocesses to use when loading the dataset.
pin_memory: whether to copy tensors into CUDA pinned memory. Set it to
    True if using GPU.
:param data_dir:
:type data_dir:
:param batch_size:
:type batch_size:
:param num_workers:
:type num_workers:
:param pin_memory:
:type pin_memory:
:param using_cuda:
:type using_cuda:
"""
    # define transforms

    if using_cuda:
      assert num_workers == 1
      assert pin_memory == True

    dataset = MNISTDataset(data_dir, split=Split.Testing)

    data_loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        )

    return data_loader

  def sample(self) -> None:
    """

"""
    images, labels = next(
        iter(
            torch.utils.data.DataLoader(
                self, batch_size=9, shuffle=True, num_workers=1, pin_memory=False
                )
            )
        )
    X = images.numpy()
    X = numpy.transpose(X, [0, 2, 3, 1])
    MNISTDataset.plot_images(X, labels)

  @staticmethod
  def plot_images(images: numpy.ndarray, label: Sequence) -> None:
    """

:param images:
:type images:
:param label:
:type label:
"""
    images = images.squeeze()
    assert len(images) == len(label) == 9

    fig, axes = pyplot.subplots(3, 3)
    for i, ax in enumerate(axes.flat):
      ax.imshow(images[i], cmap="Greys_r")
      xlabel = f"{label[i]}"
      ax.set_xlabel(xlabel)
      ax.set_xticks([])
      ax.set_yticks([])

    pyplot.show()


if __name__ == "__main__":
  def a():
    MNISTDataset(Path.home() / "Data" / "MNIST").sample()
    pyplot.show()


  def siuadyh():
    import tqdm

    batch_size = 32

    dt_t = MNISTDataset2(Path(Path.home() / "Data" / "mnist"), split=Split.Training)

    print(len(dt_t))

    dt_v = MNISTDataset2(
        Path(Path.home() / "Data" / "mnist"), split=Split.Validation
        )

    print(len(dt_v))

    dt = MNISTDataset2(Path(Path.home() / "Data" / "mnist"), split=Split.Testing)

    print(len(dt))

    data_loader = torch.utils.data.DataLoader(
        dt, batch_size=batch_size, shuffle=False
        )

    for batch_idx, (imgs, label) in tqdm.tqdm(
        enumerate(data_loader),
        total=len(data_loader),
        desc="Bro",
        ncols=80,
        leave=False,
        ):
      # pyplot.imshow(dt.inverse_transform(imgs[0]))
      # pyplot.imshow(imgs)
      # pyplot.show()
      print(imgs.shape)
      break


  siuadyh()
