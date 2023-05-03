from config import *

from containers.checkpoint import Checkpoint

def build_checkpoint(epoch: Epoch, root: Root) -> Checkpoint:
    
    return Checkpoint(epoch=epoch, root=root)