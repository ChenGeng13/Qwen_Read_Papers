**Title**:Bayesian identification of nonseparable Hamiltonians with multiplicative noise using deep learning and reduced-order modeling
**Summary**:This paper presents a structure-preserving Bayesian approach for learning
nonseparable Hamiltonian systems using stochastic dynamic models allowing for
statistically-dependent, vector-valued additive and multiplicative measurement
noise. The approach is comprised of three main facets. First, we derive a
Gaussian filter for a statistically-dependent, vector-valued, additive and
multiplicative noise model that is needed to evaluate the likelihood within the
Bayesian posterior. Second, we develop a novel algorithm for cost-effective
application of Bayesian system identification to high-dimensional systems.
Third, we demonstrate how structure-preserving methods can be incorporated into
the proposed framework, using nonseparable Hamiltonians as an illustrative
system class. We assess the method's performance based on the forecasting
accuracy of a model estimated from-single trajectory data. We compare the
Bayesian method to a state-of-the-art machine learning method on a canonical
nonseparable Hamiltonian model and a chaotic double pendulum model with small,
noisy training datasets. The results show that using the Bayesian posterior as
a training objective can yield upwards of 724 times improvement in Hamiltonian
mean squared error using training data with up to 10% multiplicative noise
compared to a standard training objective. Lastly, we demonstrate the utility
of the novel algorithm for parameter estimation of a 64-dimensional model of
the spatially-discretized nonlinear Schr\"odinger equation with data corrupted
by up to 20% multiplicative noise.

**Title**:Bayesian identification of nonseparable Hamiltonians with multiplicative noise using deep learning and reduced-order modeling
**Summary**:This paper presents a structure-preserving Bayesian approach for learning
nonseparable Hamiltonian systems using stochastic dynamic models allowing for
statistically-dependent, vector-valued additive and multiplicative measurement
noise. The approach is comprised of three main facets. First, we derive a
Gaussian filter for a statistically-dependent, vector-valued, additive and
multiplicative noise model that is needed to evaluate the likelihood within the
Bayesian posterior. Second, we develop a novel algorithm for cost-effective
application of Bayesian system identification to high-dimensional systems.
Third, we demonstrate how structure-preserving methods can be incorporated into
the proposed framework, using nonseparable Hamiltonians as an illustrative
system class. We assess the method's performance based on the forecasting
accuracy of a model estimated from-single trajectory data. We compare the
Bayesian method to a state-of-the-art machine learning method on a canonical
nonseparable Hamiltonian model and a chaotic double pendulum model with small,
noisy training datasets. The results show that using the Bayesian posterior as
a training objective can yield upwards of 724 times improvement in Hamiltonian
mean squared error using training data with up to 10% multiplicative noise
compared to a standard training objective. Lastly, we demonstrate the utility
of the novel algorithm for parameter estimation of a 64-dimensional model of
the spatially-discretized nonlinear Schr\"odinger equation with data corrupted
by up to 20% multiplicative noise.

**Title**:Scaling and renormalization in high-dimensional regression
**Summary**:This paper presents a succinct derivation of the training and generalization
performance of a variety of high-dimensional ridge regression models using the
basic tools of random matrix theory and free probability. We provide an
introduction and review of recent results on these topics, aimed at readers
with backgrounds in physics and deep learning. Analytic formulas for the
training and generalization errors are obtained in a few lines of algebra
directly from the properties of the $S$-transform of free probability. This
allows for a straightforward identification of the sources of power-law scaling
in model performance. We compute the generalization error of a broad class of
random feature models. We find that in all models, the $S$-transform
corresponds to the train-test generalization gap, and yields an analogue of the
generalized-cross-validation estimator. Using these techniques, we derive
fine-grained bias-variance decompositions for a very general class of random
feature models with structured covariates. These novel results allow us to
discover a scaling regime for random feature models where the variance due to
the features limits performance in the overparameterized setting. We also
demonstrate how anisotropic weight structure in random feature models can limit
performance and lead to nontrivial exponents for finite-width corrections in
the overparameterized setting. Our results extend and provide a unifying
perspective on earlier models of neural scaling laws.

**Title**:An Understanding of Principal Differential Analysis
**Summary**:In functional data analysis, replicate observations of a smooth functional
process and its derivatives offer a unique opportunity to flexibly estimate
continuous-time ordinary differential equation models. Ramsay (1996) first
proposed to estimate a linear ordinary differential equation from functional
data in a technique called Principal Differential Analysis, by formulating a
functional regression in which the highest-order derivative of a function is
modelled as a time-varying linear combination of its lower-order derivatives.
Principal Differential Analysis was introduced as a technique for data
reduction and representation, using solutions of the estimated differential
equation as a basis to represent the functional data. In this work, we
re-formulate PDA as a generative statistical model in which functional
observations arise as solutions of a deterministic ODE that is forced by a
smooth random error process. This viewpoint defines a flexible class of
functional models based on differential equations and leads to an improved
understanding and characterisation of the sources of variability in Principal
Differential Analysis. It does, however, result in parameter estimates that can
be heavily biased under the standard estimation approach of PDA. Therefore, we
introduce an iterative bias-reduction algorithm that can be applied to improve
parameter estimates. We also examine the utility of our approach when the form
of the deterministic part of the differential equation is unknown and possibly
non-linear, where Principal Differential Analysis is treated as an approximate
model based on time-varying linearisation. We demonstrate our approach on
simulated data from linear and non-linear differential equations and on real
data from human movement biomechanics. Supplementary R code for this manuscript
is available at
\url{https://github.com/edwardgunning/UnderstandingOfPDAManuscript}.

**Title**:Bayesian $L_{\frac{1}{2}}$ regression
**Summary**:It is well known that Bridge regression enjoys superior theoretical
properties when compared to traditional LASSO. However, the current latent
variable representation of its Bayesian counterpart, based on the exponential
power prior, is computationally expensive in higher dimensions. In this paper,
we show that the exponential power prior has a closed form scale mixture of
normal decomposition for $\alpha=(\frac{1}{2})^\gamma, \gamma \in \{1,
2,\ldots\}$. We call these types of priors $L_{\frac{1}{2}}$ prior for short.
We develop an efficient partially collapsed Gibbs sampling scheme for
computation using the $L_{\frac{1}{2}}$ prior and study theoretical properties
when $p>n$. In addition, we introduce a non-separable Bridge penalty function
inspired by the fully Bayesian formulation and a novel, efficient coordinate
descent algorithm. We prove the algorithm's convergence and show that the local
minimizer from our optimisation algorithm has an oracle property. Finally,
simulation studies were carried out to illustrate the performance of the new
algorithms. Supplementary materials for this article are available online.

