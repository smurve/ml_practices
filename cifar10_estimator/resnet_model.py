import tensorflow as tf
import cifar10_model


def resnet_model_fn(is_training, feature, label, data_format, params):
    """Build computation tower (Resnet).

    Args:
      is_training: true if is training graph.
      feature: a Tensor.
      label: a Tensor.
      data_format: channels_last (NHWC) or channels_first (NCHW).
      params for the model to consider

    Returns:
      A tuple with the loss for the tower, the gradients and parameters, and
      predictions.

    """
    num_layers = params.num_layers
    batch_norm_decay = params.batch_norm_decay
    batch_norm_epsilon = params.batch_norm_epsilon
    weight_decay = params.weight_decay

    model = cifar10_model.ResNetCifar10(
        num_layers,
        batch_norm_decay=batch_norm_decay,
        batch_norm_epsilon=batch_norm_epsilon,
        is_training=is_training,
        data_format=data_format)
    logits = model.forward_pass(feature, input_data_format='channels_last')
    tower_pred = {
        'classes': tf.argmax(input=logits, axis=1),
        'probabilities': tf.nn.softmax(logits)
    }

    tower_loss = tf.losses.sparse_softmax_cross_entropy(
        logits=logits, labels=label)
    tower_loss = tf.reduce_mean(tower_loss)

    model_params = tf.trainable_variables()
    tower_loss += weight_decay * tf.add_n(
        [tf.nn.l2_loss(v) for v in model_params])

    tower_grad = tf.gradients(tower_loss, model_params)

    return tower_loss, zip(tower_grad, model_params), tower_pred
