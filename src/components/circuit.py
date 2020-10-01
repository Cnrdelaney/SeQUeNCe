"""Models for simulation of quantum circuit

This module introduces the QuantumCircuit class.
"""
from typing import List, TYPE_CHECKING, Dict
from qutip.qip.circuit import QubitCircuit, Gate
from qutip.qip.operations import gate_sequence_product

if TYPE_CHECKING:
    import numpy


def validator(func):
    def wrapper(self, *args, **kwargs):
        for q in args:
            assert q < self.size, 'qubit index out of range'
            assert q not in self.measured_qubits, 'qubit has been measured'
        if func.__name__ != 'measure':
            self._cache = None
        return func(self, *args, **kwargs)

    return wrapper


class Circuit():
    """Class of quantum circuit

    Attributes:
        size (int): the number of quantum qubits of circuit
        gates (List[str]): a list of command bound to some registers
        circuit_matrix (List[List[complex]]): the unitary matrix of circuit
    """

    def __init__(self, size: int):
        self.size = size
        self.gates = []
        self.measured_qubits = set()
        self._cache = None

    def get_unitary_matrix(self) -> "numpy.ndarray":
        """Method to get unitary matrix of circuit without measurement

        Returns:
            numpy.ndarray: the matrix stored in the numpy.ndarray
        """
        if self._cache is None:
            qc = QubitCircuit(self.size)
            for gate in self.gates:
                name, indices = gate
                if name == 'h':
                    qc.add_gate('SNOT', indices[0])
                elif name == 'x':
                    qc.add_gate('X', indices[0])
                elif name == 'y':
                    qc.add_gate('Y', indices[0])
                elif name == 'z':
                    qc.add_gate('Z', indices[0])
                elif name == 'cx':
                    qc.add_gate('CNOT', controls=indices[0], targets=indices[1])
                elif name == 'ccx':
                    qc.add_gate('TOFFOLI', controls=indices[:2], targets=indices[2])
                elif name == 'swap':
                    qc.add_gate('SWAP', indices)
                elif name == 't':
                    qc.add_gate('T', indices[0])
                elif name == 's':
                    qc.add_gate('S', indices[0])
                else:
                    raise NotImplementedError
            self._cache = gate_sequence_product(qc.propagators()).full()
            return self._cache
        return self._cache

    @validator
    def h(self, qubit: int):
        """Method to apply single-qubit Hadamard gate on a qubit.

        Args:
            qubit (int): the index of qubit in the circuit

        """
        self.gates.append(['h', [qubit]])

    @validator
    def x(self, qubit: int):
        """Method to apply single-qubit Pauli-X gate on a qubit.

        Args:
            qubit (int): the index of qubit in the circuit

        """
        self.gates.append(['x', [qubit]])

    @validator
    def y(self, qubit: int):
        """Method to apply single-qubit Pauli-Y gate on a qubit.

        Args:
            qubit (int): the index of qubit in the circuit

        """
        self.gates.append(['y', [qubit]])

    @validator
    def z(self, qubit: int):
        """Method to apply single-qubit Pauli-Z gate on a qubit.

        Args:
            qubit (int): the index of qubit in the circuit

        """
        self.gates.append(['z', [qubit]])

    @validator
    def cx(self, control: int, target: int):
        """Method to apply Control-X gate on three qubits.

        Args:
            control1 (int): the index of control1 in the circuit
            target (int): the index of target in the circuit

        """
        self.gates.append(['cx', [control, target]])

    @validator
    def ccx(self, control1: int, control2: int, target: int):
        """Method to apply Toffoli gate on three qubits.

        Args:
            control1 (int): the index of control1 in the circuit
            control2 (int): the index of control2 in the circuit
            target (int): the index of target in the circuit

        """
        self.gates.append(['ccx', [control1, control2, target]])

    @validator
    def swap(self, qubit1: int, qubit2: int):
        """Method to apply SWAP gate on two qubits.

        Args:
            qubit1 (int): the index of qubit1 in the circuit
            qubit2 (int): the index of qubit2 in the circuit

        """
        self.gates.append(['swap', [qubit1, qubit2]])

    @validator
    def t(self, qubit: int):
        """Method to apply single T gate on a qubit.

        Args:
            qubit (int): the index of qubit in the circuit

        """
        self.gates.append(['t', [qubit]])

    @validator
    def s(self, qubit: int):
        """Method to apply single S gate on a qubit.

        Args:
            qubit (int): the index of qubit in the circuit

        """
        self.gates.append(['s', [qubit]])

    @validator
    def measure(self, qubit: int):
        """Method to measure quantum bit into classical bit.

        Args:
            qubit (int): the index of qubit in the circuit

        """
        self.measured_qubits.add(qubit)
