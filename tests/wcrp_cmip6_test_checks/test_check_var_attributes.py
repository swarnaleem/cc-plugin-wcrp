#!/usr/bin/env python
"""
Tests for check_var_attributes.py - Variable attribute checks

Tests cover the four main attribute check patterns:
1. Attribute existence (_check_attr_exists)
2. Attribute type (_check_attr_type)
3. Attribute UTF-8 encoding (_check_attr_utf8)
4. Attribute value (_check_attr_value)
"""

import numpy as np
from compliance_checker.tests import BaseTestCase
from tests.helpers import MockNetCDF


class TestCheckVarAttributesHeight(BaseTestCase):
    """Tests for height variable attribute checks."""

    # HEIGHT AXIS ATTRIBUTE TESTS

    def test_check_height_axis_exists_pass(self):
        """Test that height.axis existence check passes when attribute exists."""
        dataset = MockNetCDF()
        dataset.createDimension("height", 1)
        height_var = dataset.createVariable("height", "f", ("height",))
        height_var.axis = "Z"

        from checks.variable_checks.check_var_attributes import check_height_axis_exists
        results = check_height_axis_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_height_axis_exists_fail(self):
        """Test that height.axis existence check fails when attribute missing."""
        dataset = MockNetCDF()
        dataset.createDimension("height", 1)
        dataset.createVariable("height", "f", ("height",))
        # No axis attribute

        from checks.variable_checks.check_var_attributes import check_height_axis_exists
        results = check_height_axis_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    def test_check_height_axis_type_pass(self):
        """Test that height.axis type check passes when attribute is string."""
        dataset = MockNetCDF()
        dataset.createDimension("height", 1)
        height_var = dataset.createVariable("height", "f", ("height",))
        height_var.axis = "Z"

        from checks.variable_checks.check_var_attributes import check_height_axis_type
        results = check_height_axis_type(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_height_axis_value_pass(self):
        """Test that height.axis value check passes when value is 'Z'."""
        dataset = MockNetCDF()
        dataset.createDimension("height", 1)
        height_var = dataset.createVariable("height", "f", ("height",))
        height_var.axis = "Z"

        from checks.variable_checks.check_var_attributes import check_height_axis_value
        results = check_height_axis_value(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_height_axis_value_fail(self):
        """Test that height.axis value check fails when value is not 'Z'."""
        dataset = MockNetCDF()
        dataset.createDimension("height", 1)
        height_var = dataset.createVariable("height", "f", ("height",))
        height_var.axis = "X"  # Wrong value

        from checks.variable_checks.check_var_attributes import check_height_axis_value
        results = check_height_axis_value(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    # HEIGHT LONG_NAME ATTRIBUTE TESTS

    def test_check_height_long_name_exists_pass(self):
        """Test that height.long_name existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("height", 1)
        height_var = dataset.createVariable("height", "f", ("height",))
        height_var.long_name = "height"

        from checks.variable_checks.check_var_attributes import check_height_long_name_exists
        results = check_height_long_name_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_height_long_name_exists_fail(self):
        """Test that height.long_name existence check fails when missing."""
        dataset = MockNetCDF()
        dataset.createDimension("height", 1)
        dataset.createVariable("height", "f", ("height",))

        from checks.variable_checks.check_var_attributes import check_height_long_name_exists
        results = check_height_long_name_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])


class TestCheckVarAttributesLat(BaseTestCase):
    """Tests for lat variable attribute checks."""

    def test_check_lat_axis_value_pass(self):
        """Test that lat.axis value check passes when value is 'Y'."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var.axis = "Y"

        from checks.variable_checks.check_var_attributes import check_lat_axis_value
        results = check_lat_axis_value(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_axis_value_fail(self):
        """Test that lat.axis value check fails when value is not 'Y'."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var.axis = "X"  # Wrong value

        from checks.variable_checks.check_var_attributes import check_lat_axis_value
        results = check_lat_axis_value(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    def test_check_lat_long_name_exists_pass(self):
        """Test that lat.long_name existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var.long_name = "latitude"

        from checks.variable_checks.check_var_attributes import check_lat_long_name_exists
        results = check_lat_long_name_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_long_name_value_pass(self):
        """Test that lat.long_name value check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var.long_name = "latitude"

        from checks.variable_checks.check_var_attributes import check_lat_long_name_value
        results = check_lat_long_name_value(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_bounds_exists_pass(self):
        """Test that lat.bounds existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        lat_var = dataset.createVariable("lat", "f", ("lat",))
        lat_var.bounds = "lat_bnds"

        from checks.variable_checks.check_var_attributes import check_lat_bounds_exists
        results = check_lat_bounds_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lat_bounds_exists_fail(self):
        """Test that lat.bounds existence check fails when missing."""
        dataset = MockNetCDF()
        dataset.createDimension("lat", 5)
        dataset.createVariable("lat", "f", ("lat",))

        from checks.variable_checks.check_var_attributes import check_lat_bounds_exists
        results = check_lat_bounds_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])


class TestCheckVarAttributesLon(BaseTestCase):
    """Tests for lon variable attribute checks."""

    def test_check_lon_axis_value_pass(self):
        """Test that lon.axis value check passes when value is 'X'."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        lon_var = dataset.createVariable("lon", "f", ("lon",))
        lon_var.axis = "X"

        from checks.variable_checks.check_var_attributes import check_lon_axis_value
        results = check_lon_axis_value(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lon_axis_value_fail(self):
        """Test that lon.axis value check fails when value is not 'X'."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        lon_var = dataset.createVariable("lon", "f", ("lon",))
        lon_var.axis = "Y"  # Wrong value

        from checks.variable_checks.check_var_attributes import check_lon_axis_value
        results = check_lon_axis_value(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    def test_check_lon_long_name_value_pass(self):
        """Test that lon.long_name value check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        lon_var = dataset.createVariable("lon", "f", ("lon",))
        lon_var.long_name = "longitude"

        from checks.variable_checks.check_var_attributes import check_lon_long_name_value
        results = check_lon_long_name_value(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_lon_bounds_exists_pass(self):
        """Test that lon.bounds existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("lon", 5)
        lon_var = dataset.createVariable("lon", "f", ("lon",))
        lon_var.bounds = "lon_bnds"

        from checks.variable_checks.check_var_attributes import check_lon_bounds_exists
        results = check_lon_bounds_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])


class TestCheckVarAttributesI(BaseTestCase):
    """Tests for i variable attribute checks."""

    def test_check_i_units_exists_pass(self):
        """Test that i.units existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        i_var = dataset.createVariable("i", "i", ("i",))
        i_var.units = "1"

        from checks.variable_checks.check_var_attributes import check_i_units_exists
        results = check_i_units_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_i_units_exists_fail(self):
        """Test that i.units existence check fails when missing."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        dataset.createVariable("i", "i", ("i",))

        from checks.variable_checks.check_var_attributes import check_i_units_exists
        results = check_i_units_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])

    def test_check_i_units_value_pass(self):
        """Test that i.units value check passes when value is '1'."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        i_var = dataset.createVariable("i", "i", ("i",))
        i_var.units = "1"

        from checks.variable_checks.check_var_attributes import check_i_units_value
        results = check_i_units_value(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_i_long_name_exists_pass(self):
        """Test that i.long_name existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 10)
        i_var = dataset.createVariable("i", "i", ("i",))
        i_var.long_name = "cell index along first dimension"

        from checks.variable_checks.check_var_attributes import check_i_long_name_exists
        results = check_i_long_name_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])


class TestCheckVarAttributesJ(BaseTestCase):
    """Tests for j variable attribute checks."""

    def test_check_j_units_exists_pass(self):
        """Test that j.units existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("j", 10)
        j_var = dataset.createVariable("j", "i", ("j",))
        j_var.units = "1"

        from checks.variable_checks.check_var_attributes import check_j_units_exists
        results = check_j_units_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_j_long_name_exists_pass(self):
        """Test that j.long_name existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("j", 10)
        j_var = dataset.createVariable("j", "i", ("j",))
        j_var.long_name = "cell index along second dimension"

        from checks.variable_checks.check_var_attributes import check_j_long_name_exists
        results = check_j_long_name_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])


class TestCheckVarAttributesVerticesLatitude(BaseTestCase):
    """Tests for vertices_latitude variable attribute checks."""

    def test_check_vertices_latitude_units_exists_pass(self):
        """Test that vertices_latitude.units existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        dataset.createDimension("j", 5)
        dataset.createDimension("vertices", 4)
        vert_lat_var = dataset.createVariable("vertices_latitude", "f", ("j", "i", "vertices"))
        vert_lat_var.units = "degrees_north"

        from checks.variable_checks.check_var_attributes import check_vertices_latitude_units_exists
        results = check_vertices_latitude_units_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_latitude_units_value_pass(self):
        """Test that vertices_latitude.units value check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        dataset.createDimension("j", 5)
        dataset.createDimension("vertices", 4)
        vert_lat_var = dataset.createVariable("vertices_latitude", "f", ("j", "i", "vertices"))
        vert_lat_var.units = "degrees_north"

        from checks.variable_checks.check_var_attributes import check_vertices_latitude_units_value
        results = check_vertices_latitude_units_value(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_latitude_missing_value_exists_pass(self):
        """Test that vertices_latitude.missing_value existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        dataset.createDimension("j", 5)
        dataset.createDimension("vertices", 4)
        vert_lat_var = dataset.createVariable("vertices_latitude", "f", ("j", "i", "vertices"))
        vert_lat_var.missing_value = 1.0e20

        from checks.variable_checks.check_var_attributes import check_vertices_latitude_missing_value_exists
        results = check_vertices_latitude_missing_value_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_latitude_fillvalue_exists_pass(self):
        """Test that vertices_latitude._FillValue existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        dataset.createDimension("j", 5)
        dataset.createDimension("vertices", 4)
        vert_lat_var = dataset.createVariable("vertices_latitude", "f", ("j", "i", "vertices"),
                                               fill_value=1.0e20)

        from checks.variable_checks.check_var_attributes import check_vertices_latitude_fillvalue_exists
        results = check_vertices_latitude_fillvalue_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])


class TestCheckVarAttributesVerticesLongitude(BaseTestCase):
    """Tests for vertices_longitude variable attribute checks."""

    def test_check_vertices_longitude_units_exists_pass(self):
        """Test that vertices_longitude.units existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        dataset.createDimension("j", 5)
        dataset.createDimension("vertices", 4)
        vert_lon_var = dataset.createVariable("vertices_longitude", "f", ("j", "i", "vertices"))
        vert_lon_var.units = "degrees_east"

        from checks.variable_checks.check_var_attributes import check_vertices_longitude_units_exists
        results = check_vertices_longitude_units_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_longitude_units_value_pass(self):
        """Test that vertices_longitude.units value check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        dataset.createDimension("j", 5)
        dataset.createDimension("vertices", 4)
        vert_lon_var = dataset.createVariable("vertices_longitude", "f", ("j", "i", "vertices"))
        vert_lon_var.units = "degrees_east"

        from checks.variable_checks.check_var_attributes import check_vertices_longitude_units_value
        results = check_vertices_longitude_units_value(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_check_vertices_longitude_missing_value_exists_pass(self):
        """Test that vertices_longitude.missing_value existence check passes."""
        dataset = MockNetCDF()
        dataset.createDimension("i", 5)
        dataset.createDimension("j", 5)
        dataset.createDimension("vertices", 4)
        vert_lon_var = dataset.createVariable("vertices_longitude", "f", ("j", "i", "vertices"))
        vert_lon_var.missing_value = 1.0e20

        from checks.variable_checks.check_var_attributes import check_vertices_longitude_missing_value_exists
        results = check_vertices_longitude_missing_value_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_good(results[0])


class TestCheckVarAttributesMissingVariable(BaseTestCase):
    """Tests for attribute checks when variable is missing."""

    def test_check_attribute_missing_variable(self):
        """Test that attribute check fails gracefully when variable is missing."""
        dataset = MockNetCDF()
        # No height variable

        from checks.variable_checks.check_var_attributes import check_height_axis_exists
        results = check_height_axis_exists(dataset)

        assert len(results) == 1
        self.assert_result_is_bad(results[0])
