#!/usr/bin/env python
"""
atomic checks that verify whether all values of a
variable fall within its declared actual_range attribute.

This is differnt from CF's check_actual_range which validates that
actual_range matches the data min/max. This check validates that all data
values are contained within the declared actual_range.
"""

from compliance_checker.base import BaseCheck, TestCtx

from ..utils import get_variable_data


def _check_data_within_actual_range(ds, var_name, check_id, severity):
    """
    Internal helper function to check data within actual_range.
    """
    ctx = TestCtx(severity, f"[{check_id}] Data Within Actual Range: '{var_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    var = ds.variables[var_name]
    actual_range = getattr(var, 'actual_range', None)

    # If no actual_range attribute, skip this check
    if actual_range is None:
        return []

    try:
        # Validate actual_range has 2 elements
        if len(actual_range) != 2:
            ctx.add_failure(
                f"actual_range attribute has {len(actual_range)} elements, expected 2."
            )
            return [ctx.to_result()]

        min_val, max_val = actual_range[0], actual_range[1]

        data, error_msg = get_variable_data(ds, var_name)
        if error_msg:
            ctx.add_failure(error_msg)
            return [ctx.to_result()]

        if len(data) == 0:
            ctx.add_pass()
            return [ctx.to_result()]

        data_min = data.min()
        data_max = data.max()

        if data_min >= min_val and data_max <= max_val:
            ctx.add_pass()
        else:
            ctx.add_failure(
                f"Data range [{data_min}, {data_max}] is outside "
                f"actual_range [{min_val}, {max_val}]."
            )

    except Exception as e:
        ctx.add_failure(f"Error checking data within actual_range for '{var_name}': {e}")

    return [ctx.to_result()]


# V067: lat data within actual_range
def check_lat_data_within_actual_range(ds, severity=BaseCheck.LOW):
    """
    Verify that all lat values fall within the declared actual_range attribute.
    """
    check_id = "V067"
    return _check_data_within_actual_range(ds, "lat", check_id, severity)


# V105: lon data within actual_range
def check_lon_data_within_actual_range(ds, severity=BaseCheck.LOW):
    """
    Verify that all lon values fall within the declared actual_range attribute.
    """
    check_id = "V105"
    return _check_data_within_actual_range(ds, "lon", check_id, severity)
