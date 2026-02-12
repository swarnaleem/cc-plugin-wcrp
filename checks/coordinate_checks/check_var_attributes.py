#!/usr/bin/env python
"""
This module provides atomic checks for variable attribute validation.
Reuses check_attribute_suite from attribute_checks with specific check IDs.

Note: check_attribute_suite returns results with ATTR001-ATTR004 codes.
For specific V* check IDs, we use focused helper functions.
"""

from compliance_checker.base import BaseCheck, TestCtx
import numpy as np


def _check_attr_exists(ds, var_name, attr_name, check_id, severity):
    """
    Internal helper to verify an attribute exists on a variable.

    Parameters
    ----------
    ds : netCDF4.Dataset
        An open netCDF dataset.
    var_name : str
        The name of the variable (e.g., 'lat', 'height').
    attr_name : str
        The name of the attribute to check (e.g., 'units', 'axis').
    check_id : str
        The unique check identifier (e.g., 'V004').
    severity : int
        The severity level (BaseCheck.HIGH, BaseCheck.MEDIUM, BaseCheck.LOW).

    Returns
    -------
    list[Result]
        A list containing one Result object with pass/fail status.
    """
    ctx = TestCtx(severity, f"[{check_id}] Attribute Existence: '{var_name}.{attr_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    var = ds.variables[var_name]
    if hasattr(var, attr_name) or attr_name in var.ncattrs():
        ctx.add_pass()
    else:
        ctx.add_failure(f"Attribute '{attr_name}' not found on variable '{var_name}'.")

    return [ctx.to_result()]


def _check_attr_type(ds, var_name, attr_name, expected_type, check_id, severity):
    """
    Internal helper to verify an attribute has the expected data type.

    Parameters
    ----------
    ds : netCDF4.Dataset
        An open netCDF dataset.
    var_name : str
        The name of the variable (e.g., 'lat', 'height').
    attr_name : str
        The name of the attribute to check (e.g., 'units', 'axis').
    expected_type : str
        Expected type: 'str', 'float', or 'int'.
    check_id : str
        The unique check identifier (e.g., 'V005').
    severity : int
        The severity level (BaseCheck.HIGH, BaseCheck.MEDIUM, BaseCheck.LOW).

    Returns
    -------
    list[Result]
        A list containing one Result object with pass/fail status.
    """
    ctx = TestCtx(severity, f"[{check_id}] Attribute Type: '{var_name}.{attr_name}'")

    if var_name not in ds.variables:
        return []

    var = ds.variables[var_name]
    try:
        attr_val = getattr(var, attr_name, None)
        if attr_val is None:
            return []

        type_map = {
            "str": (str, np.str_),
            "float": (float, np.floating),
            "int": (int, np.integer),
        }

        expected_py_type = type_map.get(expected_type)
        if expected_py_type is None:
            ctx.add_failure(f"Unknown expected type '{expected_type}'.")
            return [ctx.to_result()]

        if isinstance(attr_val, expected_py_type):
            ctx.add_pass()
        else:
            ctx.add_failure(
                f"Attribute '{var_name}.{attr_name}' has type {type(attr_val).__name__}, "
                f"expected {expected_type}."
            )
    except Exception as e:
        ctx.add_failure(f"Error checking type for '{var_name}.{attr_name}': {e}")

    return [ctx.to_result()]


def _check_attr_utf8(ds, var_name, attr_name, check_id, severity):
    """
    Internal helper to verify a string attribute contains valid UTF-8 encoding.

    Parameters
    ----------
    ds : netCDF4.Dataset
        An open netCDF dataset.
    var_name : str
        The name of the variable (e.g., 'lat', 'height').
    attr_name : str
        The name of the attribute to check (e.g., 'units', 'long_name').
    check_id : str
        The unique check identifier (e.g., 'V006').
    severity : int
        The severity level (BaseCheck.HIGH, BaseCheck.MEDIUM, BaseCheck.LOW).

    Returns
    -------
    list[Result]
        A list containing one Result object with pass/fail status.
    """
    ctx = TestCtx(severity, f"[{check_id}] UTF-8 Encoding: '{var_name}.{attr_name}'")

    if var_name not in ds.variables:
        return []

    var = ds.variables[var_name]
    try:
        attr_val = getattr(var, attr_name, None)
        if attr_val is None or not isinstance(attr_val, str):
            return []

        attr_val.encode("utf-8")
        ctx.add_pass()
    except UnicodeEncodeError:
        ctx.add_failure(f"Attribute '{var_name}.{attr_name}' contains non-UTF-8 characters.")
    except Exception as e:
        ctx.add_failure(f"Error checking UTF-8 for '{var_name}.{attr_name}': {e}")

    return [ctx.to_result()]


def _check_attr_value(ds, var_name, attr_name, expected_value, check_id, severity, case_insensitive=False):
    """
    Internal helper to verify an attribute has an expected value.

    Parameters
    ----------
    ds : netCDF4.Dataset
        An open netCDF dataset.
    var_name : str
        The name of the variable (e.g., 'lat', 'height').
    attr_name : str
        The name of the attribute to check (e.g., 'axis', 'units').
    expected_value : str
        The expected attribute value (e.g., 'Y', 'degrees_north').
    check_id : str
        The unique check identifier (e.g., 'V007').
    severity : int
        The severity level (BaseCheck.HIGH, BaseCheck.MEDIUM, BaseCheck.LOW).
    case_insensitive : bool
        If True, compare values case-insensitively (default: False).

    Returns
    -------
    list[Result]
        A list containing one Result object with pass/fail status.
    """
    ctx = TestCtx(severity, f"[{check_id}] Attribute Value: '{var_name}.{attr_name}' = '{expected_value}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    var = ds.variables[var_name]
    try:
        attr_val = getattr(var, attr_name, None)
        if attr_val is None:
            ctx.add_failure(f"Attribute '{attr_name}' not found on variable '{var_name}'.")
            return [ctx.to_result()]

        actual = str(attr_val).strip()
        expected = str(expected_value).strip()

        if case_insensitive:
            match = actual.lower() == expected.lower()
        else:
            match = actual == expected

        if match:
            ctx.add_pass()
        else:
            ctx.add_failure(
                f"Expected '{var_name}.{attr_name}' = '{expected_value}', got '{attr_val}'."
            )
    except Exception as e:
        ctx.add_failure(f"Error checking value for '{var_name}.{attr_name}': {e}")

    return [ctx.to_result()]


# ===========================================================================
# HEIGHT ATTRIBUTE CHECKS
# ===========================================================================

def check_height_axis_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "height", "axis", "V004", severity)

def check_height_axis_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "height", "axis", "str", "V005", severity)

def check_height_axis_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "height", "axis", "V006", severity)

def check_height_axis_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "height", "axis", "Z", "V007", severity)

def check_height_standard_name_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "height", "standard_name", "str", "V009", severity)

def check_height_standard_name_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "height", "standard_name", "V010", severity)

def check_height_standard_name_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "height", "standard_name", "height", "V011", severity)

def check_height_long_name_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "height", "long_name", "V012", severity)

def check_height_long_name_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "height", "long_name", "str", "V013", severity)

def check_height_long_name_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "height", "long_name", "V014", severity)

def check_height_long_name_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "height", "long_name", "height", "V015", severity, case_insensitive=True)

def check_height_units_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "height", "units", "str", "V017", severity)

def check_height_units_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "height", "units", "V018", severity)

def check_height_positive_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "height", "positive", "str", "V021", severity)

def check_height_positive_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "height", "positive", "V022", severity)


# ===========================================================================
# LAT ATTRIBUTE CHECKS
# ===========================================================================

def check_lat_axis_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lat", "axis", "str", "V046", severity)

def check_lat_axis_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "lat", "axis", "V047", severity)

def check_lat_axis_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "lat", "axis", "Y", "V048", severity)

def check_lat_standard_name_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lat", "standard_name", "str", "V050", severity)

def check_lat_standard_name_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "lat", "standard_name", "V051", severity)

def check_lat_long_name_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "lat", "long_name", "V053", severity)

def check_lat_long_name_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lat", "long_name", "str", "V054", severity)

def check_lat_long_name_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "lat", "long_name", "V055", severity)

def check_lat_long_name_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "lat", "long_name", "latitude", "V056", severity, case_insensitive=True)

def check_lat_units_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lat", "units", "str", "V058", severity)

def check_lat_units_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "lat", "units", "V059", severity)

def check_lat_bounds_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "lat", "bounds", "V061", severity)

def check_lat_bounds_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lat", "bounds", "str", "V062", severity)

def check_lat_bounds_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "lat", "bounds", "V063", severity)

def check_lat_actual_range_exists(ds, severity=BaseCheck.LOW):
    return _check_attr_exists(ds, "lat", "actual_range", "V065", severity)

def check_lat_actual_range_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lat", "actual_range", "float", "V066", severity)


# ===========================================================================
# LON ATTRIBUTE CHECKS
# ===========================================================================

def check_lon_axis_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lon", "axis", "str", "V084", severity)

def check_lon_axis_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "lon", "axis", "V085", severity)

def check_lon_axis_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "lon", "axis", "X", "V086", severity)

def check_lon_standard_name_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lon", "standard_name", "str", "V088", severity)

def check_lon_standard_name_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "lon", "standard_name", "V089", severity)

def check_lon_long_name_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "lon", "long_name", "V091", severity)

def check_lon_long_name_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lon", "long_name", "str", "V092", severity)

def check_lon_long_name_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "lon", "long_name", "V093", severity)

def check_lon_long_name_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "lon", "long_name", "longitude", "V094", severity, case_insensitive=True)

def check_lon_units_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lon", "units", "str", "V096", severity)

def check_lon_units_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "lon", "units", "V097", severity)

def check_lon_bounds_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "lon", "bounds", "V099", severity)

def check_lon_bounds_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lon", "bounds", "str", "V100", severity)

def check_lon_bounds_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "lon", "bounds", "V101", severity)

def check_lon_actual_range_exists(ds, severity=BaseCheck.LOW):
    return _check_attr_exists(ds, "lon", "actual_range", "V103", severity)

def check_lon_actual_range_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "lon", "actual_range", "float", "V104", severity)


# ===========================================================================
# I VARIABLE ATTRIBUTE CHECKS
# ===========================================================================

def check_i_units_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "i", "units", "V228", severity)

def check_i_units_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "i", "units", "str", "V229", severity)

def check_i_units_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "i", "units", "V230", severity)

def check_i_units_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "i", "units", "1", "V231", severity)

def check_i_long_name_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "i", "long_name", "V232", severity)

def check_i_long_name_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "i", "long_name", "str", "V233", severity)

def check_i_long_name_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "i", "long_name", "V234", severity)

def check_i_long_name_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "i", "long_name", "cell index", "V235", severity, case_insensitive=True)


# ===========================================================================
# J VARIABLE ATTRIBUTE CHECKS
# ===========================================================================

def check_j_units_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "j", "units", "V236", severity)

def check_j_units_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "j", "units", "str", "V237", severity)

def check_j_units_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "j", "units", "V238", severity)

def check_j_units_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "j", "units", "1", "V239", severity)

def check_j_long_name_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "j", "long_name", "V240", severity)

def check_j_long_name_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "j", "long_name", "str", "V241", severity)

def check_j_long_name_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "j", "long_name", "V242", severity)

def check_j_long_name_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "j", "long_name", "cell index", "V243", severity, case_insensitive=True)


# ===========================================================================
# VERTICES_LATITUDE ATTRIBUTE CHECKS
# ===========================================================================

def check_vertices_latitude_units_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "vertices_latitude", "units", "V244", severity)

def check_vertices_latitude_units_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "vertices_latitude", "units", "str", "V245", severity)

def check_vertices_latitude_units_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "vertices_latitude", "units", "V246", severity)

def check_vertices_latitude_units_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "vertices_latitude", "units", "degrees_north", "V247", severity)

def check_vertices_latitude_missing_value_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "vertices_latitude", "missing_value", "V248", severity)

def check_vertices_latitude_missing_value_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "vertices_latitude", "missing_value", "float", "V249", severity)

def check_vertices_latitude_fillvalue_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "vertices_latitude", "_FillValue", "V251", severity)

def check_vertices_latitude_fillvalue_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "vertices_latitude", "_FillValue", "float", "V252", severity)


# ===========================================================================
# VERTICES_LONGITUDE ATTRIBUTE CHECKS
# ===========================================================================

def check_vertices_longitude_units_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "vertices_longitude", "units", "V254", severity)

def check_vertices_longitude_units_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "vertices_longitude", "units", "str", "V255", severity)

def check_vertices_longitude_units_utf8(ds, severity=BaseCheck.LOW):
    return _check_attr_utf8(ds, "vertices_longitude", "units", "V256", severity)

def check_vertices_longitude_units_value(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_value(ds, "vertices_longitude", "units", "degrees_east", "V257", severity)

def check_vertices_longitude_missing_value_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "vertices_longitude", "missing_value", "V258", severity)

def check_vertices_longitude_missing_value_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "vertices_longitude", "missing_value", "float", "V259", severity)

def check_vertices_longitude_fillvalue_exists(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_exists(ds, "vertices_longitude", "_FillValue", "V261", severity)

def check_vertices_longitude_fillvalue_type(ds, severity=BaseCheck.MEDIUM):
    return _check_attr_type(ds, "vertices_longitude", "_FillValue", "float", "V262", severity)
