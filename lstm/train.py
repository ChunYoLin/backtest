import sys, os
sys.path.insert(0, os.path.abspath('..'))

from fetcher.fetch_data import get_stock_pd
from reader import _prepare_data, gen_one_epoch, denormalize
import tensorflow as tf
import numpy as np

class RNNConfig():
    input_size=5
    output_size=1
    num_steps=20
    lstm_size=128
    num_layers=1
    keep_prob=0.8
    batch_size = 32
    init_learning_rate = 0.001
    learning_rate_decay = 0.99
    init_epoch = 5
    max_epoch = 1000

config = RNNConfig()

S = get_stock_pd("3078", fetch_from=(2013, 1), scale="D", mode="dynamic")
X_train, y_train, X_test, y_test = _prepare_data(S, config.num_steps)

lstm_graph = tf.Graph()
with lstm_graph.as_default():
    inputs = tf.placeholder(tf.float32, [None, config.num_steps, config.input_size])
    targets = tf.placeholder(tf.float32, [None, config.output_size])
    learning_rate = tf.placeholder(tf.float32, None)

    def _create_one_cell():
        return tf.contrib.rnn.LSTMCell(config.lstm_size, state_is_tuple=True)
    cell = tf.contrib.rnn.MultiRNNCell(
        [_create_one_cell() for _ in range(config.num_layers)], 
        state_is_tuple=True
    ) if config.num_layers > 1 else _create_one_cell()

    val, _ = tf.nn.dynamic_rnn(cell, inputs, dtype=tf.float32)
    val = tf.transpose(val, [1, 0, 2])
    last = tf.gather(val, int(val.get_shape()[0]) - 1, name="last_lstm_output")
    weight = tf.Variable(tf.truncated_normal([config.lstm_size, config.output_size]))
    bias = tf.Variable(tf.constant(0.1, shape=[config.output_size]))
    prediction = tf.matmul(last, weight) + bias
    loss = tf.reduce_mean(tf.square(prediction - targets))
    optimizer = tf.train.RMSPropOptimizer(learning_rate)
    minimize = optimizer.minimize(loss)
    saver = tf.train.Saver()
    with tf.Session(graph=lstm_graph) as sess:
        tf.global_variables_initializer().run()
        learning_rates_to_use = [
            config.init_learning_rate * (
                config.learning_rate_decay ** max(float(i + 1 - config.init_epoch), 0.0)
            ) for i in range(config.max_epoch)]
        for epoch_step in range(config.max_epoch):
            current_lr = learning_rates_to_use[epoch_step]

            # Check https://github.com/lilianweng/stock-rnn/blob/master/data_wrapper.py
            # if you are curious to know what is StockDataSet and how generate_one_epoch() 
            # is implemented.
            for batch_X, batch_y in gen_one_epoch(X_train, y_train, config.num_steps, config.batch_size):
                train_data_feed = {
                    inputs: batch_X, 
                    targets: batch_y, 
                    learning_rate: current_lr
                    }
                train_loss, pred, _ = sess.run([loss, prediction, minimize], train_data_feed)
            if epoch_step % 10 == 0:
                saver.save(sess, './model/simple-lstm', global_step=epoch_step)
            print("epoch: {}".format(epoch_step))
        test_data_feed = {
                inputs: X_test,
                }
        pred = sess.run([prediction], test_data_feed)
        pred = pred[0].reshape(-1)
        print(denormalize(S, pred))
        print(denormalize(S, y_test))
