from sequence.app.random_request import RandomRequestApp
from sequence.kernel.timeline import Timeline
from sequence.network_management.reservation import Reservation
from sequence.topology.node import QuantumRouter


class FakeNode(QuantumRouter):
    def __init__(self, name, tl):
        super().__init__(name, tl)
        self.reserve_log = []

    def reserve_net_resource(self, responder: str, start_time: int, end_time: int, memory_size: int,
                             target_fidelity: float) -> None:
        self.reserve_log.append(responder)


def test_RandomRequestApp_update_last_rsvp_metrics():
    tl = Timeline()
    node = QuantumRouter("n1", tl)
    app = RandomRequestApp(node, [], 0)
    app._update_last_rsvp_metrics()
    assert len(app.get_throughput()) == 0
    app.cur_reserve = ["n2", 1e13, 2e13, 5, 0.9]
    app.reserves.append(app.cur_reserve)
    app.memory_counter = 10
    tl.time = 20
    assert app.request_time == 0
    app._update_last_rsvp_metrics()
    assert len(app.get_throughput()) == 1 and app.get_throughput()[0] == 1
    assert app.cur_reserve == []
    assert app.request_time == 20
    assert app.memory_counter == 0


def test_RandomRequestApp_start():
    tl = Timeline()
    node = FakeNode("n1", tl)
    app = RandomRequestApp(node, ["n2", "n3"], 0)
    for _ in range(1000):
        app.start()
        assert app.cur_reserve[0] == node.reserve_log[-1]

    counter = 0
    for responder in node.reserve_log:
        if responder == "n2":
            counter += 1
    assert abs(counter / (1000 - counter) - 1) < 0.1


def test_RandomRequestApp_get_reserve_res():
    tl = Timeline()
    tl.time = 6
    node = FakeNode("n1", tl)
    app = RandomRequestApp(node, ["n2", "n3"], 0)
    app.cur_reserve = ["n3", 10, 20, 5, 0.9]
    reservation = Reservation("n1", "n3", 10, 20, 5, 0.9)
    for i, card in enumerate(node.network_manager.protocol_stack[1].timecards):
        if i < 20:
            card.add(reservation)

    app.request_time = 5
    app.get_reserve_res(reservation, True)
    assert app.get_wait_time()[0] == 5
    assert len(tl.events) == 41 and tl.events.data[0].time == 10

    tl = Timeline()
    tl.time = 6
    node = FakeNode("n1", tl)
    app = RandomRequestApp(node, ["n2", "n3"], 0)
    app.cur_reserve = ["n3", 10, 20, 5, 0.9]
    reservation = Reservation("n1", "n3", 10, 20, 5, 0.9)
    app.request_time = 5
    app.get_reserve_res(reservation, False)
    tl.run()
    assert len(app.get_wait_time()) == 0
    assert app.cur_reserve[0] == "n3"
    assert app.cur_reserve[1] != 10
    assert app.cur_reserve[2] != 20
    assert app.cur_reserve[3] != 5
    assert app.cur_reserve[4] == 0.9
    assert len(node.reserve_log) == 1


def test_RandomRequestApp_get_memory():
    tl = Timeline(1)
    node = FakeNode("n1", tl)
    app = RandomRequestApp(node, ["n2", "n3"], 0)
    app.cur_reserve = ["n2", 0, 100, 2, 0.85]
    reservation = Reservation("n1", "n2", 0, 100, 2, 0.85)
    counter = 0
    for card in node.network_manager.protocol_stack[1].timecards:
        card.add(reservation)
        counter += 1
        if counter > 2:
            break
    app.get_other_reservation(reservation)

    tl.run()

    node.memory_array[0].entangled_memory["node_id"] = "n2"
    node.memory_array[0].entangled_memory["memo_id"] = "1"
    node.memory_array[0].fidelity = 0.9
    node.resource_manager.update(None, node.memory_array[0], "ENTANGLED")
    app.get_memory(node.resource_manager.memory_manager[0])
    assert node.resource_manager.memory_manager[0].state == "RAW"
    assert node.memory_array[0].entangled_memory["node_id"] == None
    assert node.memory_array[0].fidelity == 0

    node.memory_array[1].entangled_memory["node_id"] = "n3"
    node.memory_array[1].entangled_memory["memo_id"] = "1"
    node.memory_array[1].fidelity = 0.9
    node.resource_manager.update(None, node.memory_array[1], "ENTANGLED")
    app.get_memory(node.resource_manager.memory_manager[1])
    assert node.resource_manager.memory_manager[1].state == "ENTANGLED"

    node.memory_array[2].entangled_memory["node_id"] = "n2"
    node.memory_array[2].entangled_memory["memo_id"] = "1"
    node.memory_array[2].fidelity = 0.84
    node.resource_manager.update(None, node.memory_array[2], "ENTANGLED")
    app.get_memory(node.resource_manager.memory_manager[2])
    assert node.resource_manager.memory_manager[2].state == "ENTANGLED"

    node.memory_array[3].entangled_memory["node_id"] = "n2"
    node.memory_array[3].entangled_memory["memo_id"] = "1"
    node.memory_array[3].fidelity = 0.9
    node.resource_manager.update(None, node.memory_array[3], "ENTANGLED")
    app.get_memory(node.resource_manager.memory_manager[3])
    assert node.resource_manager.memory_manager[3].state == "ENTANGLED"


def test_RandomRequestApp_get_other_reservation():
    tl = Timeline()
    node = FakeNode("fake", tl)
    reservation = Reservation("initiator", "fake", 10, 100, 10, 0.9)
    counter = 0
    for card in node.network_manager.protocol_stack[1].timecards:
        if counter >= 10:
            break
        card.add(reservation)
        counter += 1

    app = RandomRequestApp(node, [], 0)
    app.get_other_reservation(reservation)
    assert len(app.memo_to_reserve) == 0
    tl.stop_time = 11
    tl.run()
    assert len(app.memo_to_reserve) == 10

    info = node.resource_manager.memory_manager[0]
    info.memory.entangled_memory = {"node_id": "initiator", "memo_id": "memo"}
    info.memory.fidelity = 1
    info.to_entangled()
    app.get_memory(info)
    assert info.state == "RAW" and info.memory.entangled_memory["node_id"] is None

    info = node.resource_manager.memory_manager[10]
    info.memory.entangled_memory = {"node_id": "initiator", "memo_id": "memo"}
    info.memory.fidelity = 1
    info.to_entangled()
    app.get_memory(info)
    assert info.state == "ENTANGLED"

    info = node.resource_manager.memory_manager[0]
    info.memory.entangled_memory = {"node_id": "initiator", "memo_id": "memo"}
    info.memory.fidelity = 0.8
    info.to_entangled()
    app.get_memory(info)
    assert info.state == "ENTANGLED"

    info = node.resource_manager.memory_manager[1]
    info.memory.entangled_memory = {"node_id": "x", "memo_id": "memo"}
    info.memory.fidelity = 1
    info.to_entangled()
    app.get_memory(info)
    assert info.state == "ENTANGLED"

    tl.stop_time = 101
    tl.run()

    print(app.memo_to_reserve)
    assert len(app.memo_to_reserve) == 0
    info = node.resource_manager.memory_manager[0]
    info.memory.entangled_memory = {"node_id": "initiator", "memo_id": "memo"}
    info.memory.fidelity = 1
    info.to_entangled()
    app.get_memory(info)
    assert info.state == "ENTANGLED"
