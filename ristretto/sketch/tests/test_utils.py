import numpy as np
from numpy.testing import assert_raises

from ristretto.sketch.utils import orthonormalize
from ristretto.sketch.utils import perform_subspace_iterations


def test_orthonormalize():
    # ------------------------------------------------------------------------
    # test overwrite
    A = np.eye(10)

    B = orthonormalize(A, overwrite_a=False)
    over = orthonormalize(A, overwrite_a=True)
    
    assert A is not B
    assert A is over

    # ------------------------------------------------------------------------
    # test return array type
    assert A.dtype == B.dtype

    # ------------------------------------------------------------------------
    # test check_finite
    A[0,0] = np.inf
    assert_raises(ValueError, orthonormalize, A, check_finite=True)


def test_perform_subspace_iterations():
    # ------------------------------------------------------------------------
    # test shapes
    A = np.eye(10)
    Q_row = np.eye(10)[:5]
    Q_col = np.eye(10)[:,:5]

    rowwise = perform_subspace_iterations(A, Q_row)
    colwise = perform_subspace_iterations(A, Q_col)

    assert rowwise.shape == Q_row.shape
    assert colwise.shape == Q_col.shape
