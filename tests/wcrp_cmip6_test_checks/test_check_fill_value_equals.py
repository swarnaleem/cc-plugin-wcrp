#!/usr/bin/env python
"""
Test for check_fill_value_equals.py
"""

import os
import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


class TestCheckFillValueEquals(BaseTestCase):
    """Tests for fill value equals checks."""

    # NOMINAL TEST CASES 

    def test_check_vertices_latitude_missing_value_pass(self):
        """Test that vertices_latitude with correct missing_value passes."""
         
        dataset = MockNetCDF()
        dataset.createDimension("cell", 3)
        dataset.createDimension("vertex", 4)
        vl_var = dataset.createVariable("vertices_latitude", "f", ("cell", "vertex"))
        vl_var[:] = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0]])
        vl_var.missing_value = 1.e+20

         
        from checks.variable_checks.check_fill_value_equals import check_vertices_latitude_missing_value
        results = check_vertices_latitude_missing_value(dataset)

         
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_latitude_fill_value_pass(self):
        """Test that vertices_latitude with correct _FillValue passes."""
         
        dataset = MockNetCDF()
        dataset.createDimension("cell", 3)
        dataset.createDimension("vertex", 4)
        vl_var = dataset.createVariable("vertices_latitude", "f", ("cell", "vertex"), fill_value=1.e+20)
        vl_var[:] = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0]])

         
        from checks.variable_checks.check_fill_value_equals import check_vertices_latitude_fill_value
        results = check_vertices_latitude_fill_value(dataset)

         
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_longitude_missing_value_pass(self):
        """Test that vertices_longitude with correct missing_value passes."""
         
        dataset = MockNetCDF()
        dataset.createDimension("cell", 3)
        dataset.createDimension("vertex", 4)
        vl_var = dataset.createVariable("vertices_longitude", "f", ("cell", "vertex"))
        vl_var[:] = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0]])
        vl_var.missing_value = 1.e+20

         
        from checks.variable_checks.check_fill_value_equals import check_vertices_longitude_missing_value
        results = check_vertices_longitude_missing_value(dataset)

         
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_longitude_fill_value_pass(self):
        """Test that vertices_longitude with correct _FillValue passes."""
         
        dataset = MockNetCDF()
        dataset.createDimension("cell", 3)
        dataset.createDimension("vertex", 4)
        vl_var = dataset.createVariable("vertices_longitude", "f", ("cell", "vertex"), fill_value=1.e+20)
        vl_var[:] = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0]])

         
        from checks.variable_checks.check_fill_value_equals import check_vertices_longitude_fill_value
        results = check_vertices_longitude_fill_value(dataset)

         
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_latitude_missing_value_pass_close(self):
        """Test that vertices_latitude with close missing_value passes (floating point tolerance)."""
         
        dataset = MockNetCDF()
        dataset.createDimension("cell", 1)
        dataset.createDimension("vertex", 4)
        vl_var = dataset.createVariable("vertices_latitude", "f", ("cell", "vertex"))
        vl_var[:] = np.array([[1.0, 2.0, 3.0, 4.0]])
        # Slightly off due to floating point, but within tolerance
        vl_var.missing_value = 1.00001e+20

         
        from checks.variable_checks.check_fill_value_equals import check_vertices_latitude_missing_value
        results = check_vertices_latitude_missing_value(dataset)

         
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    # ERROR TEST CASES

    def test_check_vertices_latitude_missing_value_fails_wrong_value(self):
        """Test that vertices_latitude with wrong missing_value fails."""
         
        dataset = MockNetCDF()
        dataset.createDimension("cell", 3)
        dataset.createDimension("vertex", 4)
        vl_var = dataset.createVariable("vertices_latitude", "f", ("cell", "vertex"))
        vl_var[:] = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0]])
        vl_var.missing_value = -999.0  # Wrong value

         
        from checks.variable_checks.check_fill_value_equals import check_vertices_latitude_missing_value
        results = check_vertices_latitude_missing_value(dataset)

         
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "Expected" in results[0].msgs[0]

    def test_check_vertices_latitude_fill_value_fails_no_attr(self):
        """Test that vertices_latitude without _FillValue attribute fails."""
         
        dataset = MockNetCDF()
        dataset.createDimension("cell", 3)
        dataset.createDimension("vertex", 4)
        vl_var = dataset.createVariable("vertices_latitude", "f", ("cell", "vertex"))
        vl_var[:] = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0]])
        # No _FillValue attribute

         
        from checks.variable_checks.check_fill_value_equals import check_vertices_latitude_fill_value
        results = check_vertices_latitude_fill_value(dataset)

         
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "not found" in results[0].msgs[0]

    def test_check_vertices_latitude_missing_value_fails_variable_not_found(self):
        """Test that missing vertices_latitude variable fails."""
         
        dataset = MockNetCDF()
        # No vertices_latitude variable created

         
        from checks.variable_checks.check_fill_value_equals import check_vertices_latitude_missing_value
        results = check_vertices_latitude_missing_value(dataset)

         
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "not found" in results[0].msgs[0]

    def test_check_vertices_longitude_fill_value_fails_wrong_value(self):
        """Test that vertices_longitude with wrong _FillValue fails."""
         
        dataset = MockNetCDF()
        dataset.createDimension("cell", 3)
        dataset.createDimension("vertex", 4)
        vl_var = dataset.createVariable("vertices_longitude", "f", ("cell", "vertex"), fill_value=0.0)  # Wrong value
        vl_var[:] = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0]])

         
        from checks.variable_checks.check_fill_value_equals import check_vertices_longitude_fill_value
        results = check_vertices_longitude_fill_value(dataset)

         
        assert len(results) == 1
        self.assert_result_is_bad(results[0])
        assert "Expected" in results[0].msgs[0]
