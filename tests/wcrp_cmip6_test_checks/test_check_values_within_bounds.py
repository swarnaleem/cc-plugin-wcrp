#!/usr/bin/env python
"""
Tests for check_values_within_bounds.py - Values within bounds checks

Note: These tests focus on the wrapper functions correctly calling the underlying
check_bounds_value_consistency function.
"""

import numpy as np
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


class TestCheckValuesWithinBounds(BaseTestCase):
    """Tests for values within bounds checks."""

    # LAT VALUES WITHIN BOUNDS TESTS

    def test_check_lat_values_within_bounds_pass(self):
        """Test that lat values within bounds check passes when values are within bounds."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        dataset.createDimension("bnds", 2)

        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var[:] = np.array([-60.0, 0.0, 60.0])
        lat_var.bounds = "lat_bnds"

        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))
        lat_bnds_var[:] = np.array([[-90.0, -30.0], [-30.0, 30.0], [30.0, 90.0]])

        from checks.variable_checks.check_values_within_bounds import check_lat_values_within_bounds
        results = check_lat_values_within_bounds(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    # LON VALUES WITHIN BOUNDS TESTS

    def test_check_lon_values_within_bounds_pass(self):
        """Test that lon values within bounds check passes when values are within bounds."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 3)
        dataset.createDimension("bnds", 2)

        lon_var = dataset.createVariable("lon", "f", ("lon",))
        lon_var[:] = np.array([60.0, 180.0, 300.0])
        lon_var.bounds = "lon_bnds"

        lon_bnds_var = dataset.createVariable("lon_bnds", "f", ("lon", "bnds"))
        lon_bnds_var[:] = np.array([[0.0, 120.0], [120.0, 240.0], [240.0, 360.0]])

        from checks.variable_checks.check_values_within_bounds import check_lon_values_within_bounds
        results = check_lon_values_within_bounds(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])
