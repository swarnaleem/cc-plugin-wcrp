#!/usr/bin/env python
"""
This module provides atomic checks that verify whether all values of a
variable fall within a specified range.
"""

from compliance_checker.base import BaseCheck, TestCtx

from ..utils import get_variable_data


def _check_value_range(ds, var_name, min_val, max_val, check_id, severity):
    """
    Internal helper to verify all values of a variable fall within a range.

    Parameters
    ----------
    ds : netCDF4.Dataset
        An open netCDF dataset.
    var_name : str
        The name of the variable to check (e.g., 'lat', 'lon').
    min_val : float
        The minimum allowed value (inclusive).
    max_val : float
        The maximum allowed value (inclusive).
    check_id : str
        The unique check identifier (e.g., 'V036' for lat range).
    severity : int
        The severity level (BaseCheck.HIGH, BaseCheck.MEDIUM, BaseCheck.LOW).

    Returns
    -------
    list[Result]
        A list containing one Result object with pass/fail status.
    """
    ctx = TestCtx(severity, f"[{check_id}] Value Range: '{var_name}' in [{min_val}, {max_val}]")

    data, error_msg = get_variable_data(ds, var_name)
    if error_msg:
        ctx.add_failure(error_msg)
        return [ctx.to_result()]

    try:
        if len(data) == 0:
            ctx.add_pass()
            return [ctx.to_result()]

        below_min = data < min_val
        above_max = data > max_val
        outside_range = below_min | above_max

        if outside_range.any():
            count = outside_range.sum()
            out_of_range_values = data[outside_range]
            examples = out_of_range_values[:5]
            examples_str = ", ".join(f"{v}" for v in examples)
            ctx.add_failure(
                f"{count} value(s) outside range [{min_val}, {max_val}]. "
                f"Examples: {examples_str}"
            )
        else:
            ctx.add_pass()

    except Exception as e:
        ctx.add_failure(f"Error checking value range for '{var_name}': {e}")

    return [ctx.to_result()]


# V036: lat values within -90 to 90
def check_lat_value_range(ds, severity=BaseCheck.HIGH):
    return _check_value_range(ds, "lat", -90, 90, "V036", severity)


# V074: lon values within 0 to 360
def check_lon_value_range(ds, severity=BaseCheck.HIGH):
    return _check_value_range(ds, "lon", 0, 360, "V074", severity)


# V044: lat_bnds values within -90 to 90
def check_lat_bnds_value_range(ds, severity=BaseCheck.HIGH):
    return _check_value_range(ds, "lat_bnds", -90, 90, "V044", severity)


# V082: lon_bnds values within 0 to 360
def check_lon_bnds_value_range(ds, severity=BaseCheck.HIGH):
    return _check_value_range(ds, "lon_bnds", 0, 360, "V082", severity)


# V222: vertices_latitude values within -90 to 90
def check_vertices_latitude_value_range(ds, severity=BaseCheck.HIGH):
    return _check_value_range(ds, "vertices_latitude", -90, 90, "V222", severity)


# V227: vertices_longitude values within 0 to 360
def check_vertices_longitude_value_range(ds, severity=BaseCheck.HIGH):
    return _check_value_range(ds, "vertices_longitude", 0, 360, "V227", severity)


# Generic function for dynamic coordinate checks
def check_value_range(ds, var_name, min_val, max_val, severity=BaseCheck.HIGH):
    return _check_value_range(ds, var_name, min_val, max_val, "VAR", severity)
