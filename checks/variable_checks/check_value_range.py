#!/usr/bin/env python
"""
atomic checks that verify whether all values of a
variable fall within a specified range.
"""

from compliance_checker.base import BaseCheck, TestCtx

from ..utils import get_variable_data


def _check_value_range(ds, var_name, min_val, max_val, check_id, severity):
    """
    Internal helper function to check value range.
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
    """
    Verify that all lat values are within -90 to 90 degrees north.
    """
    check_id = "V036"
    return _check_value_range(ds, "lat", -90, 90, check_id, severity)


# V074: lon values within 0 to 360
def check_lon_value_range(ds, severity=BaseCheck.HIGH):
    """
    Verify that all lon values are within 0 to 360 degrees east.
    """
    check_id = "V074"
    return _check_value_range(ds, "lon", 0, 360, check_id, severity)


# V044: lat_bnds values within -90 to 90
def check_lat_bnds_value_range(ds, severity=BaseCheck.HIGH):
    """
    Verify that all lat_bnds values are within -90 to 90 degrees north.
    """
    check_id = "V044"
    return _check_value_range(ds, "lat_bnds", -90, 90, check_id, severity)


# V082: lon_bnds values within 0 to 360
def check_lon_bnds_value_range(ds, severity=BaseCheck.HIGH):
    """
    Verify that all lon_bnds values are within 0 to 360 degrees east.
    """
    check_id = "V082"
    return _check_value_range(ds, "lon_bnds", 0, 360, check_id, severity)


# V222: vertices_latitude values within -90 to 90
def check_vertices_latitude_value_range(ds, severity=BaseCheck.HIGH):
    """
    Verify that all vertices_latitude values are within -90 to 90 degrees north.
    """
    check_id = "V222"
    return _check_value_range(ds, "vertices_latitude", -90, 90, check_id, severity)


# V227: vertices_longitude values within 0 to 360
def check_vertices_longitude_value_range(ds, severity=BaseCheck.HIGH):
    """
    Verify that all vertices_longitude values are within 0 to 360 degrees east.
    """
    check_id = "V227"
    return _check_value_range(ds, "vertices_longitude", 0, 360, check_id, severity)
