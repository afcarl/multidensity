#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
Multivariate Skewed Normal (Azzalini & Capitanio)
=================================================

"""
from __future__ import print_function, division

import numpy as np

import scipy.stats as scs
import scipy.linalg as scl

from .multidensity import MultiDensity
from .mvn import MvN

__all__ = ['MvSN']


class MvSN(MultiDensity):

    """Multidimensional Skewed Normal Distribution (Azzalini & Capitanio).

    Attributes
    ----------
    lam : array_like
        Asymmetry. :math:`-\infty < \lambda < \infty`
    data : array_like
        Data grid

    Methods
    -------
    from_theta
        Initialize individual parameters from theta
    cdf
        Cumulative density function (CDF)
    rvs
        Simulate random variables

    """

    def __init__(self, ndim=None, lam=[.5, 1.5],
                 mu=None, sigma=None, data=None):
        """Initialize the class.

        Parameters
        ----------
        lam : array_like
            Asymmetry. :math:`-\infty < \lambda < \infty`
        mu : array_like
            Constant in the mean. None for centered density.
        sigma : array_like
            Covariance matrix. None for standardized density.
        data : array_like
            Data grid

        """
        super(MvSN, self).__init__(ndim=ndim, lam=lam, data=data)
        self.mu = mu
        self.sigma = sigma

    def get_name(self):
        return 'Multivariate Skewed Normal'

    def from_theta(self, theta=[.5, 1.5]):
        """Initialize individual parameters from theta.

        Parameters
        ----------
        theta : array_like
            Density parameters

        """
        self.lam = np.array(theta)

    def theta_start(self, ndim=2):
        """Initialize parameter for optimization.

        Parameters
        ----------
        ndim : int
            Number of dimensions

        Returns
        -------
        int
            Parameters in one vector

        """
        return np.zeros(ndim)

    def const_mu(self):
        """Compute a constant.

        Returns
        -------
        (ndim, ) array

        """
        if self.mu is None:
            return -(2 / np.pi)**.5 \
                * self.const_delta() * self.const_omega()
        else:
            return np.array(self.mu)

    def const_sigma(self):
        """Compute a constant.

        Returns
        -------
        (ndim, ndim) array

        """
        if self.sigma is None:
            return np.eye(self.ndim)
        else:
            return np.array(self.sigma)

    def const_omega(self):
        """Compute a constant.

        Returns
        -------
        (ndim, ) array

        """
        if self.sigma is None:
            return np.ones(self.ndim)
        else:
            return np.diag(self.const_sigma())**.5

    def const_rho(self):
        """Compute a constant.

        Returns
        -------
        (ndim, ndim) array

        """
        if self.sigma is None:
            return np.eye(self.ndim)
        else:
            omega = self.const_omega()
            return self.const_sigma() / (omega[:, np.newaxis] * omega)

    def const_delta(self):
        """Compute a constant.

        Returns
        -------
        (ndim, ) array

        """
        if self.sigma is None:
            return self.lam / (1 + np.sum(self.lam ** 2))**.5
        else:
            norm_lam = scl.solve(self.const_rho(), self.lam)
            return norm_lam / (1 + np.sum(norm_lam * self.lam))**.5

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
        if data is None:
            raise ValueError('No data given!')
        self.data = np.atleast_2d(data)
        # (T, ) array
        norm_diff = np.sum((self.data - self.const_mu())
            / self.const_omega() * self.lam, 1)
        if self.lam.ndim == 1:
            norm_pdf = scs.multivariate_normal.pdf(self.data,
                                                   mean=self.const_mu(),
                                                   cov=self.const_sigma())
        elif self.lam.ndim == 2:
            cov = np.tile(self.const_sigma(), (self.data.shape[0], 1, 1))
            norm_pdf = MvN.pdf(self.data, mean=self.const_mu(), cov=cov)
        return 2 * norm_pdf * scs.norm.cdf(norm_diff)

    def cdf(self, data=None):
        """Cumulative density function (CDF).

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
        if data is None:
            raise ValueError('No data given!')
        self.data = np.atleast_2d(data)
        # (k, ) array
        omega = self.const_omega()
        rho = self.const_rho()
        norm_diff = (self.data - self.const_mu()) / omega
        delta = np.atleast_2d(self.const_delta())
        rho_ext = np.bmat([[np.ones((1, 1)), delta], [delta.T, rho]])
        norm_diff_ext = np.hstack((np.zeros((self.data.shape[0], 1)),
                                   norm_diff))
        low = -10 * np.ones(1 + self.ndim)
        mean = np.zeros(1 + self.ndim)
        # (http://www.nhsilbert.net/source/2014/04/
        # multivariate-normal-cdf-values-in-python/)
        mvncdf = [2 * scs.mvn.mvnun(low, x, mean, rho_ext)[0]
            for x in norm_diff_ext]
        if len(mvncdf) == 1:
            return mvncdf[0]
        else:
            return np.array(mvncdf)

    def rvs(self, size=10):
        """Simulate random variables.

        Parameters
        ----------
        size : int
            Number of data points

        Returns
        -------
        (size, ndim) array

        """
        rho = self.const_rho()
        delta = np.atleast_2d(self.const_delta())
        rho_ext = np.bmat([[np.ones((1, 1)), delta], [delta.T, rho]])
        normrv = scs.multivariate_normal.rvs(cov=rho_ext, size=size)
        ind = (normrv[:, 0] >= 0).astype(float)[:, np.newaxis]
        rvs = normrv[:, 1:] * (2 * ind - 1)
        return self.const_mu() + rvs * self.const_omega()
