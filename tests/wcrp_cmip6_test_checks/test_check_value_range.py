#!/usr/bin/env python
"""
Test for check_value_range.py
"""

import os
import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


# Path to IPSL test file
IPSL_FILE_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "data", "CMIP6", "CMIP", "IPSL", "IPSL-CM5A2-INCA",
    "historical", "r1i1p1f1", "Amon", "pr", "gr", "v20240619",
    "pr_Amon_IPSL-CM5A2-INCA_historical_r1i1p1f1_gr_185001-201412.nc"
))


class TestCheckValueRange(BaseTestCase):
    """Tests for value range checks."""

    # NOMINAL TEST CASES 

    def test_check_lat_value_range_pass(self):
        """Test that lat values within -90 to 90 pass using IPSL file."""
         
        dataset = Dataset(IPSL_FILE_PATH, mode="r")

         
        from checks.variable_checks.check_value_range import check_lat_value_range
        results = check_lat_value_range(dataset)

         
        assert len(results) == 1
        self.assert_result_is_good(results[0])
        dataset.close()

    def test_check_lon_value_range_pass(self):
        """Test that lon values within 0 to 360 pass using IPSL file."""
         
        dataset = Dataset(IPSL_FILE_PATH, mode="r")

         
        from checks.variable_checks.check_value_range import check_lon_value_range
        results = check_lon_value_range(dataset)

         
        assert len(results) == 1
        self.assert_result_is_good(results[0])
        dataset.close()

    # NOMINAL TEST CASES - Using MockNetCDF for bounds

    def test_check_lat_bnds_value_range_pass(self):
        """Test that lat_bnds values within -90 to 90 pass."""
         
        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        dataset.createDimension("bnds", 2)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))
        lat_bnds_var[:] = np.array([[-90.0, -30.0], [-30.0, 30.0], [30.0, 90.0]])

         
        from checks.variable_checks.check_value_range import check_lat_bnds_value_range
        results = check_lat_bnds_value_range(dataset)

         
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lon_bnds_value_range_pass(self):
        """Test that lon_bnds values within 0 to 360 pass."""
         
        dataset = MockNetCDF()
        dataset.createDimension("lon", 3)
        dataset.createDimension("bnds", 2)
        lon_bnds_var = dataset.createVariable("lon_bnds", "f", ("lon", "bnds"))
        lon_bnds_var[:] = np.array([[0.0, 120.0], [120.0, 240.0], [240.0, 360.0]])

         
        from checks.variable_checks.check_value_range import check_lon_bnds_value_range
        results = check_lon_bnds_value_range(dataset)

         
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    # ERROR TEST CASES

    def test_check_lat_value_range_fails_below_min(self):
        """Test that lat values below -90 fail."""
         
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var[:] = np.array([-95.0, -45.0, 0.0, 45.0, 90.0])  # -95 is invalid

         
        from checks.variable_checks.check_value_range import check_lat_value_range
        results = check_lat_value_range(dataset)

         
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "outside range" in results[0].msgs[0]

    def test_check_lat_value_range_fails_above_max(self):
        """Test that lat values above 90 fail."""
         
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var[:] = np.array([-90.0, -45.0, 0.0, 45.0, 95.0])  # 95 is invalid

         
        from checks.variable_checks.check_value_range import check_lat_value_range
        results = check_lat_value_range(dataset)

         
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "outside range" in results[0].msgs[0]

    def test_check_lon_value_range_fails_below_min(self):
        """Test that lon values below 0 fail."""
         
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        lon_var = dataset.createVariable("lon", "f", ("lon",))
        lon_var[:] = np.array([-10.0, 90.0, 180.0, 270.0, 360.0])  # -10 is invalid

         
        from checks.variable_checks.check_value_range import check_lon_value_range
        results = check_lon_value_range(dataset)

         
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "outside range" in results[0].msgs[0]

    def test_check_lon_value_range_fails_above_max(self):
        """Test that lon values above 360 fail."""
         
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        lon_var = dataset.createVariable("lon", "f", ("lon",))
        lon_var[:] = np.array([0.0, 90.0, 180.0, 270.0, 370.0])  # 370 is invalid

         
        from checks.variable_checks.check_value_range import check_lon_value_range
        results = check_lon_value_range(dataset)

         
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "outside range" in results[0].msgs[0]

    def test_check_lat_value_range_fails_variable_not_found(self):
        """Test that missing lat variable fails."""
         
        dataset = MockNetCDF()
        # No lat variable created

         
        from checks.variable_checks.check_value_range import check_lat_value_range
        results = check_lat_value_range(dataset)

         
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "not found" in results[0].msgs[0]
