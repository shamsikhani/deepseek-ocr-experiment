# Second-Order Elliptic Equations

## Chapter 6 Solutions

### 6.1 General Form

The general form of a second-order elliptic equation is:

$$\sum_{i,j=1}^n a_{ij}(x)\frac{\partial^2 u}{\partial x_i \partial x_j} + \sum_{i=1}^n b_i(x)\frac{\partial u}{\partial x_i} + c(x)u = f(x)$$

where the coefficient matrix $(a_{ij})$ is positive definite.

### 6.2 Boundary Conditions

#### Dirichlet Boundary Conditions
$$u|_{\partial \Omega} = g$$

#### Neumann Boundary Conditions
$$\frac{\partial u}{\partial n}\bigg|_{\partial \Omega} = h$$

#### Mixed Boundary Conditions
$$\alpha u + \beta \frac{\partial u}{\partial n}\bigg|_{\partial \Omega} = \gamma$$

### 6.3 Existence and Uniqueness

**Theorem 6.1**: For the Dirichlet problem with continuous boundary data $g$ and $f \in L^2(\Omega)$, there exists a unique weak solution $u \in H_0^1(\Omega)$.

**Proof Outline**:
1. Apply the Lax-Milgram theorem
2. Show coercivity of the bilinear form
3. Establish continuity conditions

### 6.4 Maximum Principle

**Maximum Principle**: Let $u$ satisfy the elliptic equation with $c(x) \leq 0$. Then:

$$\max_{\overline{\Omega}} u = \max_{\partial \Omega} u$$

#### Applications
- Uniqueness of solutions
- Comparison principles
- A priori estimates

### 6.5 Regularity Theory

#### Interior Regularity
If $f \in C^k(\Omega)$ and coefficients are $C^k$, then $u \in C^{k+2}(\Omega)$.

#### Boundary Regularity
Regularity near the boundary depends on:
- Smoothness of $\partial \Omega$
- Compatibility conditions
- Type of boundary conditions

### 6.6 Numerical Methods

#### Finite Element Method
1. Weak formulation
2. Discretization
3. Assembly of system matrix
4. Solution of linear system

#### Finite Difference Method
- Central differences for second derivatives
- Stability analysis
- Convergence rates
