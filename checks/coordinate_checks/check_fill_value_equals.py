#!/usr/bin/env python
"""
This module provides atomic checks that verify whether a fill value
attribute (_FillValue or missing_value) equals an expected value.
"""

from compliance_checker.base import BaseCheck, TestCtx
import numpy as np


def _check_fill_value_equals(ds, var_name, attr_name, expected_value, check_id, severity):
    """
    Internal helper to verify a fill value attribute equals an expected value.

    Uses numpy.isclose for floating point comparison with relative tolerance.

    Parameters
    ----------
    ds : netCDF4.Dataset
        An open netCDF dataset.
    var_name : str
        The name of the variable (e.g., 'vertices_latitude').
    attr_name : str
        The fill value attribute name ('_FillValue' or 'missing_value').
    expected_value : float
        The expected fill value (e.g., 1.e+20).
    check_id : str
        The unique check identifier (e.g., 'V250').
    severity : int
        The severity level (BaseCheck.HIGH, BaseCheck.MEDIUM, BaseCheck.LOW).

    Returns
    -------
    list[Result]
        A list containing one Result object with pass/fail status.
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
    return _check_fill_value_equals(ds, "vertices_latitude", "missing_value", 1.e+20, "V250", severity)


# V253: vertices_latitude _FillValue = 1.e+20f
def check_vertices_latitude_fill_value(ds, severity=BaseCheck.MEDIUM):
    return _check_fill_value_equals(ds, "vertices_latitude", "_FillValue", 1.e+20, "V253", severity)


# V260: vertices_longitude missing_value = 1.e+20f
def check_vertices_longitude_missing_value(ds, severity=BaseCheck.MEDIUM):
    return _check_fill_value_equals(ds, "vertices_longitude", "missing_value", 1.e+20, "V260", severity)


# V263: vertices_longitude _FillValue = 1.e+20f
def check_vertices_longitude_fill_value(ds, severity=BaseCheck.MEDIUM):
    return _check_fill_value_equals(ds, "vertices_longitude", "_FillValue", 1.e+20, "V263", severity)
