#!/usr/bin/env python
"""
Tests for check_var_type.py - Variable type checks
"""

import numpy as np
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


class TestCheckVarType(BaseTestCase):
    """Tests for variable type checks."""

    # LAT TYPE TESTS

    def test_check_lat_type_pass(self):
        """Test that lat type check passes when lat is NC_FLOAT."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        dataset.createVariable("lat", "f", ("lat",))  # 'f' = float32

        from checks.variable_checks.check_var_type import check_lat_type
        results = check_lat_type(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_type_fail_wrong_type(self):
        """Test that lat type check fails when lat is integer (not floating point)."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        dataset.createVariable("lat", "i", ("lat",))  # 'i' = int32, not float

        from checks.variable_checks.check_var_type import check_lat_type
        results = check_lat_type(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    def test_check_lat_type_fail_missing(self):
        """Test that lat type check fails when lat is missing."""
        dataset = MockNetCDF()

        from checks.variable_checks.check_var_type import check_lat_type
        results = check_lat_type(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # LON TYPE TESTS

    def test_check_lon_type_pass(self):
        """Test that lon type check passes when lon is NC_FLOAT."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        dataset.createVariable("lon", "f", ("lon",))

        from checks.variable_checks.check_var_type import check_lon_type
        results = check_lon_type(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lon_type_fail_wrong_type(self):
        """Test that lon type check fails when lon is not NC_FLOAT."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        dataset.createVariable("lon", "i", ("lon",))  # 'i' = int32

        from checks.variable_checks.check_var_type import check_lon_type
        results = check_lon_type(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # HEIGHT TYPE TESTS

    def test_check_height_type_pass(self):
        """Test that height type check passes when height is NC_FLOAT."""
        dataset = MockNetCDF()
        dataset.createDimension("height", 1)
        dataset.createVariable("height", "f", ("height",))

        from checks.variable_checks.check_var_type import check_height_type
        results = check_height_type(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_height_type_fail_wrong_type(self):
        """Test that height type check fails when height is not NC_FLOAT."""
        dataset = MockNetCDF()
        dataset.createDimension("height", 1)
        dataset.createVariable("height", "i", ("height",))

        from checks.variable_checks.check_var_type import check_height_type
        results = check_height_type(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # LAT_BNDS TYPE TESTS

    def test_check_lat_bnds_type_pass(self):
        """Test that lat_bnds type check passes when lat_bnds is NC_FLOAT."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        dataset.createDimension("bnds", 2)
        dataset.createVariable("lat_bnds", "f", ("lat", "bnds"))

        from checks.variable_checks.check_var_type import check_lat_bnds_type
        results = check_lat_bnds_type(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_bnds_type_fail_wrong_type(self):
        """Test that lat_bnds type check fails when lat_bnds is integer."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        dataset.createDimension("bnds", 2)
        dataset.createVariable("lat_bnds", "i", ("lat", "bnds"))  # int instead of float

        from checks.variable_checks.check_var_type import check_lat_bnds_type
        results = check_lat_bnds_type(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # LON_BNDS TYPE TESTS

    def test_check_lon_bnds_type_pass(self):
        """Test that lon_bnds type check passes when lon_bnds is NC_FLOAT."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        dataset.createDimension("bnds", 2)
        dataset.createVariable("lon_bnds", "f", ("lon", "bnds"))

        from checks.variable_checks.check_var_type import check_lon_bnds_type
        results = check_lon_bnds_type(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    # I TYPE TESTS

    def test_check_i_type_pass(self):
        """Test that i type check passes when i is NC_INT."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        dataset.createVariable("i", "i", ("i",))  # 'i' = int32

        from checks.variable_checks.check_var_type import check_i_type
        results = check_i_type(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_i_type_fail_wrong_type(self):
        """Test that i type check fails when i is not NC_INT."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        dataset.createVariable("i", "f", ("i",))  # float instead of int

        from checks.variable_checks.check_var_type import check_i_type
        results = check_i_type(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # J TYPE TESTS

    def test_check_j_type_pass(self):
        """Test that j type check passes when j is NC_INT."""
        dataset = MockNetCDF()
        dataset.createDimension("j", 10)
        dataset.createVariable("j", "i", ("j",))

        from checks.variable_checks.check_var_type import check_j_type
        results = check_j_type(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_j_type_fail_wrong_type(self):
        """Test that j type check fails when j is not NC_INT."""
        dataset = MockNetCDF()
        dataset.createDimension("j", 10)
        dataset.createVariable("j", "f", ("j",))

        from checks.variable_checks.check_var_type import check_j_type
        results = check_j_type(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # VERTICES_LATITUDE TYPE TESTS

    def test_check_vertices_latitude_type_pass(self):
        """Test that vertices_latitude type check passes when NC_FLOAT."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        dataset.createDimension("j", 10)
        dataset.createDimension("vertices", 4)
        dataset.createVariable("vertices_latitude", "f", ("j", "i", "vertices"))

        from checks.variable_checks.check_var_type import check_vertices_latitude_type
        results = check_vertices_latitude_type(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_latitude_type_fail(self):
        """Test that vertices_latitude type check fails when not NC_FLOAT."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        dataset.createDimension("j", 10)
        dataset.createDimension("vertices", 4)
        dataset.createVariable("vertices_latitude", "i", ("j", "i", "vertices"))

        from checks.variable_checks.check_var_type import check_vertices_latitude_type
        results = check_vertices_latitude_type(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # VERTICES_LONGITUDE TYPE TESTS

    def test_check_vertices_longitude_type_pass(self):
        """Test that vertices_longitude type check passes when NC_FLOAT."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        dataset.createDimension("j", 10)
        dataset.createDimension("vertices", 4)
        dataset.createVariable("vertices_longitude", "f", ("j", "i", "vertices"))

        from checks.variable_checks.check_var_type import check_vertices_longitude_type
        results = check_vertices_longitude_type(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_longitude_type_fail(self):
        """Test that vertices_longitude type check fails when integer."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        dataset.createDimension("j", 10)
        dataset.createDimension("vertices", 4)
        dataset.createVariable("vertices_longitude", "i", ("j", "i", "vertices"))  # int instead of float

        from checks.variable_checks.check_var_type import check_vertices_longitude_type
        results = check_vertices_longitude_type(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
