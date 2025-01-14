from base.base_trainer import BaseTrainer
import numpy as np
import os 


class MNISTTrainer(BaseTrainer):
    def __init__(self, sess, model, data, config,logger, summary):
        super(MNISTTrainer, self).__init__(sess, model, data, config, logger, summary)

    def train_epoch(self, current_epoch):
        loop = range(self.config["num_iter_per_epoch"])
        losses = []
        accs = []
        for current_iter in loop:
            loss, acc = self.train_step(current_epoch, current_iter)
            losses.append(loss)
            accs.append(acc)
        loss = np.mean(losses)
        acc = np.mean(accs)

        cur_it = self.model.global_step_tensor.eval(self.sess)
        summaries_dict = {
            'loss': loss,
            'acc': acc,
        }
        self.summary.summarize(cur_it, summaries_dict=summaries_dict)
        self.model.save_checkpoint(self.sess)

        if current_epoch % self.config["save_protobuf_epoch_interval"]:
            self.model.save_to_protobuf(self.sess, self.model.output_node_name, \
            os.path.join(self.config["model_dir"], "model_epoch_{}.pb".format(current_epoch)))

    def train_step(self, current_epoch, current_iter):
        batch_x, batch_y = next(self.data.next_batch(self.config["batch_size"]))
        feed_dict = {self.model.x: batch_x, self.model.y: batch_y, self.model.is_training: True}
        _, loss, acc = self.sess.run([self.model.train_step, self.model.loss, self.model.acc],
                                     feed_dict=feed_dict)
        
        log_text = "epoch: {}, step: {}, loss: {:.6f}, acc: {:.3f}".\
            format(current_epoch, current_iter, loss, acc)
        self.logger.logging("train", log_text)

        return loss, acc
