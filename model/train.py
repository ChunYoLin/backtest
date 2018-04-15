import sys, os
sys.path.insert(0, os.path.abspath('..'))

from fetcher.fetch_data import get_stock_pd
from reader import _prepare_data, gen_one_epoch

    
time_frame = 5
S = get_stock_pd("3078", fetch_from=(2017, 1), scale="D", mode="dynamic")
X_train, y_train, X_test, y_test = _prepare_data(S, time_frame)
gen_one_epoch(X_train, y_train, time_frame, 16)

import tensorflow as tf
lstm_graph = tf.Graph()
with lstm_graph.as_default():
    pass

