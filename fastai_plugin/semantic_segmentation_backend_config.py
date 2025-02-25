from copy import deepcopy

import rastervision as rv

from fastai_plugin.semantic_segmentation_backend import (
    SemanticSegmentationBackend)
from fastai_plugin.simple_backend_config import (
    SimpleBackendConfig, SimpleBackendConfigBuilder)

FASTAI_SEMANTIC_SEGMENTATION = 'FASTAI_SEMANTIC_SEGMENTATION'


class TrainOptions():
    def __init__(self, batch_sz=None, weight_decay=None, lr=None,
                 one_cycle=None,
                 num_epochs=None, model_arch=None, fp16=None,
                 flip_vert=None, sync_interval=None, debug=None,
                 train_prop=None, train_count=None, tta=None, oversample=None):
        self.batch_sz = batch_sz
        self.weight_decay = weight_decay
        self.lr = lr
        self.one_cycle = one_cycle
        self.num_epochs = num_epochs
        self.model_arch = model_arch
        self.fp16 = fp16
        self.flip_vert = flip_vert
        self.sync_interval = sync_interval
        self.debug = debug
        self.train_prop = train_prop
        self.train_count = train_count
        self.tta = tta
        self.oversample = oversample

    def __setattr__(self, name, value):
        if name in ['batch_sz', 'num_epochs', 'sync_interval']:
            value = int(value) if isinstance(value, float) else value
        super().__setattr__(name, value)


class SemanticSegmentationBackendConfig(SimpleBackendConfig):
    train_opts_class = TrainOptions
    backend_type = FASTAI_SEMANTIC_SEGMENTATION
    backend_class = SemanticSegmentationBackend


class SemanticSegmentationBackendConfigBuilder(SimpleBackendConfigBuilder):
    config_class = SemanticSegmentationBackendConfig

    def _applicable_tasks(self):
        return [rv.SEMANTIC_SEGMENTATION]

    def with_train_options(
            self,
            batch_sz=8,
            weight_decay=1e-2,
            lr=1e-4,
            one_cycle=False,
            num_epochs=5,
            model_arch='resnet18',
            fp16=False,
            flip_vert=False,
            sync_interval=1,
            debug=False,
            train_prop=1.0,
            train_count=None,
            tta=False,
            oversample=None):
        """Set options for training models.

        Args:
            batch_sz: (int) the batch size
            weight_decay: (float) the weight decay
            lr: (float or None) the learning rate if using a fixed LR (ie. one_cycle is False),
                or the maximum LR to use if one_cycle is True,
                or None if automatic learning rate finder (fastai lr_find)
                should be used
            one_cycle: (bool) True if fastai fit_one_cycle should be used. This
                cycles the LR once during the course of training and seems to
                result in a pretty consistent improvement. See lr for more
                details.
            num_epochs: (int) number of epochs (sweeps through training set) to
                train model for
            model_arch: (str) classification model backbone to use for UNet
                architecture. Any option in torchvision.models is valid, for
                example, resnet18.
            fp16: (bool) use mixed-precision training. Ideally, this will make
                things run 2x fast.
            flip_vert: (bool) use vertical flips and rotations for data aug
            sync_interval: (int) sync training directory to cloud every
                sync_interval epochs.
            debug: (bool) if True, save debug chips (ie. visualizations of
                input to model during training) during training and use
                single-core for creating minibatches.
            train_prop: (float) number between 0 and 1 that controls what
                proportion of the training set is used for training
            train_count: (int) number of training examples to use during
                training
            tta: (bool) if True, use test-time augmentation. This will make
                a prediction for 8 flips/rotations of the image and then
                average them together. Should result in small improvement in
                accuracy, but 8x slowdown.
            oversample: (dict or None) of form
                {'rare_class_ids': <list of class ids>, 'rare_target_prop': <float>}
                This will make it so chips containing any labels in rare_class_ids
                will be sampled with a probability of rare_target_prop. This is
                to help cope with severely imbalanced datasets.
        """
        b = deepcopy(self)
        b.train_opts = TrainOptions(
            batch_sz=batch_sz, weight_decay=weight_decay, lr=lr,
            one_cycle=one_cycle,
            num_epochs=num_epochs, model_arch=model_arch, fp16=fp16,
            flip_vert=flip_vert, sync_interval=sync_interval, debug=debug,
            train_prop=train_prop, train_count=train_count, tta=tta,
            oversample=oversample)
        return b

    def with_pretrained_uri(self, pretrained_uri):
        """pretrained_uri should be uri of exported model file."""
        return super().with_pretrained_uri(pretrained_uri)


def register_plugin(plugin_registry):
    plugin_registry.register_config_builder(
        rv.BACKEND, FASTAI_SEMANTIC_SEGMENTATION,
        SemanticSegmentationBackendConfigBuilder)