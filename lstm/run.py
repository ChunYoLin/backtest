import sys, os
sys.path.insert(0, os.path.abspath('..'))
from fetcher.fetch_data import get_stock_pd
from reader import _prepare_data, gen_one_epoch, denormalize
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt


FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string("run_type", "train", "running type(train, test)")

class RNNConfig():
    input_size=8
    output_size=1
    num_steps=5
    lstm_size=256
    num_layers=2
    keep_prob=1.0
    batch_size = 128
    learning_rate = 0.001
    init_epoch = 5
    max_epoch = 1000

def main():
    config = RNNConfig()

    stock_pd = get_stock_pd("3078", fetch_from=(2013, 1), scale="W", mode="static", chip=True)
    X_train, y_train, X_test, y_test = _prepare_data(stock_pd, config.num_steps)

    lstm_graph = tf.Graph()
    with lstm_graph.as_default():
        inputs = tf.placeholder(tf.float32, [None, config.num_steps, config.input_size])
        targets = tf.placeholder(tf.float32, [None, config.output_size])

        def _create_one_cell():
            lstm_cell = tf.contrib.rnn.LSTMCell(config.lstm_size, state_is_tuple=True)
            if config.keep_prob < 1.0:
                lstm_cell = tf.contrib.rnn.DropoutWrapper(lstm_cell, output_keep_prob=config.keep_prob)
            return lstm_cell

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
        if FLAGS.run_type == "test":
            with tf.Session() as sess:
                saver = tf.train.Saver()
                saver.restore(sess, './model/simple-lstm.ckpt')
                test_data_feed = {
                        inputs: X_test,
                        }
                pred = sess.run([prediction], test_data_feed)
                pred = pred[0].reshape(-1)
                denorm_pred = denormalize(stock_pd, pred)
                denorm_ytest = denormalize(stock_pd, y_test)
                plt.plot(denorm_pred,color='red', label='Prediction')
                plt.plot(denorm_ytest,color='blue', label='Answer')
                plt.legend(loc='best')
                plt.show()
        else:
            saver = tf.train.Saver()
            loss = tf.reduce_mean(tf.square(prediction - targets))
            optimizer = tf.train.AdamOptimizer(config.learning_rate)
            minimize = optimizer.minimize(loss)
            with tf.Session(graph=lstm_graph) as sess:
                tf.global_variables_initializer().run()
                #  saver.restore(sess, './model/simple-lstm.ckpt')
                for epoch_step in range(config.max_epoch):
                    mean_loss = 0.
                    # Check https://github.com/lilianweng/stock-rnn/blob/master/data_wrapper.py
                    # if you are curious to know what is StockDataSet and how generate_one_epoch() 
                    # is implemented.
                    for batch_X, batch_y in gen_one_epoch(X_train, y_train, config.num_steps, config.batch_size):
                        train_data_feed = {
                            inputs: batch_X, 
                            targets: batch_y
                            }
                        train_loss, _ = sess.run([loss, minimize], train_data_feed)
                        mean_loss += train_loss
                    if epoch_step % 10 == 0:
                        saver.save(sess, './model/simple-lstm.ckpt')
                    print("epoch: {}, loss: {}".format(epoch_step, mean_loss/len(batch_X)))

if __name__ == '__main__':
    main()
