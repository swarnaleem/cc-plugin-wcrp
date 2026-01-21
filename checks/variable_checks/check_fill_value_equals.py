#!/usr/bin/env python
"""
atomic checks that verify whether a fill value
attribute (_FillValue or missing_value) equals an expected value.
"""

from compliance_checker.base import BaseCheck, TestCtx
import numpy as np


def _check_fill_value_equals(ds, var_name, attr_name, expected_value, check_id, severity):
    """
    Internal helper function to check fill value equals expected.
    """
    ctx = TestCtx(severity, f"[{check_id}] Fill Value: '{var_name}.{attr_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    var = ds.variables[var_name]
    fill_val = getattr(var, attr_name, None)

    if fill_val is None:
        ctx.add_failure(
            f"Attribute '{attr_name}' not found on variable '{var_name}'."
        )
        return [ctx.to_result()]

    try:
        # Use numpy isclose for floating point comparison with relative tolerance
        if np.isclose(fill_val, expected_value, rtol=1e-5):
            ctx.add_pass()
        else:
            ctx.add_failure(
                f"Expected {attr_name}={expected_value}, got {fill_val}."
            )

    except Exception as e:
        ctx.add_failure(f"Error checking fill value for '{var_name}.{attr_name}': {e}")

    return [ctx.to_result()]


# V250: vertices_latitude missing_value = 1.e+20f
def check_vertices_latitude_missing_value(ds, severity=BaseCheck.MEDIUM):
    """
    Verify that vertices_latitude missing_value equals 1.e+20.
    """
    check_id = "V250"
    return _check_fill_value_equals(ds, "vertices_latitude", "missing_value", 1.e+20, check_id, severity)


# V253: vertices_latitude _FillValue = 1.e+20f
def check_vertices_latitude_fill_value(ds, severity=BaseCheck.MEDIUM):
    """
    Verify that vertices_latitude _FillValue equals 1.e+20.
    """
    check_id = "V253"
    return _check_fill_value_equals(ds, "vertices_latitude", "_FillValue", 1.e+20, check_id, severity)


# V260: vertices_longitude missing_value = 1.e+20f
def check_vertices_longitude_missing_value(ds, severity=BaseCheck.MEDIUM):
    """
    Verify that vertices_longitude missing_value equals 1.e+20.
    """
    check_id = "V260"
    return _check_fill_value_equals(ds, "vertices_longitude", "missing_value", 1.e+20, check_id, severity)


# V263: vertices_longitude _FillValue = 1.e+20f
def check_vertices_longitude_fill_value(ds, severity=BaseCheck.MEDIUM):
    """
    Verify that vertices_longitude _FillValue equals 1.e+20.
    """
    check_id = "V263"
    return _check_fill_value_equals(ds, "vertices_longitude", "_FillValue", 1.e+20, check_id, severity)
