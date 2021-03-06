import math

from sequence.components.optical_channel import QuantumChannel, ClassicalChannel
from sequence.kernel.event import Event
from sequence.kernel.process import Process
from sequence.kernel.timeline import Timeline
from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.topology.node import QKDNode
import sequence.utils.log as log


# constants
log_filename = "bb84.log"
runtime = 2e10
distance = 1e3

tl = Timeline(runtime)
tl.seed(1)
tl.show_progress = True

# set log
log.set_logger(__name__, tl, log_filename)
log.set_logger_level("DEBUG")
log.track_module("BB84")
log.track_module('timeline')

qc = QuantumChannel("qc", tl, distance=distance, polarization_fidelity=0.97, attenuation=0.0002)
cc = ClassicalChannel("cc", tl, distance=distance)
cc.delay += 1e9  # 1 ms

# Alice
ls_params = {"frequency": 80e6, "mean_photon_num": 0.1}
alice = QKDNode("alice", tl, stack_size=1)

for name, param in ls_params.items():
    alice.update_lightsource_params(name, param)

# Bob
detector_params = [{"efficiency": 0.8, "dark_count": 10, "time_resolution": 10, "count_rate": 50e6},
                   {"efficiency": 0.8, "dark_count": 10, "time_resolution": 10, "count_rate": 50e6}]
bob = QKDNode("bob", tl, stack_size=1)

for i in range(len(detector_params)):
    for name, param in detector_params[i].items():
        bob.update_detector_params(i, name, param)

qc.set_ends(alice, bob)
cc.set_ends(alice, bob)

# BB84 config
pair_bb84_protocols(alice.protocol_stack[0], bob.protocol_stack[0])

process = Process(alice.protocol_stack[0], "push", [256, math.inf, 6e12])
event = Event(0, process)
tl.schedule(event)

tl.init()
tl.run()
