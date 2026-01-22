#!/usr/bin/env python
"""
Tests for check_no_nan_inf.py - NaN/Inf value checks

Note: These tests focus on the wrapper functions correctly calling the underlying
check_nan_inf function. Testing the pass cases is sufficient to verify the wiring.
"""

import numpy as np
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


class TestCheckNoNanInf(BaseTestCase):
    """Tests for NaN/Inf value checks."""

    # LAT NO NAN/INF TESTS

    def test_check_lat_no_nan_inf_pass(self):
        """Test that lat no NaN/Inf check passes with valid data."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var[:] = np.array([-90.0, -45.0, 0.0, 45.0, 90.0])

        from checks.variable_checks.check_no_nan_inf import check_lat_no_nan_inf
        results = check_lat_no_nan_inf(dataset)

        assert len(results) == 2  # One for NaN, one for Inf
        for result in results:
            self.assert_result_is_good(result)

    def test_check_lat_no_nan_inf_missing_variable(self):
        """Test that lat no NaN/Inf check returns empty when lat missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_no_nan_inf import check_lat_no_nan_inf
        results = check_lat_no_nan_inf(dataset)

        assert len(results) == 0

    # LON NO NAN/INF TESTS

    def test_check_lon_no_nan_inf_pass(self):
        """Test that lon no NaN/Inf check passes with valid data."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        lon_var = dataset.createVariable("lon", "f", ("lon",))
        lon_var[:] = np.array([0.0, 90.0, 180.0, 270.0, 360.0])

        from checks.variable_checks.check_no_nan_inf import check_lon_no_nan_inf
        results = check_lon_no_nan_inf(dataset)

        assert len(results) == 2
        for result in results:
            self.assert_result_is_good(result)

    # LAT_BNDS NO NAN/INF TESTS

    def test_check_lat_bnds_no_nan_inf_pass(self):
        """Test that lat_bnds no NaN/Inf check passes with valid data."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        dataset.createDimension("bnds", 2)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))
        lat_bnds_var[:] = np.array([[-90.0, -30.0], [-30.0, 30.0], [30.0, 90.0]])

        from checks.variable_checks.check_no_nan_inf import check_lat_bnds_no_nan_inf
        results = check_lat_bnds_no_nan_inf(dataset)

        assert len(results) == 2
        for result in results:
            self.assert_result_is_good(result)

    # LON_BNDS NO NAN/INF TESTS

    def test_check_lon_bnds_no_nan_inf_pass(self):
        """Test that lon_bnds no NaN/Inf check passes with valid data."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 3)
        dataset.createDimension("bnds", 2)
        lon_bnds_var = dataset.createVariable("lon_bnds", "f", ("lon", "bnds"))
        lon_bnds_var[:] = np.array([[0.0, 120.0], [120.0, 240.0], [240.0, 360.0]])

        from checks.variable_checks.check_no_nan_inf import check_lon_bnds_no_nan_inf
        results = check_lon_bnds_no_nan_inf(dataset)

        assert len(results) == 2
        for result in results:
            self.assert_result_is_good(result)

    # I NO NAN/INF TESTS

    def test_check_i_no_nan_inf_pass(self):
        """Test that i no NaN/Inf check passes with valid data."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        i_var = dataset.createVariable("i", "i", ("i",))
        i_var[:] = np.arange(1, 11)

        from checks.variable_checks.check_no_nan_inf import check_i_no_nan_inf
        results = check_i_no_nan_inf(dataset)

        assert len(results) == 2
        for result in results:
            self.assert_result_is_good(result)

    # J NO NAN/INF TESTS

    def test_check_j_no_nan_inf_pass(self):
        """Test that j no NaN/Inf check passes with valid data."""
        dataset = MockNetCDF()
        dataset.createDimension("j", 10)
        j_var = dataset.createVariable("j", "i", ("j",))
        j_var[:] = np.arange(1, 11)

        from checks.variable_checks.check_no_nan_inf import check_j_no_nan_inf
        results = check_j_no_nan_inf(dataset)

        assert len(results) == 2
        for result in results:
            self.assert_result_is_good(result)

    # VERTICES_LATITUDE NO NAN/INF TESTS

    def test_check_vertices_latitude_no_nan_inf_pass(self):
        """Test that vertices_latitude no NaN/Inf check passes with valid data."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        dataset.createDimension("j", 5)
        dataset.createDimension("vertices", 4)
        vert_lat_var = dataset.createVariable("vertices_latitude", "f", ("j", "i", "vertices"))
        vert_lat_var[:] = np.ones((5, 5, 4)) * 45.0

        from checks.variable_checks.check_no_nan_inf import check_vertices_latitude_no_nan_inf
        results = check_vertices_latitude_no_nan_inf(dataset)

        assert len(results) == 2
        for result in results:
            self.assert_result_is_good(result)

    # VERTICES_LONGITUDE NO NAN/INF TESTS

    def test_check_vertices_longitude_no_nan_inf_pass(self):
        """Test that vertices_longitude no NaN/Inf check passes with valid data."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        dataset.createDimension("j", 5)
        dataset.createDimension("vertices", 4)
        vert_lon_var = dataset.createVariable("vertices_longitude", "f", ("j", "i", "vertices"))
        vert_lon_var[:] = np.ones((5, 5, 4)) * 180.0

        from checks.variable_checks.check_no_nan_inf import check_vertices_longitude_no_nan_inf
        results = check_vertices_longitude_no_nan_inf(dataset)

        assert len(results) == 2
        for result in results:
            self.assert_result_is_good(result)
