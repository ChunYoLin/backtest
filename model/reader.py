import sys, os
import time
import random

import numpy as np
import pandas as pd


random.seed(time.time())


def _prepare_data(stock_pd, time_frame):
    stock_pd = stock_pd[["open", "high", "close", "low", "capacity"]]
    number_features = len(stock_pd.columns)
    datavalue = stock_pd.as_matrix()
    result = []
    for idx in range(len(datavalue) - (time_frame+1)):
        result.append(datavalue[idx: idx + (time_frame+1)])

    result = np.array(result)
    number_train = round(0.9 * result.shape[0])

    x_train = result[:int(number_train), :-1]
    y_train = result[:int(number_train), -1][:,2]

    x_test = result[int(number_train):, :-1]
    y_test = result[int(number_train):, -1][:,2]
    
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], number_features))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], number_features))

    return [x_train, y_train, x_test, y_test]


def gen_one_epoch(X, y, num_steps, batch_size):
    num_batches = int(len(X))
    if batch_size * num_batches < len(X):
        num_batches += 1

    batch_indices = list(range(num_batches))
    random.shuffle(batch_indices)

    for j in batch_indices:
        batch_X = X[j: j + batch_size]
        batch_y = y[j: j + batch_size]
        assert set(map(len, batch_X)) == {num_steps}
        yield batch_X, batch_y.reshape(-1, 1)
