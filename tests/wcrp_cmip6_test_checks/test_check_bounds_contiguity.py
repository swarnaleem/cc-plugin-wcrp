#!/usr/bin/env python
"""
Test for check_bounds_contiguity.py
"""

import os
import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


class TestCheckBoundsContiguity(BaseTestCase):
    """Tests for bounds contiguity checks."""

    def test_check_lat_bnds_contiguity_pass(self):
        """Test that contiguous lat_bnds pass."""

        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        dataset.createDimension("bnds", 2)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))

        # Upper bound of interval i equals lower bound of interval i+1
        lat_bnds_var[:] = np.array([[-90.0, -30.0], [-30.0, 30.0], [30.0, 90.0]])

        from checks.variable_checks.check_bounds_contiguity import check_lat_bnds_contiguity
        results = check_lat_bnds_contiguity(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lon_bnds_contiguity_pass(self):
        """Test that contiguous lon_bnds pass."""

        dataset = MockNetCDF()
        dataset.createDimension("lon", 3)
        dataset.createDimension("bnds", 2)
        lon_bnds_var = dataset.createVariable("lon_bnds", "f", ("lon", "bnds"))
        lon_bnds_var[:] = np.array([[0.0, 120.0], [120.0, 240.0], [240.0, 360.0]])

        from checks.variable_checks.check_bounds_contiguity import check_lon_bnds_contiguity
        results = check_lon_bnds_contiguity(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_bnds_contiguity_pass_single_interval(self):
        """Test that single interval bounds pass (nothing to check)."""
        
        dataset = MockNetCDF()
        dataset.createDimension("lat", 1)
        dataset.createDimension("bnds", 2)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))
        lat_bnds_var[:] = np.array([[-90.0, 90.0]])

        from checks.variable_checks.check_bounds_contiguity import check_lat_bnds_contiguity
        results = check_lat_bnds_contiguity(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    # ERROR TEST CASES

    def test_check_lat_bnds_contiguity_fails_gap(self):
        """Test that bounds with gaps fail."""
        
        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        dataset.createDimension("bnds", 2)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))

        # Gap between -30.0 and -20.0
        lat_bnds_var[:] = np.array([[-90.0, -30.0], [-20.0, 30.0], [30.0, 90.0]])

        from checks.variable_checks.check_bounds_contiguity import check_lat_bnds_contiguity
        results = check_lat_bnds_contiguity(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "gap" in results[0].msgs[0].lower()

    def test_check_lat_bnds_contiguity_fails_overlap(self):
        """Test that bounds with overlaps fail."""
        
        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        dataset.createDimension("bnds", 2)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))

        # Overlap between -30.0 and -40.0
        lat_bnds_var[:] = np.array([[-90.0, -30.0], [-40.0, 30.0], [30.0, 90.0]])

        # When
        from checks.variable_checks.check_bounds_contiguity import check_lat_bnds_contiguity
        results = check_lat_bnds_contiguity(dataset)

        # Then
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "overlap" in results[0].msgs[0].lower()

    def test_check_lat_bnds_contiguity_fails_wrong_shape(self):
        """Test that bounds with wrong shape fail."""
        
        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat",))
        lat_bnds_var[:] = np.array([-90.0, 0.0, 90.0])

        from checks.variable_checks.check_bounds_contiguity import check_lat_bnds_contiguity
        results = check_lat_bnds_contiguity(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "unexpected shape" in results[0].msgs[0]

    def test_check_lat_bnds_contiguity_fails_variable_not_found(self):
        """Test that missing lat_bnds variable fails."""
        
        dataset = MockNetCDF()
        # No lat_bnds variable created
        # When
        from checks.variable_checks.check_bounds_contiguity import check_lat_bnds_contiguity
        results = check_lat_bnds_contiguity(dataset)

        # Then
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "not found" in results[0].msgs[0]
