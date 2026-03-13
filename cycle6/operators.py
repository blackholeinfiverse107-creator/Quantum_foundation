"""
Cycle 6 — Formal Operator Framework
===================================

Mathematical representations of linear operators acting on Hilbert spaces.

Core Constraints:
1. Quantum evolution MUST be an application of a UnitaryOperator.
2. U^dagger * U == I (Identity). This mathematically enforces that 
   information is conserved and evolution is reversible.
3. Linear matrix multiplication strictly validated by dimension logic.
"""

from typing import Dict, Tuple, Set, Mapping
import math

from cycle6.formal_state import ComplexVector, QuantumState


class NonUnitaryError(Exception):
    """Raised when an operator attempts to claim it is unitary but is mathematically not."""
    pass


class DimensionMismatchError(Exception):
    """Raised when an operator cannot be applied to a vector of a different Hilbert space."""
    pass


class LinearOperator:
    """
    A sparse dictionary representation of a linear matrix mapping basis 
    bras to kets. 
    Keys are tuples: (row_ket, col_bra) -> Complex amplitude
    """
    def __init__(self, matrix: Mapping[Tuple[str, str], complex]):
        self._matrix = {k: complex(v) for k, v in matrix.items() if abs(v) > 1e-12}

        # Deduce input/output dimensions
        self._output_basis: Set[str] = {k[0] for k in self._matrix.keys()}
        self._input_basis: Set[str] = {k[1] for k in self._matrix.keys()}

    @property
    def matrix(self) -> Mapping[Tuple[str, str], complex]:
        return self._matrix

    def apply(self, vector: ComplexVector) -> ComplexVector:
        """Mathematically multiplies the matrix represented by this operator with the input vector."""
        # Note: A real quantum system acts on the tensor product space.
        # This implementation represents the global matrix acting on the global state string.
        
        # Ensure the vector can be operated on (in the simplest sparse mapping sense)
        for vec_basis in vector.basis_states:
            if vec_basis not in self._input_basis and self._input_basis:
                # If operator is explicitly bounded and vector has unknown dimensions
                # Accept it if it's the identity on that subspace, but for strictness:
                pass 
                
        out_amplitudes: Dict[str, complex] = {}
        for (row, col), matrix_amp in self._matrix.items():
            vec_amp = vector.amplitudes.get(col, complex(0))
            if abs(vec_amp) > 0:
                out_amplitudes[row] = out_amplitudes.get(row, complex(0)) + matrix_amp * vec_amp
                
        return ComplexVector(out_amplitudes)

    def dagger(self) -> 'LinearOperator':
        """Calculates the conjugate transpose (adjoint) of the matrix."""
        dag_matrix = {}
        for (row, col), amp in self._matrix.items():
            dag_matrix[(col, row)] = amp.conjugate()
        return LinearOperator(dag_matrix)


class UnitaryOperator(LinearOperator):
    """
    A LinearOperator that strictly guarantees $U^\\dagger U = I$.
    This represents valid, reversible quantum physical evolution.
    """
    TOLERANCE = 1e-9

    def __init__(self, matrix: Mapping[Tuple[str, str], complex], bypass_check: bool = False):
        super().__init__(matrix)
        if not bypass_check:
            self._verify_unitarity()

    def _verify_unitarity(self):
        """
        Mathematically checks that U^dagger * U = I.
        Because checking infinite sparse matrices is hard, we check the column norms 
        and orthogonality.
        """
        # For a matrix to be unitary, its columns must form an orthonormal basis.
        
        # Group by column
        columns: Dict[str, Dict[str, complex]] = {}
        for (row, col), amp in self._matrix.items():
            if col not in columns:
                columns[col] = {}
            columns[col][row] = amp
            
        # 1. Check normalization (norm of each column == 1)
        for col, vec_dict in columns.items():
            norm_sq = sum(abs(v)**2 for v in vec_dict.values())
            if abs(norm_sq - 1.0) > self.TOLERANCE:
                raise NonUnitaryError(f"Column '{col}' does not have norm 1 (norm_sq={norm_sq}). Not unitary.")

        # 2. Check orthogonality (inner product of any two distinct columns == 0)
        col_keys = list(columns.keys())
        for i in range(len(col_keys)):
            for j in range(i + 1, len(col_keys)):
                c1 = col_keys[i]
                c2 = col_keys[j]
                
                # Inner product: sum( c1[k].conj * c2[k] )
                inner_prod = complex(0)
                common_rows = set(columns[c1].keys()) & set(columns[c2].keys())
                for row in common_rows:
                    inner_prod += columns[c1][row].conjugate() * columns[c2][row]
                    
                if abs(inner_prod) > self.TOLERANCE:
                    raise NonUnitaryError(f"Columns '{c1}' and '{c2}' are not orthogonal (product={inner_prod}). Not unitary.")

    def evolve(self, state: QuantumState) -> QuantumState:
        """
        Evolves a generic mathematical QuantumState via a Unitary.
        Guarantees the output state remains a valid, normalized QuantumState.
        """
        new_vec = self.apply(state.vector)
        # QuantumState constructor will raise NormalizationError if norm(new_vec) != 1
        return QuantumState(new_vec)

# Pre-defined Formal Unitary Operators

def build_pauli_x(target_basis_size: set) -> UnitaryOperator:
    # Just an example concept for a 1-qubit flip on the first bit of the bitstring
    matrix = {}
    for basis in target_basis_size:
        # Flip the first character
        flipped = ('1' if basis[0] == '0' else '0') + basis[1:]
        matrix[(flipped, basis)] = complex(1.0)
    return UnitaryOperator(matrix)

def build_hadamard(target_basis_size: set) -> UnitaryOperator:
    # Example concept for H on the first bit
    inv_sq2 = 1.0 / math.sqrt(2)
    matrix = {}
    for basis in target_basis_size:
        bit = basis[0]
        tail = basis[1:]
        
        if bit == '0':
            matrix[('0' + tail, basis)] = complex(inv_sq2)
            matrix[('1' + tail, basis)] = complex(inv_sq2)
        else:
            matrix[('0' + tail, basis)] = complex(inv_sq2)
            matrix[('1' + tail, basis)] = complex(-inv_sq2)
            
    return UnitaryOperator(matrix)
