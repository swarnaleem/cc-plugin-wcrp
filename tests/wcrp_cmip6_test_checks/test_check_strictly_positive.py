#!/usr/bin/env python
"""
Test for check_strictly_positive.py
"""

import os
import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


class TestCheckStrictlyPositive(BaseTestCase):
    """Tests for strictly positive value checks."""

    # NOMINAL TEST CASES 

    def test_check_height_strictly_positive_pass(self):
        """Test that positive height values pass."""

        dataset = MockNetCDF()
        dataset.createDimension("height", 5)
        height_var = dataset.createVariable("height", "f", ("height",))
        height_var[:] = np.array([1.0, 5.0, 10.0, 50.0, 100.0])

        from checks.variable_checks.check_strictly_positive import check_height_strictly_positive
        results = check_height_strictly_positive(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_i_strictly_positive_pass(self):
        """Test that positive i values pass."""

        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        i_var = dataset.createVariable("i", "i", ("i",))
        i_var[:] = np.array([1, 2, 3, 4, 5])

        from checks.variable_checks.check_strictly_positive import check_i_strictly_positive
        results = check_i_strictly_positive(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_j_strictly_positive_pass(self):
        """Test that positive j values pass."""

        dataset = MockNetCDF()
        dataset.createDimension("j", 5)
        j_var = dataset.createVariable("j", "i", ("j",))
        j_var[:] = np.array([1, 2, 3, 4, 5])

        from checks.variable_checks.check_strictly_positive import check_j_strictly_positive
        results = check_j_strictly_positive(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    # ERROR TEST CASES

    def test_check_height_strictly_positive_fails_zero(self):
        """Test that zero height value fails."""

        dataset = MockNetCDF()
        dataset.createDimension("height", 5)
        height_var = dataset.createVariable("height", "f", ("height",))
        height_var[:] = np.array([0.0, 5.0, 10.0, 50.0, 100.0])  # 0 is invalid

        from checks.variable_checks.check_strictly_positive import check_height_strictly_positive
        results = check_height_strictly_positive(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "not strictly positive" in results[0].msgs[0]

    def test_check_height_strictly_positive_fails_negative(self):
        """Test that negative height value fails."""

        dataset = MockNetCDF()
        dataset.createDimension("height", 5)
        height_var = dataset.createVariable("height", "f", ("height",))
        height_var[:] = np.array([-5.0, 5.0, 10.0, 50.0, 100.0])  # -5 is invalid

        from checks.variable_checks.check_strictly_positive import check_height_strictly_positive
        results = check_height_strictly_positive(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "not strictly positive" in results[0].msgs[0]

    def test_check_i_strictly_positive_fails_zero(self):
        """Test that zero i value fails."""

        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        i_var = dataset.createVariable("i", "i", ("i",))
        i_var[:] = np.array([0, 1, 2, 3, 4])  # 0 is invalid

        from checks.variable_checks.check_strictly_positive import check_i_strictly_positive
        results = check_i_strictly_positive(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "not strictly positive" in results[0].msgs[0]

    def test_check_height_strictly_positive_fails_variable_not_found(self):
        """Test that missing height variable fails."""

        dataset = MockNetCDF()
        # No height variable created

        from checks.variable_checks.check_strictly_positive import check_height_strictly_positive
        results = check_height_strictly_positive(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "not found" in results[0].msgs[0]
