import sys, os
sys.path.insert(0, os.path.abspath('../../'))
from fetcher.fetch_data import get_stock_pd
from reader import _prepare_data, gen_one_epoch, denormalize
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

class RNNConfig():
    input_size=8
    output_size=1
    output_length=5
    num_steps=20
    lstm_size=256
    num_layers=2
    keep_prob=1.0
    batch_size = 128
    learning_rate = 0.001
    init_epoch = 5
    max_epoch = 1000

config = RNNConfig()

def single_cell():
    return tf.contrib.rnn.LSTMCell(config.lstm_size, forget_bias=0., state_is_tuple=True)
with tf.variable_scope("model") as scope:
    #  build encoder #
    encoder_inputs = []
    for i in range(config.num_steps): 
        encoder_inputs.append(tf.placeholder(shape=[config.batch_size, config.input_size], dtype=tf.float32, name='encoder_inputs{0}'.format(i)))
    cell = single_cell()
    if config.num_layers > 1:
        cell = tf.contrib.rnn.MultiRNNCell([single_cell() for _ in range(config.num_layers)])
    encoder_out = tf.contrib.rnn.static_rnn(
        cell=cell, 
        inputs=encoder_inputs, 
        initial_state=cell.zero_state(config.batch_size, dtype=tf.float32),
    )
    encoder_final_outputs = encoder_out[0]
    encoder_final_state = encoder_out[1]


with tf.variable_scope("decoder", reuse=False):
    #  build decoder #
    decoder_inputs = []
    for i in range(config.output_length): 
        decoder_inputs.append(tf.placeholder(shape=[config.batch_size, config.output_size], dtype=tf.float32, name='decoder_inputs{0}'.format(i)))
    decoder_targets = tf.placeholder(shape=[config.output_length, config.batch_size, config.output_size], dtype=tf.float32, name='decoder_targets')
    #  tf.get_variable_scope().reuse_variables()
    cell = single_cell()
    if config.num_layers > 1:
        cell = tf.contrib.rnn.MultiRNNCell([single_cell() for _ in range(config.num_layers)])

    decoder_out = tf.contrib.rnn.static_rnn(
        cell=cell, 
        inputs=decoder_inputs, 
        initial_state=encoder_final_state,
    )
    decoder_final_outputs = decoder_out[0]
    decoder_final_state = decoder_out[1]
    decoder_final_outputs = tf.concat(axis=0, values=decoder_final_outputs)
    #  decoder output
    decoder_w = tf.get_variable('decoder_w', [config.lstm_size, config.output_size])
    decoder_b = tf.get_variable('decoder_b', [config.output_size])
    decoder_logits = (tf.matmul(decoder_final_outputs, decoder_w) + decoder_b)
    decoder_logits = tf.reshape(decoder_logits, [config.output_length, config.batch_size, config.output_size])
    #  get loss
    saver = tf.train.Saver()
    loss = tf.reduce_mean(tf.square(decoder_logits-decoder_targets))
    optimizer = tf.train.AdamOptimizer(config.learning_rate)
    minimize = optimizer.minimize(loss)
    #  get data
    stock_pd = get_stock_pd("3078", fetch_from=(2013, 1), scale="D", mode="dynamic", chip=True)
    X_train, y_train, X_test, y_test = _prepare_data(stock_pd, config.num_steps, config.output_length+1)
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        #  saver.restore(sess, './model/simple-lstm.ckpt')
        for epoch_step in range(config.max_epoch):
            mean_loss = 0.
            for batch_X, batch_y in gen_one_epoch(X_train, y_train, config.num_steps, config.batch_size):
                batch_y = batch_y.reshape([config.batch_size, config.output_length+1, 1])
                batch_X = np.transpose(batch_X, (1, 0, 2))
                batch_y = np.transpose(batch_y, (1, 0, 2))
                train_data_feed = {}
                for i in range(config.num_steps):
                    train_data_feed[encoder_inputs[i]] = batch_X[i]
                for i in range(config.output_length):
                    train_data_feed[decoder_inputs[i]] = batch_y[i]
                train_data_feed[decoder_targets] = batch_y[1:]
                train_loss, _ = sess.run([loss, minimize], train_data_feed)
                mean_loss += train_loss
            if epoch_step % 10 == 0:
                saver.save(sess, './model/simple-seq2seq.ckpt')
            print("epoch: {}, loss: {}".format(epoch_step, mean_loss/len(batch_X)))
