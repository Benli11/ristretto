
import numpy as np
import scipy as sci

from ristretto import *
from ristretto.nmf import *
from ristretto.mf import *
from ristretto.dmd import *
from ristretto.util import *

from ristretto.big.random_qr \
    import _random_sketch, _power_iterations, randomized_qr_sample


from unittest import main, makeSuite, TestCase, TestSuite
from numpy.testing \
    import (assert_raises, assert_equal, assert_allclose, assert_array_equal,
            assert_array_almost_equal)

atol_float32 = 1e-4
atol_float64 = 1e-8

#
#******************************************************************************
#
class test_mf(TestCase):
    def setUp(self):
        np.random.seed(123)

    def test_rqb_float64(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot( A.T )
        Q, B = rqb(A, k=k, p=5, q=2)
        Ak = Q.dot(B)
        percent_error = 100 * np.linalg.norm(A - Ak) / np.linalg.norm(A)

        assert percent_error < atol_float64


    def test_rqb_complex128(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64) + 1j * np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.conj().T)
        Q, B = rqb(A, k=k, p=5, q=2)
        Ak = Q.dot(B)
        percent_error = 100 * np.linalg.norm(A - Ak) / np.linalg.norm(A)

        assert percent_error < atol_float64

    def test_rsvd_float64(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot( A.T )
        U, s, Vt = rsvd(A, k=k, p=5, q=2)
        Ak = U.dot(np.diag(s).dot(Vt))
        percent_error = 100 * np.linalg.norm(A - Ak) / np.linalg.norm(A)

        assert percent_error < atol_float64


    def test_rsvd_complex128(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64) + 1j * np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.conj().T)
        U, s, Vh = rsvd(A, k=k, p=5, q=2)
        Ak = U.dot(np.diag(s).dot(Vh))
        percent_error = 100 * np.linalg.norm(A - Ak) / np.linalg.norm(A)

        assert percent_error < atol_float64


    def test_rsvd_fliped_float64(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.T)
        A = A[:,0:50]
        U, s, Vh = rsvd(A.T, k=k, p=5, q=2)
        Ak = U.dot(np.diag(s).dot(Vh))
        percent_error = 100 * np.linalg.norm(A.T - Ak) / np.linalg.norm(A.T)
        
        assert percent_error < atol_float64  
  
		    
    def test_rsvd_fliped_complex128(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64) + 1j * np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.conj().T)
        A = A[:,0:50]
        U, s, Vh = rsvd(A.conj().T, k=k, p=5, q=2)
        Ak = U.dot(np.diag(s).dot(Vh))
        percent_error = 100 * np.linalg.norm(A.conj().T - Ak) / np.linalg.norm(A.conj().T)
        
        assert percent_error < atol_float64 

    def test_rsvd_single_float64(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot( A.T )
        U, s, Vt = rsvd_single(A, k=k, p=5)
        Ak = U.dot(np.diag(s).dot(Vt))
        percent_error = 100 * np.linalg.norm(A - Ak) / np.linalg.norm(A)
        
        assert percent_error < atol_float64
           

    def test_rsvd_single_complex128(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64) + 1j * np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.conj().T)
        U, s, Vh = rsvd_single(A, k=k, p=5)
        Ak = U.dot(np.diag(s).dot(Vh))
        percent_error = 100 * np.linalg.norm(A - Ak) / np.linalg.norm(A)

    def test_rsvd_single_orthogonal_complex128(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64) + 1j * np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.conj().T)
        U, s, Vh = rsvd_single(A, k=k, p=5, sdist='orthogonal')
        Ak = U.dot(np.diag(s).dot(Vh))
        percent_error = 100 * np.linalg.norm(A - Ak) / np.linalg.norm(A)

    def test_rlu_float64(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.T)
        A = A[:,0:50]
        P, L, U, Q = rlu(A, permute=False, k=k, p=5, q=2)
        Ak = P.dot(L.dot(U)).dot(Q)        
        percent_error = 100 * np.linalg.norm(A - Ak) / np.linalg.norm(A)
        
        assert percent_error < atol_float64  
  
		    
    def test_rlu_complex128(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64) + 1j * np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.conj().T)
        A = A[:,0:50]
        P, L, U, Q = rlu(A, permute=False, k=k, p=5, q=2)
        Ak = P.dot(L.dot(U)).dot(Q)        
        percent_error = 100 * np.linalg.norm(A - Ak) / np.linalg.norm(A)
        
        assert percent_error < atol_float64 

    def test_rlu_permute_float64(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.T)
        A = A[:,0:50]
        L, U, = rlu(A, permute=True, k=k, p=5, q=2)
        Ak = L.dot(U)        
        percent_error = 100 * np.linalg.norm(A - Ak) / np.linalg.norm(A)
        
        assert percent_error < atol_float64  
  
		    
    def test_rlu_permute_complex128(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64) + 1j * np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.conj().T)
        A = A[:,0:50]
        L, U= rlu(A, permute=True, k=k, p=5, q=2)
        Ak = L.dot(U)        
        percent_error = 100 * np.linalg.norm(A - Ak) / np.linalg.norm(A)
        
        assert percent_error < atol_float64 
        
        
#
#******************************************************************************
#
class test_cur(TestCase):
    def setUp(self):
        np.random.seed(123)

    def test_id_col(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.T)
        A = A[:,0:50]
        
        # index_set = False
        C, V = interp_decomp(A, k=k+2, mode='column', index_set=False)
        relative_error = (np.linalg.norm(A - C.dot(V)) / np.linalg.norm(A))
        assert relative_error < 1e-4  

        # index_set = True
        C, V = interp_decomp(A, k=k+2, mode='column', index_set=True)
        relative_error = (np.linalg.norm(A - A[:,C].dot(V)) / np.linalg.norm(A))
        assert relative_error < 1e-4  

    def test_id_row(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.T)
        A = A[:,0:50]
        
        # index_set = False
        Z, R = interp_decomp(A, k=k+2, mode='row', index_set=False)
        relative_error = (np.linalg.norm(A - Z.dot(R)) / np.linalg.norm(A))
        assert relative_error < 1e-4  

        # index_set = True
        Z, R = interp_decomp(A, k=k+2, mode='row', index_set=True)
        relative_error = (np.linalg.norm(A - Z.dot(A[R,:])) / np.linalg.norm(A))
        assert relative_error < 1e-4 
     

    def test_rid_col(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.T)
        A = A[:,0:50]
        
        # index_set = False
        C, V = rinterp_decomp(A, k=k+2, mode='column', index_set=False)
        relative_error = (np.linalg.norm(A - C.dot(V)) / np.linalg.norm(A))
        assert relative_error < 1e-4  

        # index_set = True
        C, V = rinterp_decomp(A, k=k+2, mode='column', index_set=True)
        relative_error = (np.linalg.norm(A - A[:,C].dot(V)) / np.linalg.norm(A))
        assert relative_error < 1e-4  

    def test_rid_row(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.T)
        A = A[:,0:50]
        
        # index_set = False
        Z, R = rinterp_decomp(A, k=k+2, mode='row', index_set=False)
        relative_error = (np.linalg.norm(A - Z.dot(R)) / np.linalg.norm(A))
        assert relative_error < 1e-4  

        # index_set = True
        Z, R = rinterp_decomp(A, k=k+2, mode='row', index_set=True)
        relative_error = (np.linalg.norm(A - Z.dot(A[R,:])) / np.linalg.norm(A))
        assert relative_error < 1e-4        

    def test_ridqb_col(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.T)
        A = A[:,0:50]
        
        # index_set = False
        C, V = rinterp_decomp_qb(A, k=k+2, mode='column', index_set=False)
        relative_error = (np.linalg.norm(A - C.dot(V)) / np.linalg.norm(A))
        assert relative_error < 1e-4  

        # index_set = True
        C, V = rinterp_decomp_qb(A, k=k+2, mode='column', index_set=True)
        relative_error = (np.linalg.norm(A - A[:,C].dot(V)) / np.linalg.norm(A))
        assert relative_error < 1e-4  


    def test_ridqb_row(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.T)
        A = A[:,0:50]
        
        # index_set = False
        Z, R = rinterp_decomp_qb(A, k=k+2, mode='row', index_set=False)
        relative_error = (np.linalg.norm(A - Z.dot(R)) / np.linalg.norm(A))
        assert relative_error < 1e-4  

        # index_set = True
        Z, R = rinterp_decomp_qb(A, k=k+2, mode='row', index_set=True)
        relative_error = (np.linalg.norm(A - Z.dot(A[R,:])) / np.linalg.norm(A))
        assert relative_error < 1e-4  
        
        
    def test_cur(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.T)
        A = A[:,0:50]
        
        # index_set = False
        C, U, R = cur(A, k=k+2, index_set=False)
        relative_error = (np.linalg.norm(A - C.dot(U).dot(R)) / np.linalg.norm(A))
        assert relative_error < 1e-4  

        # index_set = True
        C, U, R = cur(A, k=k+2, index_set=True)
        relative_error = (np.linalg.norm(A - A[:,C].dot(U).dot(A[R,:])) / np.linalg.norm(A))
        assert relative_error < 1e-4        


    def test_cur(self):
        m, k = 100, 10
        A = np.array(np.random.randn(m, k), np.float64)
        A = A.dot(A.T)
        A = A[:,0:50]
        
        # index_set = False
        C, U, R = rcur(A, k=k+2, index_set=False)
        relative_error = (np.linalg.norm(A - C.dot(U).dot(R)) / np.linalg.norm(A))
        assert relative_error < 1e-4  

        # index_set = True
        C, U, R = rcur(A, k=k+2, index_set=True)
        relative_error = (np.linalg.norm(A - A[:,C].dot(U).dot(A[R,:])) / np.linalg.norm(A))
        assert relative_error < 1e-4 

                
#
#******************************************************************************
#
class test_nmf(TestCase):
    def setUp(self):
        np.random.seed(123)

    def test_rnmf_fhals(self):
        A, Anoisy = nmf_data(100, 100, 10, factor_type='normal', noise_type='normal',  noiselevel=0)
        W, H = rnmf_fhals(Anoisy, k=10)

        relative_error = (np.linalg.norm(A - W.dot(H)) / np.linalg.norm(A))
        assert relative_error < 1e-4  


    def test_nmf_fhals(self):
        A, Anoisy = nmf_data(100, 100, 10, factor_type='normal', noise_type='normal',  noiselevel=0)
        W, H = nmf_fhals(Anoisy, k=10)
		
        relative_error = (np.linalg.norm(A - W.dot(H)) / np.linalg.norm(A))
        assert relative_error < 1e-4  
     


#
#******************************************************************************
#
  

class test_dmd(TestCase):
    def setUp(self):
        np.random.seed(123)        
        
    def test_dmd(self):
        # Define time and space discretizations
        x=np.linspace( -10, 10, 100)
        t=np.linspace(0, 8*np.pi , 60) 
        dt=t[2]-t[1]
        X, T = np.meshgrid(x,t)
        # Create two patio-temporal patterns
        F1 = 0.5* np.cos(X)*(1.+0.* T)
        F2 = ( (1./np.cosh(X)) * np.tanh(X)) *(2.*np.exp(1j*2.8*T))
        A = np.array((F1+F2).T, order='C')
        
        Fmodes, b, V, omega = dmd(A, k=2, modes='standard', return_amplitudes=True, return_vandermonde=True)
        Atilde = Fmodes.dot( np.dot(np.diag(b), V))        
        assert np.allclose(A, Atilde, atol_float64)   
        
        Fmodes, b, V, omega = dmd(A, modes='standard', return_amplitudes=True, return_vandermonde=True)
        Atilde = Fmodes.dot( np.dot(np.diag(b), V))        
        assert np.allclose(A, Atilde, atol_float64)          

        Fmodes, b, V, omega = dmd(A, modes='exact', return_amplitudes=True, return_vandermonde=True)
        Atilde = Fmodes.dot( np.dot(np.diag(b), V))        
        assert np.allclose(A, Atilde, atol_float64)          
        


    def test_rdmd(self):
        # Define time and space discretizations
        x=np.linspace( -10, 10, 100)
        t=np.linspace(0, 8*np.pi , 60) 
        dt=t[2]-t[1]
        X, T = np.meshgrid(x,t)
        # Create two patio-temporal patterns
        F1 = 0.5* np.cos(X)*(1.+0.* T)
        F2 = ( (1./np.cosh(X)) * np.tanh(X)) *(2.*np.exp(1j*2.8*T))
        A = np.array((F1+F2).T, order='C')
        
        Fmodes, b, V, omega = rdmd(A, k=2, p=10, q=2, sdist='uniform', return_amplitudes=True, return_vandermonde=True)
        Atilde = Fmodes.dot( np.dot(np.diag(b), V))        
        assert np.allclose(A, Atilde, atol_float64) 

        Fmodes, b, V, omega = rdmd(A, k=2, p=10, q=2, sdist='normal', return_amplitudes=True, return_vandermonde=True)
        Atilde = Fmodes.dot( np.dot(np.diag(b), V))        
        assert np.allclose(A, Atilde, atol_float64) 


    def test_rdmd_single(self):
        # Define time and space discretizations
        x=np.linspace( -10, 10, 100)
        t=np.linspace(0, 8*np.pi , 60) 
        dt=t[2]-t[1]
        X, T = np.meshgrid(x,t)
        # Create two patio-temporal patterns
        F1 = 0.5* np.cos(X)*(1.+0.* T)
        F2 = ( (1./np.cosh(X)) * np.tanh(X)) *(2.*np.exp(1j*2.8*T))
        A = np.array((F1+F2).T, order='C')
        
        Fmodes, b, V, omega = rdmd_single(A, k=2, p=10, l=20, sdist='uniform', return_amplitudes=True, return_vandermonde=True)
        Atilde = Fmodes.dot( np.dot(np.diag(b), V))        
        assert np.allclose(A, Atilde, atol_float64) 

        Fmodes, b, V, omega = rdmd_single(A, k=2, p=10, l=20, sdist='orthogonal', return_amplitudes=True, return_vandermonde=True)
        Atilde = Fmodes.dot( np.dot(np.diag(b), V))        
        assert np.allclose(A, Atilde, atol_float64) 


#
#******************************************************************************
#
class test_random_qr(TestCase):
    def setUp(self):
        np.random.seed(123)

    def test_random_sketch(self):
        A = np.random.rand(50,100).astype(np.float16)
        r = 10

        sketch = _random_sketch(A, r)

        assert( sketch.shape == (50,r) )
        assert( sketch.dtype == A.dtype )

    def test_random_sketch_blocked(self):
        A = np.random.rand(50,100)
        r = 10

        np.random.seed(123)
        sketch = _random_sketch(A, r)

        np.random.seed(123)
        blocked = _random_sketch(A, r, n_blocks=5)

        assert_array_almost_equal( sketch, blocked )

    def test_power_iterations(self):
        A = np.random.rand(50,100).astype(np.float32)
        Y = np.random.rand(50,10).astype(np.float32)
        n = 5

        out = _power_iterations(A, Y.copy(), n_iters=n)

        assert( out.dtype == A.dtype )

    def test_power_iterations_blocked(self):
        A = np.random.rand(50,100).astype(np.float32)
        Y = np.random.rand(50,10).astype(np.float32)
        n = 5

        out = _power_iterations(A, Y.copy(), n_iters=n)
        blocked = _power_iterations(A, Y.copy(), n_iters=n, n_blocks=10)

        assert_array_almost_equal( out, blocked )

    def test_randomized_qr_sample(self):
        # ensure truely low dim
        l = np.random.rand(50,10)
        r = np.random.rand(10,100)
        A = l.dot(r)
        k = 10

        random = randomized_qr_sample( A, target_rank=k, oversample=50,
                                       n_iters=10)
        _, _, P = sci.linalg.qr(A.T, mode='economic', overwrite_a=False,
                                      pivoting=True)

        assert_array_almost_equal( random, P[:k] )

    def test_randomized_qr_sample_blocked(self):
        l = np.random.rand(100,10)
        r = np.random.rand(10,200)
        A = l.dot(r)
        k = 10

        np.random.seed(123)
        random = randomized_qr_sample( A, target_rank=k, oversample=50,
                                       n_iters=10)

        np.random.seed(123)
        blocked = randomized_qr_sample( A, target_rank=k, oversample=50,
                                        n_iters=10, n_blocks=5)

        assert_array_almost_equal( random, blocked )

#
#******************************************************************************
#

def suite():
    s = TestSuite()

    return s

if __name__ == '__main__':
    main(defaultTest = 'suite')
