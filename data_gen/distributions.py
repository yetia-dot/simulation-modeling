# data_gen/distributions.py
import numpy as np

def clipped_normal(mean, std, min_val=0):
    """Normal distribution clipped at min_val to avoid negatives."""
    sample = np.random.normal(mean, std)
    return max(sample, min_val)

def lognormal_from_mean_std(mean, std):
    """Convert mean/std to mu/sigma for lognormal distribution."""
    phi = np.sqrt(std**2 + mean**2)
    mu = np.log(mean**2 / phi)
    sigma = np.sqrt(np.log(phi**2 / mean**2))
    return np.random.lognormal(mu, sigma)
