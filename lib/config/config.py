from .yacs import CfgNode as CN
import argparse
import os
import numpy as np
from . import yacs

cfg = CN()

# module
cfg.dataset_module = 'lib.datasets'
cfg.generate_module = 'lib.generate'

# experiment name
cfg.exp_name = 'gitbranch_hello'
cfg.exp_name_tag = ''

# task
cfg.task = 'hello'

# gpus
cfg.gpus = list(range(4))

# result
cfg.result_dir = 'E:/SciKnowEval-main/results'


def parse_cfg(cfg, args):
    if len(cfg.task) == 0:
        raise ValueError('task must be specified')

    # assign the gpus
    if -1 not in cfg.gpus:
        os.environ['CUDA_VISIBLE_DEVICES'] = ', '.join([str(gpu) for gpu in cfg.gpus])

    if len(cfg.exp_name_tag) != 0:
        cfg.exp_name +=  ('_' + cfg.exp_name_tag)
    cfg.exp_name = cfg.exp_name.replace('gitbranch', os.popen('git describe --all').readline().strip()[6:])
    cfg.exp_name = cfg.exp_name.replace('gitcommit', os.popen('git describe --tags --always').readline().strip())
    print('EXP NAME: ', cfg.exp_name)
    cfg.result_dir = os.path.join(cfg.result_dir, cfg.task, cfg.exp_name)
    modules = [key for key in cfg if '_module' in key]
    for module in modules:
        cfg[module.replace('_module', '_path')] = cfg[module].replace('.', '/') + '.py'

def make_cfg(args):
    def merge_cfg(cfg_file, cfg):
        with open(cfg_file, 'r') as f:
            current_cfg = yacs.load_cfg(f)
        if 'parent_cfg' in current_cfg.keys():
            cfg = merge_cfg(current_cfg.parent_cfg, cfg)
            cfg.merge_from_other_cfg(current_cfg)
        else:
            cfg.merge_from_other_cfg(current_cfg)
        print(cfg_file)
        return cfg
    cfg_ = merge_cfg(args.cfg_file, cfg)
    parse_cfg(cfg_, args)
    return cfg_


parser = argparse.ArgumentParser()
parser.add_argument("--cfg_file", default="configs/default.yaml", type=str)
args = parser.parse_args()
cfg = make_cfg(args)
