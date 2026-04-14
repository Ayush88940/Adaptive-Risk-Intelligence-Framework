import numpy as np

def calculate_ahp_weights(matrix: np.ndarray) -> np.ndarray:
    """
    Computes weights from a pairwise comparison matrix using the Eigenvector method.
    """
    # 1. Compute the principal eigenvector
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    max_index = np.argmax(np.abs(eigenvalues))
    principal_eigenvector = np.abs(eigenvectors[:, max_index])
    
    # 2. Normalize the eigenvector to get weights
    weights = principal_eigenvector / np.sum(principal_eigenvector)
    return weights

def get_adaptive_weights():
    """
    Returns the weights for [Severity, Exploitability, Stage, Exposure] 
    based on a pre-defined pairwise comparison matrix.
    
    Matrix justification: 
    - Stage (Environment) is prioritized over raw Severity for 'Adaptivity'.
    - Severity and Exploitability are balanced.
    - Exposure is a secondary multiplier.
    """
    # Matrix: [Sev, Expl, Stage, Exp]
    # Rows/Cols corresponding to: 
    # 0: Severity
    # 1: Exploitability
    # 2: Stage
    # 3: Exposure
    
    matrix = np.array([
        [1.0,  1.0,  0.5,  2.0],  # Severity vs others
        [1.0,  1.0,  0.5,  2.0],  # Exploitability vs others
        [2.0,  2.0,  1.0,  3.0],  # Stage vs others
        [0.5,  0.5,  0.33, 1.0]   # Exposure vs others
    ])
    
    weights = calculate_ahp_weights(matrix)
    return {
        "severity": weights[0],
        "exploitability": weights[1],
        "stage": weights[2],
        "exposure": weights[3]
    }

if __name__ == "__main__":
    w = get_adaptive_weights()
    print("AHP Weights:")
    for key, val in w.items():
        print(f"  {key}: {val:.4f}")
    print(f"  Sum: {sum(w.values()):.4f}")
