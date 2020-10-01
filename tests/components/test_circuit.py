from sequence.components.circuit import Circuit
from numpy import array, array_equal
from pytest import raises


def test_h():
    circuit = Circuit(1)
    circuit.h(0)
    coefficient = 1 / (2 ** 0.5)
    expect = array([[coefficient, coefficient], [coefficient, -coefficient]])
    assert array_equal(expect, circuit.get_unitary_matrix())


def test_x():
    circuit = Circuit(1)
    circuit.x(0)
    expect = array([[0, 1], [1, 0]])
    assert array_equal(expect, circuit.get_unitary_matrix())


def test_y():
    circuit = Circuit(1)
    circuit.y(0)
    expect = array([[0, complex(0, -1)], [complex(0, 1), 0]])
    assert array_equal(expect, circuit.get_unitary_matrix())


def test_z():
    circuit = Circuit(1)
    circuit.z(0)
    expect = array([[1, 0], [0, -1]])
    assert array_equal(expect, circuit.get_unitary_matrix())


def test_cx():
    circuit = Circuit(2)
    circuit.cx(0, 1)
    expect = array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    assert array_equal(expect, circuit.get_unitary_matrix())


def test_ccx():
    circuit = Circuit(3)
    circuit.ccx(0, 1, 2)
    expect = array([[1, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 0, 0, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0],
                    [0, 0, 0, 0, 1, 0, 0, 0],
                    [0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 0, 1, 0]])
    assert array_equal(expect, circuit.get_unitary_matrix())


def test_swap():
    circuit = Circuit(2)
    circuit.swap(0, 1)
    expect = array([[1, 0, 0, 0],
                    [0, 0, 1, 0],
                    [0, 1, 0, 0],
                    [0, 0, 0, 1]])
    assert array_equal(expect, circuit.get_unitary_matrix())


def test_t():
    from numpy import e, pi
    circuit = Circuit(1)
    circuit.t(0)
    expect = array([[1, 0], [0, e ** (complex(0, 1) * pi / 4)]])
    assert array_equal(expect, circuit.get_unitary_matrix())


def test_s():
    circuit = Circuit(1)
    circuit.s(0)
    expect = array([[1, 0], [0, complex(0, 1)]])
    assert array_equal(expect, circuit.get_unitary_matrix())


def test_measure():
    qc = Circuit(1)
    assert len(qc.measured_qubits) == 0
    qc.measure(0)
    assert len(qc.measured_qubits) == 1 and 0 in qc.measured_qubits
    with raises(AssertionError):
        qc.h(0)

    qc = Circuit(1)
    qc.h(0)
    qc.get_unitary_matrix()
    assert not qc._cache is None
    qc.x(0)
    assert qc._cache is None
    qc.get_unitary_matrix()
    qc.measure(0)
    assert not qc._cache is None


def test_Circuit():
    qc = Circuit(4)
    assert qc.size == 4 and len(qc.gates) == 0 and len(qc.measured_qubits) == 0
    with raises(AssertionError):
        qc.h(4)
    qc.cx(0, 3)
    qc.cx(1, 2)
    qc.measure(2)
    qc.measure(3)

    expect = array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, ],
                    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
                    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, ],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, ],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, ],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, ],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, ]])
    assert array_equal(expect, qc.get_unitary_matrix())
