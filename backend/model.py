import tensorflow as tf
from tensorflow.keras import layers, Model, regularizers
from tensorflow.keras.utils import register_keras_serializable

@register_keras_serializable()
class AttentionSum(layers.Layer):
    def call(self, inputs):
        return tf.reduce_sum(inputs, axis=1)

def attention_block(x):
    score = layers.Dense(1, activation="tanh")(x)
    weights = layers.Softmax(axis=1)(score)
    context = layers.Multiply()([x, weights])
    return AttentionSum()(context)

def build_model(input_shape):
    inp = layers.Input(shape=input_shape)
    
    # Simple, proven architecture
    x = layers.Conv1D(64, 3, activation='relu', padding='same')(inp)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling1D(2)(x)
    x = layers.Dropout(0.3)(x)

    x = layers.Conv1D(128, 3, activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling1D(2)(x)
    x = layers.Dropout(0.3)(x)

    x = layers.LSTM(64, return_sequences=True)(x)
    x = attention_block(x)

    x = layers.Dense(64, activation='relu')(x)
    x = layers.Dropout(0.4)(x)
    
    out = layers.Dense(1, activation='sigmoid')(x)
    return Model(inp, out)
