#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
Multivariate Skewed Student Distribution (Bauwens & Laurent)
============================================================

Introduction
------------


References
----------


Examples
--------


"""
from __future__ import print_function, division

import numpy as np

from scipy.special import gamma

from .multidensity import MultiDensity

__all__ = ['SkStBL']


class SkStBL(MultiDensity):

    """Multidimensional density (Bauwens & Laurent).

    Attributes
    ----------
    eta : float
        Degrees of freedom. :math:`2 < \eta < \infty`
    lam : array_like
        Asymmetry. :math:`0 < \lambda < \infty`
    data : array_like
        Data grid

    Methods
    -------
    from_theta
        Initialize individual parameters from theta
    marginals
        Marginal drobability density functions
    pdf
        Probability density function
    loglikelihood
        Log-likelihood function
    fit_mle
        Fit parameters with MLE

    """

    def __init__(self, eta=10., lam=[.5, 1.5], data=[0, 0]):
        """Initialize the class.

        Parameters
        ----------
        eta : array_like
            Degrees of freedom. :math:`2 < \eta < \infty`
        lam : array_like
            Asymmetry. :math:`0 < \lambda < \infty`
        data : array_like
            Data grid

        """
        super(SkStBL, self).__init__(eta=eta, lam=lam, data=data)

    def from_theta(self, theta=[10., .5, 1.5]):
        """Initialize individual parameters from theta.

        Parameters
        ----------
        theta : array_like
            Density parameters

        """
        self.eta = np.atleast_1d(theta[0])
        self.lam = np.atleast_1d(theta[1:])

    def theta_start(self, ndim=2):
        """Initialize parameter for optimization.

        """
        eta = np.array([10])
        lam = np.ones(ndim)
        return np.concatenate((eta, lam))

    def pdf(self, data=None):
        """Probability density function (PDF).

        Parameters
        ----------
        data : array_like
            Grid of point to evaluate PDF at.

            (k,) - one observation, k dimensions

            (T, k) - T observations, k dimensions

        Returns
        -------
        (T, ) array
            PDF values

        """
        ndim = self.lam.size
        if data is None:
            raise ValueError('No data given!')
        self.data = np.atleast_2d(data)
        ind = - np.sign(self.data + self.const_a() / self.const_b())
        # (T, k) array
        kappa = (self.const_b() * self.data + self.const_a()) \
            * self.lam ** ind
        return (2 / (np.pi * (self.eta - 2)) ** .5) ** ndim \
            * gamma((self.eta + ndim) / 2) / gamma(self.eta / 2) \
            * (1 + np.sum(kappa * kappa, axis=1) / (self.eta - 2)) \
            ** (- (self.eta + ndim) / 2) \
            * np.prod(self.const_b() / (self.lam + 1. / self.lam))