#!/usr/bin/env python
"""
Test for check_bounds_monotonicity.py
"""

import os
import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


class TestCheckBoundsMonotonicity(BaseTestCase):
    """Tests for bounds monotonicity checks."""
    def test_check_lat_bnds_monotonicity_pass(self):
        """Test that monotonically increasing lat_bnds pass."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        dataset.createDimension("bnds", 2)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))
        lat_bnds_var[:] = np.array([[-90.0, -30.0], [-30.0, 30.0], [30.0, 90.0]])

        from checks.variable_checks.check_bounds_monotonicity import check_lat_bnds_monotonicity
        results = check_lat_bnds_monotonicity(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lon_bnds_monotonicity_pass(self):
        """Test that monotonically increasing lon_bnds pass."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 3)
        dataset.createDimension("bnds", 2)
        lon_bnds_var = dataset.createVariable("lon_bnds", "f", ("lon", "bnds"))
        lon_bnds_var[:] = np.array([[0.0, 120.0], [120.0, 240.0], [240.0, 360.0]])

        from checks.variable_checks.check_bounds_monotonicity import check_lon_bnds_monotonicity
        results = check_lon_bnds_monotonicity(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_bnds_monotonicity_pass_constant(self):
        """Test that constant bounds values (non-decreasing) pass."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        dataset.createDimension("bnds", 2)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))
        # Same lower bounds - still non-decreasing
        lat_bnds_var[:] = np.array([[0.0, 30.0], [0.0, 30.0], [0.0, 30.0]])

        from checks.variable_checks.check_bounds_monotonicity import check_lat_bnds_monotonicity
        results = check_lat_bnds_monotonicity(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    # ERROR TEST CASES

    def test_check_lat_bnds_monotonicity_fails_lower(self):
        """Test that non-monotonic lower bounds fail."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        dataset.createDimension("bnds", 2)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))
        # Lower bounds are not monotonic: -90 > -100 (decreasing)
        lat_bnds_var[:] = np.array([[-90.0, -30.0], [-100.0, 30.0], [30.0, 90.0]])

        from checks.variable_checks.check_bounds_monotonicity import check_lat_bnds_monotonicity
        results = check_lat_bnds_monotonicity(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "Lower bounds not monotonic" in results[0].msgs[0]

    def test_check_lat_bnds_monotonicity_fails_upper(self):
        """Test that non-monotonic upper bounds fail."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        dataset.createDimension("bnds", 2)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))
        # Upper bounds are not monotonic: 30 > 10
        lat_bnds_var[:] = np.array([[-90.0, 30.0], [-30.0, 10.0], [30.0, 90.0]])

        from checks.variable_checks.check_bounds_monotonicity import check_lat_bnds_monotonicity
        results = check_lat_bnds_monotonicity(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "Upper bounds not monotonic" in results[0].msgs[0]

    def test_check_lat_bnds_monotonicity_fails_wrong_shape(self):
        """Test that bounds with wrong shape fail."""

        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat",))
        lat_bnds_var[:] = np.array([-90.0, 0.0, 90.0])

        from checks.variable_checks.check_bounds_monotonicity import check_lat_bnds_monotonicity
        results = check_lat_bnds_monotonicity(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "unexpected shape" in results[0].msgs[0]

    def test_check_lat_bnds_monotonicity_fails_variable_not_found(self):
        """Test that missing lat_bnds variable fails."""

        dataset = MockNetCDF()
        # No lat_bnds variable created

        from checks.variable_checks.check_bounds_monotonicity import check_lat_bnds_monotonicity
        results = check_lat_bnds_monotonicity(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "not found" in results[0].msgs[0]
