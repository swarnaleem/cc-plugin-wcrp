#!/usr/bin/env python
"""
Tests for check_var_existence.py - Variable existence checks
"""

import numpy as np
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


class TestCheckVarExistence(BaseTestCase):
    """Tests for variable existence checks."""

    # LAT EXISTENCE TESTS

    def test_check_lat_exists_pass(self):
        """Test that lat variable existence check passes when lat exists."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        dataset.createVariable("lat", "f", ("lat",))

        from checks.variable_checks.check_var_existence import check_lat_exists
        results = check_lat_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_exists_fail(self):
        """Test that lat variable existence check fails when lat is missing."""
        dataset = MockNetCDF()
        # No lat variable

        from checks.variable_checks.check_var_existence import check_lat_exists
        results = check_lat_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # LON EXISTENCE TESTS

    def test_check_lon_exists_pass(self):
        """Test that lon variable existence check passes when lon exists."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        dataset.createVariable("lon", "f", ("lon",))

        from checks.variable_checks.check_var_existence import check_lon_exists
        results = check_lon_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lon_exists_fail(self):
        """Test that lon variable existence check fails when lon is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_existence import check_lon_exists
        results = check_lon_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # HEIGHT EXISTENCE TESTS

    def test_check_height_exists_pass(self):
        """Test that height variable existence check passes when height exists."""
        dataset = MockNetCDF()
        dataset.createDimension("height", 1)
        dataset.createVariable("height", "d", ("height",))

        from checks.variable_checks.check_var_existence import check_height_exists
        results = check_height_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_height_exists_fail(self):
        """Test that height variable existence check fails when height is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_existence import check_height_exists
        results = check_height_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # LAT_BNDS EXISTENCE TESTS

    def test_check_lat_bnds_exists_pass(self):
        """Test that lat_bnds variable existence check passes when lat_bnds exists."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        dataset.createDimension("bnds", 2)
        dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))

        from checks.variable_checks.check_var_existence import check_lat_bnds_exists
        results = check_lat_bnds_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_bnds_exists_fail(self):
        """Test that lat_bnds variable existence check fails when lat_bnds is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_existence import check_lat_bnds_exists
        results = check_lat_bnds_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # LON_BNDS EXISTENCE TESTS

    def test_check_lon_bnds_exists_pass(self):
        """Test that lon_bnds variable existence check passes when lon_bnds exists."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        dataset.createDimension("bnds", 2)
        dataset.createVariable("lon_bnds", "f", ("lon", "bnds"))

        from checks.variable_checks.check_var_existence import check_lon_bnds_exists
        results = check_lon_bnds_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lon_bnds_exists_fail(self):
        """Test that lon_bnds variable existence check fails when lon_bnds is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_existence import check_lon_bnds_exists
        results = check_lon_bnds_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # I VARIABLE EXISTENCE TESTS

    def test_check_i_exists_pass(self):
        """Test that i variable existence check passes when i exists."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        dataset.createVariable("i", "i", ("i",))

        from checks.variable_checks.check_var_existence import check_i_exists
        results = check_i_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_i_exists_fail(self):
        """Test that i variable existence check fails when i is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_existence import check_i_exists
        results = check_i_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # J VARIABLE EXISTENCE TESTS

    def test_check_j_exists_pass(self):
        """Test that j variable existence check passes when j exists."""
        dataset = MockNetCDF()
        dataset.createDimension("j", 10)
        dataset.createVariable("j", "i", ("j",))

        from checks.variable_checks.check_var_existence import check_j_exists
        results = check_j_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_j_exists_fail(self):
        """Test that j variable existence check fails when j is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_existence import check_j_exists
        results = check_j_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # VERTICES_LATITUDE EXISTENCE TESTS

    def test_check_vertices_latitude_exists_pass(self):
        """Test that vertices_latitude existence check passes when it exists."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        dataset.createDimension("j", 10)
        dataset.createDimension("vertices", 4)
        dataset.createVariable("vertices_latitude", "f", ("j", "i", "vertices"))

        from checks.variable_checks.check_var_existence import check_vertices_latitude_exists
        results = check_vertices_latitude_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_latitude_exists_fail(self):
        """Test that vertices_latitude existence check fails when missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_existence import check_vertices_latitude_exists
        results = check_vertices_latitude_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # VERTICES_LONGITUDE EXISTENCE TESTS

    def test_check_vertices_longitude_exists_pass(self):
        """Test that vertices_longitude existence check passes when it exists."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        dataset.createDimension("j", 10)
        dataset.createDimension("vertices", 4)
        dataset.createVariable("vertices_longitude", "f", ("j", "i", "vertices"))

        from checks.variable_checks.check_var_existence import check_vertices_longitude_exists
        results = check_vertices_longitude_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_longitude_exists_fail(self):
        """Test that vertices_longitude existence check fails when missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_existence import check_vertices_longitude_exists
        results = check_vertices_longitude_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
