#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Testing suite for MultiDensity class.

"""
from __future__ import print_function, division

import unittest as ut
import numpy as np
import numpy.testing as npt

from multidensity import MultiDensity


class MultiDensityTestCase(ut.TestCase):

    """Test MultiDensity distribution class."""

    def test_init(self):
        """Test __init__."""

        skst = MultiDensity()

        self.assertIsInstance(skst.eta, np.ndarray)
        self.assertIsInstance(skst.lam, np.ndarray)

        eta, lam = [10, 15], [.5, 1.5]
        skst = MultiDensity(eta=eta, lam=lam)

        npt.assert_array_equal(skst.eta, np.array(eta))
        npt.assert_array_equal(skst.lam, np.array(lam))


if __name__ == '__main__':
    ut.main()