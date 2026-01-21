#!/usr/bin/env python
"""
Test for check_data_within_actual_range.py
"""

import os
import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


class TestCheckDataWithinActualRange(BaseTestCase):
    """Tests for data within actual_range checks."""

    # NOMINAL TEST CASES 

    def test_check_lat_data_within_actual_range_pass(self):
        """Test that lat data within actual_range passes."""
           
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var[:] = np.array([-45.0, -30.0, 0.0, 30.0, 45.0])
        lat_var.actual_range = np.array([-90.0, 90.0])

         
        from checks.variable_checks.check_data_within_actual_range import check_lat_data_within_actual_range
        results = check_lat_data_within_actual_range(dataset)

          
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lon_data_within_actual_range_pass(self):
        """Test that lon data within actual_range passes."""

        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        lon_var = dataset.createVariable("lon", "f", ("lon",))
        lon_var[:] = np.array([0.0, 90.0, 180.0, 270.0, 360.0])
        lon_var.actual_range = np.array([0.0, 360.0])

         
        from checks.variable_checks.check_data_within_actual_range import check_lon_data_within_actual_range
        results = check_lon_data_within_actual_range(dataset)

          
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_data_within_actual_range_skips_no_attr(self):
        """Test that check is skipped if no actual_range attribute."""
           
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var[:] = np.array([-45.0, -30.0, 0.0, 30.0, 45.0])
        # No actual_range attribute

         
        from checks.variable_checks.check_data_within_actual_range import check_lat_data_within_actual_range
        results = check_lat_data_within_actual_range(dataset)

          
        assert len(results) == 0  # skipped

    def test_check_lat_data_within_actual_range_pass_at_boundaries(self):
        """Test that lat data exactly at actual_range boundaries passes."""
           
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var[:] = np.array([-90.0, -45.0, 0.0, 45.0, 90.0])
        lat_var.actual_range = np.array([-90.0, 90.0])

         
        from checks.variable_checks.check_data_within_actual_range import check_lat_data_within_actual_range
        results = check_lat_data_within_actual_range(dataset)

          
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    # ERROR TEST CASES

    def test_check_lat_data_within_actual_range_fails_below_min(self):
        """Test that lat data below actual_range min fails."""
           
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var[:] = np.array([-95.0, -45.0, 0.0, 45.0, 90.0])  # -95 < -90
        lat_var.actual_range = np.array([-90.0, 90.0])

         
        from checks.variable_checks.check_data_within_actual_range import check_lat_data_within_actual_range
        results = check_lat_data_within_actual_range(dataset)

          
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "outside" in results[0].msgs[0]

    def test_check_lat_data_within_actual_range_fails_above_max(self):
        """Test that lat data above actual_range max fails."""
           
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var[:] = np.array([-90.0, -45.0, 0.0, 45.0, 95.0])  # 95 > 90
        lat_var.actual_range = np.array([-90.0, 90.0])

         
        from checks.variable_checks.check_data_within_actual_range import check_lat_data_within_actual_range
        results = check_lat_data_within_actual_range(dataset)

          
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "outside" in results[0].msgs[0]

    def test_check_lat_data_within_actual_range_fails_invalid_actual_range(self):
        """Test that invalid actual_range with wrong length fails."""
           
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var[:] = np.array([-45.0, -30.0, 0.0, 30.0, 45.0])
        lat_var.actual_range = np.array([-90.0, 0.0, 90.0])  # 3 elements instead of 2

         
        from checks.variable_checks.check_data_within_actual_range import check_lat_data_within_actual_range
        results = check_lat_data_within_actual_range(dataset)

          
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "expected 2" in results[0].msgs[0]

    def test_check_lat_data_within_actual_range_fails_variable_not_found(self):
        """Test that missing lat variable fails."""
           
        dataset = MockNetCDF()
        # No lat variable created

         
        from checks.variable_checks.check_data_within_actual_range import check_lat_data_within_actual_range
        results = check_lat_data_within_actual_range(dataset)

          
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "not found" in results[0].msgs[0]
