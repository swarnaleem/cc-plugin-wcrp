#!/usr/bin/env python
"""
Tests for check_var_shape.py - Variable shape checks
"""

import numpy as np
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


class TestCheckVarShape(BaseTestCase):
    """Tests for variable shape checks."""

    # LAT SHAPE TESTS

    def test_check_lat_shape_pass(self):
        """Test that lat shape check passes when shape aligns with dimension."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var[:] = np.array([-90.0, -45.0, 0.0, 45.0, 90.0])

        from checks.variable_checks.check_var_shape import check_lat_shape
        results = check_lat_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_shape_fail_missing(self):
        """Test that lat shape check fails when lat is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_shape import check_lat_shape
        results = check_lat_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # LON SHAPE TESTS

    def test_check_lon_shape_pass(self):
        """Test that lon shape check passes when shape aligns with dimension."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 6)
        lon_var = dataset.createVariable("lon", "f", ("lon",))
        lon_var[:] = np.array([0.0, 60.0, 120.0, 180.0, 240.0, 300.0])

        from checks.variable_checks.check_var_shape import check_lon_shape
        results = check_lon_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lon_shape_fail_missing(self):
        """Test that lon shape check fails when lon is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_shape import check_lon_shape
        results = check_lon_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # LAT_BNDS SHAPE TESTS

    def test_check_lat_bnds_shape_pass(self):
        """Test that lat_bnds shape check passes when shape aligns."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 3)
        dataset.createDimension("bnds", 2)
        lat_bnds_var = dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))
        lat_bnds_var[:] = np.array([[-90.0, -30.0], [-30.0, 30.0], [30.0, 90.0]])

        from checks.variable_checks.check_var_shape import check_lat_bnds_shape
        results = check_lat_bnds_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_bnds_shape_fail_missing(self):
        """Test that lat_bnds shape check fails when lat_bnds is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_shape import check_lat_bnds_shape
        results = check_lat_bnds_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # LON_BNDS SHAPE TESTS

    def test_check_lon_bnds_shape_pass(self):
        """Test that lon_bnds shape check passes when shape aligns."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 3)
        dataset.createDimension("bnds", 2)
        lon_bnds_var = dataset.createVariable("lon_bnds", "f", ("lon", "bnds"))
        lon_bnds_var[:] = np.array([[0.0, 120.0], [120.0, 240.0], [240.0, 360.0]])

        from checks.variable_checks.check_var_shape import check_lon_bnds_shape
        results = check_lon_bnds_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    # I SHAPE TESTS

    def test_check_i_shape_pass(self):
        """Test that i shape check passes when shape aligns with dimension."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        i_var = dataset.createVariable("i", "i", ("i",))
        i_var[:] = np.arange(1, 11)

        from checks.variable_checks.check_var_shape import check_i_shape
        results = check_i_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_i_shape_fail_missing(self):
        """Test that i shape check fails when i is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_shape import check_i_shape
        results = check_i_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # J SHAPE TESTS

    def test_check_j_shape_pass(self):
        """Test that j shape check passes when shape aligns with dimension."""
        dataset = MockNetCDF()
        dataset.createDimension("j", 10)
        j_var = dataset.createVariable("j", "i", ("j",))
        j_var[:] = np.arange(1, 11)

        from checks.variable_checks.check_var_shape import check_j_shape
        results = check_j_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_j_shape_fail_missing(self):
        """Test that j shape check fails when j is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_shape import check_j_shape
        results = check_j_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # VERTICES_LATITUDE SHAPE TESTS

    def test_check_vertices_latitude_shape_pass(self):
        """Test that vertices_latitude shape check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        dataset.createDimension("j", 5)
        dataset.createDimension("vertices", 4)
        vert_lat_var = dataset.createVariable("vertices_latitude", "f", ("j", "i", "vertices"))
        vert_lat_var[:] = np.zeros((5, 5, 4))

        from checks.variable_checks.check_var_shape import check_vertices_latitude_shape
        results = check_vertices_latitude_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_latitude_shape_fail_missing(self):
        """Test that vertices_latitude shape check fails when missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_shape import check_vertices_latitude_shape
        results = check_vertices_latitude_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # VERTICES_LONGITUDE SHAPE TESTS

    def test_check_vertices_longitude_shape_pass(self):
        """Test that vertices_longitude shape check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        dataset.createDimension("j", 5)
        dataset.createDimension("vertices", 4)
        vert_lon_var = dataset.createVariable("vertices_longitude", "f", ("j", "i", "vertices"))
        vert_lon_var[:] = np.zeros((5, 5, 4))

        from checks.variable_checks.check_var_shape import check_vertices_longitude_shape
        results = check_vertices_longitude_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_longitude_shape_fail_missing(self):
        """Test that vertices_longitude shape check fails when missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_shape import check_vertices_longitude_shape
        results = check_vertices_longitude_shape(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
