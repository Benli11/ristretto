""" 
Randomized Singular Value Decomposition
"""
# Author: N. Benjamin Erichson
# License: GNU General Public License v3.0

from __future__ import division

import numpy as np
import scipy as sci
from scipy import linalg
import scipy.sparse.linalg as scislin
 
#matrix transpose for real matricies
def rT(A): 
    return A.T
    
#matrix transpose for complex matricies
def cT(A): 
    return A.conj().T      

epsi = np.finfo(np.float32).eps


def reigh(A, k, p=20, q=2, sdist='normal'):
    """
    Randomized eigendecompostion.
    
        
    
    Parameters
    ----------
    A : array_like, shape `(n, n)`.
        Hermitian matrix.
    
    k : integer, `k << n`.
        Target rank.
    
    p : integer, default: `p=10`.
        Parameter to control oversampling.

    q : integer, default: `q=2`.
        Parameter to control number of power (subspace) iterations.    
                  
    sdist : str `{'uniform', 'normal'}`, default: `sdist='uniform'`.
        'uniform' : Random test matrix with uniform distributed elements.
        
        'normal' : Random test matrix with normal distributed elements.     
    
    Returns
    -------
    w : array_like, 1-d array of length `k`.
        The eigenvalues.     
    
    v: array_like, shape `(n, k)`.
        The normalized selected eigenvector corresponding to the 
        eigenvalue w[i] is the column v[:,i].
    

    Notes
    -----   
    
    References
    ----------
    N. Halko, P. Martinsson, and J. Tropp.
    "Finding structure with randomness: probabilistic
    algorithms for constructing approximate matrix
    decompositions" (2009).
    (available at `arXiv <http://arxiv.org/abs/0909.4061>`_).
    
    
    Examples
    --------
    
    """
    
    m , n = A.shape 
    dat_type =  A.dtype   

    #p = int(np.floor(m*0.1))

    if  dat_type == sci.float32: 
        isreal = True
        real_type = sci.float32
        fT = rT
    elif dat_type == sci.float64: 
        isreal = True
        real_type = sci.float64  
        fT = rT
    elif dat_type == sci.complex64:
        isreal = False 
        real_type = sci.float32
        fT = cT
    elif dat_type == sci.complex128:
        isreal = False 
        real_type = sci.float64
        fT = cT
    else:
        raise ValueError( "A.dtype is not supported" )
    
    if k is None:
        raise ValueError( "Target rank k is required." )

    if k < 0:
        raise ValueError( "Target rank k not valid." )
        
    if k > min(m,n):
        k = min(m,n)       
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Generate a random test matrix Omega
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if sdist=='uniform':   
        Omega = np.array( sci.random.uniform( -1 , 1 , size=( n, k+p ) ) , dtype = dat_type ) 
        if isreal==False: 
            Omega += 1j * sci.array( sci.random.uniform(-1 , 1 , size=( n, k+p  ) ) , dtype = real_type )
      
    elif sdist=='normal':   
        Omega = np.array( sci.random.standard_normal( size=( n, k+p  ) ) , dtype = dat_type ) 
        if isreal==False: 
            Omega += 1j * sci.array( sci.random.standard_normal( size=( n, k+p  ) ) , dtype = real_type )     

    else: 
        raise ValueError('Sampling distribution is not supported.')    
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Build sample matrix Y : Y = A * Omega
    #Note: Y should approximate the range of A
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    Y = A.dot( Omega )
    del( Omega )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Orthogonalize Y using economic QR decomposition: Y=QR
    #If q > 0 perfrom q subspace iterations
    #Note: check_finite=False may give a performance gain
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~      
    s=1 #control parameter for number of orthogonalizations
    if q > 0:
        for i in np.arange( 1, q+1 ):
            if( (2*i-2) % s == 0 ):
                Y , _ = sci.linalg.qr( Y , mode='economic', check_finite=False, overwrite_a=True )
                        
            if( (2*i-1) % s == 0 ):
                Z , _ = sci.linalg.qr( fT( A ).dot( Y ) , mode='economic', check_finite=False, overwrite_a=True)
       
            Y = A.dot( Z )
        #End for
     #End if       
        
    Q , _ = sci.linalg.qr( Y ,  mode='economic' , check_finite=False, overwrite_a=True ) 
    del(Y)    
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Project the data matrix a into a lower dimensional subspace
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    B = A.dot(Q)
    B = fT(Q).dot(B)

    B = (B + fT(B)) / 2 # Symmetry

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Eigendecompositoin
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    w, v = sci.linalg.eigh(B,  eigvals_only=False, overwrite_a=True,  
                           turbo=True, eigvals=None, type=1, check_finite=True)


    v[ : , :n ] = v[ : , n-1::-1 ]         
    w = w[ ::-1 ]

    return ( w[0:k] , (Q.dot(v))[:,0:k] ) 

    

    #**************************************************************************   
    #End reigen
    #**************************************************************************       




def reigh_nystroem(A, k, p=10, q=2, sdist='normal'):
    """
    Randomized eigendecompostion using the Nystroem method.
    
        
    
    Parameters
    ----------
    A : array_like, shape `(n, n)`.
        Positive-definite matrix (PSD) input matrix.
    
    k : integer, `k << n`.
        Target rank.
    
    p : integer, default: `p=10`.
        Parameter to control oversampling.

    q : integer, default: `q=2`.
        Parameter to control number of power (subspace) iterations.    
                  
    sdist : str `{'uniform', 'normal'}`, default: `sdist='uniform'`.
        'uniform' : Random test matrix with uniform distributed elements.
        
        'normal' : Random test matrix with normal distributed elements.     
    
    Returns
    -------
    w : array_like, 1-d array of length `k`.
        The eigenvalues.     
    
    v: array_like, shape `(n, k)`.
        The normalized selected eigenvector corresponding 
        to the eigenvalue w[i] is the column v[:,i].
    

    Notes
    -----   
    
    References
    ----------
    N. Halko, P. Martinsson, and J. Tropp.
    "Finding structure with randomness: probabilistic
    algorithms for constructing approximate matrix
    decompositions" (2009).
    (available at `arXiv <http://arxiv.org/abs/0909.4061>`_).
    
    
    Examples
    --------
    
    """

    # Shape of input matrix 
    m , n = A.shape 
    dat_type =  A.dtype   

    if  dat_type == sci.float32: 
        isreal = True
        real_type = sci.float32
        fT = rT
    elif dat_type == sci.float64: 
        isreal = True
        real_type = sci.float64  
        fT = rT
    elif dat_type == sci.complex64:
        isreal = False 
        real_type = sci.float32
        fT = cT
    elif dat_type == sci.complex128:
        isreal = False 
        real_type = sci.float64
        fT = cT
    else:
        raise ValueError( "A.dtype is not supported" )
    
    if k is None:
        raise ValueError( "Target rank k is required." )

    if k < 0:
        raise ValueError( "Target rank k not valid." )
        
    if k > min(m,n):
        k = min(m,n)       
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Generate a random test matrix Omega
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if sdist=='uniform':   
        Omega = np.array( sci.random.uniform( -1 , 1 , size=( n, k+p ) ) , dtype = dat_type ) 
        if isreal==False: 
            Omega += 1j * sci.array( sci.random.uniform(-1 , 1 , size=( n, k+p  ) ) , dtype = real_type )
      
    elif sdist=='normal':   
        Omega = np.array( sci.random.standard_normal( size=( n, k+p  ) ) , dtype = dat_type ) 
        if isreal==False: 
            Omega += 1j * sci.array( sci.random.standard_normal( size=( n, k+p  ) ) , dtype = real_type )     

    else: 
        raise ValueError('Sampling distribution is not supported.')    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Build sample matrix Y : Y = A * Omega
    #Note: Y should approximate the range of A
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    Y = A.dot( Omega )
    del( Omega )
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Orthogonalize Y using economic QR decomposition: Y=QR
    #If q > 0 perfrom q subspace iterations
    #Note: check_finite=False may give a performance gain
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~      
    s=1 #control parameter for number of orthogonalizations
    if q > 0:
        for i in np.arange( 1, q+1 ):
            if( (2*i-2) % s == 0 ):
                Y , _ = sci.linalg.qr( Y , mode='economic', check_finite=False, overwrite_a=True )
                        
            if( (2*i-1) % s == 0 ):
                Z , _ = sci.linalg.qr( fT( A ).dot( Y ) , mode='economic', check_finite=False, overwrite_a=True)
       
            Y = A.dot( Z )
        #End for
     #End if       
        
    Q , _ = sci.linalg.qr( Y ,  mode='economic' , check_finite=False, overwrite_a=True ) 
    del(Y)    
        

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Project the data matrix a into a lower dimensional subspace
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    B1 = A.dot(Q)
    B2 = fT(Q).dot(B1)

    B2 = (B2 + fT(B2)) / 2 # Symmetry

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Cholesky factorizatoin
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    #C = sci.linalg.cholesky(B2, lower=True, overwrite_a=True, check_finite=True)
    #C = sci.linalg.cho_factor(B2, lower=True, overwrite_a=True, check_finite=True)
    try:
        C = sci.linalg.cholesky(B2, lower=True, overwrite_a=True, check_finite=True)
    except:
        print("Cholesky factorizatoin has failed, because array is not positive definite.")
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Eigendecompositoin
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        w, v = sci.linalg.eigh(B2,  eigvals_only=False, overwrite_a=True,  
                               turbo=True, eigvals=None, type=1, check_finite=True)
    
    
        v[ : , :n ] = v[ : , n-1::-1 ]         
        w = w[ ::-1 ]
    
        return ( w[0:k] , (Q.dot(v))[:,0:k] ) 

    
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Upper triangular solve
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~     
    F = sci.linalg.solve_triangular(a=C, b=fT(B1),  lower=True, 
                                   unit_diagonal=False, overwrite_b=True, 
                                   debug=None, check_finite=True)

    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Singular Value Decomposition
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~      
    #Compute SVD
    v , w , _ = sci.linalg.svd( fT(F) ,  compute_uv=True, full_matrices=False, 
                             overwrite_a=True, check_finite=False)
     

    #v , w , _ = sci.sparse.linalg.svds(fT(F), k=k, ncv=None, tol=0, which='LM', 
    #                                     v0=None, maxiter=None, return_singular_vectors=True)
 

    #v[ : , :n ] = v[ : , n-1::-1 ]         
    #w = w[ ::-1 ]

    return ( w[0:k]**2 , v[:,0:k] ) 

    #**************************************************************************   
    #End reigen
    #**************************************************************************     
    
 








def reigh_nystroem_col(A, k, p=0):
    """
    Randomized eigendecompostion using the Nystroem method.
    
        
    
    Parameters
    ----------
    A : array_like, shape `(n, n)`.
        Positive-definite matrix (PSD) input matrix.
    
    k : integer, `k << n`.
        Target rank.
    
    p : integer, default: `p=0`.
        Parameter to control oversampling.
    
    
    Returns
    -------
    w : array_like, 1-d array of length `k`.
        The eigenvalues.     
    
    v: array_like, shape `(n, k)`.
        The normalized selected eigenvector corresponding 
        to the eigenvalue w[i] is the column v[:,i].
    

    Notes
    -----   
    
    References
    ----------
    N. Halko, P. Martinsson, and J. Tropp.
    "Finding structure with randomness: probabilistic
    algorithms for constructing approximate matrix
    decompositions" (2009).
    (available at `arXiv <http://arxiv.org/abs/0909.4061>`_).
    
    
    Examples
    --------
    
    """

    # Shape of input matrix 
    m , n = A.shape 
    dat_type =  A.dtype   

    if  dat_type == sci.float32: 
        isreal = True
        real_type = sci.float32
        fT = rT
    elif dat_type == sci.float64: 
        isreal = True
        real_type = sci.float64  
        fT = rT
    elif dat_type == sci.complex64:
        isreal = False 
        real_type = sci.float32
        fT = cT
    elif dat_type == sci.complex128:
        isreal = False 
        real_type = sci.float64
        fT = cT
    else:
        raise ValueError( "A.dtype is not supported" )
    
    if k is None:
        raise ValueError( "Target rank k is required." )

    if k < 0:
        raise ValueError( "Target rank k not valid." )
        
    if k > min(m,n):
        k = min(m,n)       
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Generate a random test matrix Omega
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #p_col = sci.linalg.norm(A, axis=1)**2 / sci.linalg.norm(A)**2
    #idx = sci.sort(sci.random.choice(range(n), size = int(k+p), replace = False, p = p_col))
    idx = sci.sort(sci.random.choice(range(n), size = int(k+p), replace = False, p = None))

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Project the data matrix a into a lower dimensional subspace
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    B1 = A[:,idx]
    B2 = B1[idx,:].copy()

    B2 = (B2 + fT(B2)) / 2 # Symmetry

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Cholesky factorizatoin
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    try:
        C = sci.linalg.cholesky(B2, lower=True, overwrite_a=True, check_finite=True)
    except:
        print("Cholesky factorizatoin has failed, because array is not positive definite.")
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Eigendecompositoin
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        U, s, _ = sci.linalg.svd(B2,  full_matrices=False, overwrite_a=True)

    
        
        U = B1.dot(U  * s  **-1)
        U = U[:,0:k] * np.sqrt(k / n)
        s = s[0:k] * (n / k)         
        
    
        return ( s[0:k]**2 , U) 
    
    

    #C = sci.linalg.cho_factor(B2, lower=True, overwrite_a=True, check_finite=True)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Upper triangular solve
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~     
    F = sci.linalg.solve_triangular(a=C, b=fT(B1),  lower=True, 
                                   unit_diagonal=False, overwrite_b=True, 
                                   debug=None, check_finite=True)

    #F = sci.linalg.cho_solve(C, b=fT(B1), overwrite_b=True, check_finite=True)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Singular Value Decomposition
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~      
    #Compute SVD
    v , w , _ = sci.linalg.svd( fT(F) ,  compute_uv=True, full_matrices=False, 
                              overwrite_a=True, check_finite=False)
     
 

    return ( w[0:k]**2 , v[:,0:k] ) 

    #**************************************************************************   
    #End reigen
    #**************************************************************************     
    
     
