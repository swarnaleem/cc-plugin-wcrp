#!/usr/bin/env python
"""
This module provides atomic checks that verify whether specific variables
have the expected data type. Each function uses a specific check ID.
"""

from compliance_checker.base import BaseCheck, TestCtx


def _check_var_type(ds, var_name, allowed_types, check_id, severity):
    """Internal helper to check variable type with a specific check ID."""
    ctx = TestCtx(severity, f"[{check_id}] Variable Type: '{var_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    var = ds.variables[var_name]
    try:
        dtype_kind = var.dtype.kind
    except AttributeError:
        ctx.add_failure(f"Could not determine dtype for variable '{var_name}'.")
        return [ctx.to_result()]

    if dtype_kind in allowed_types:
        ctx.add_pass()
    else:
        ctx.add_failure(
            f"Variable '{var_name}' has type '{dtype_kind}' (expected one of {allowed_types}). "
            f"Full dtype: {var.dtype}"
        )
    return [ctx.to_result()]


# V031: lat type NC_FLOAT
def check_lat_type(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lat' variable has type NC_FLOAT."""
    return _check_var_type(ds, "lat", ["f"], "V031", severity)


# V069: lon type NC_FLOAT
def check_lon_type(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lon' variable has type NC_FLOAT."""
    return _check_var_type(ds, "lon", ["f"], "V069", severity)


# V002: height type NC_FLOAT
def check_height_type(ds, severity=BaseCheck.HIGH):
    """Verify that the 'height' variable has type NC_FLOAT."""
    return _check_var_type(ds, "height", ["f"], "V002", severity)


# V039: lat_bnds type NC_FLOAT
def check_lat_bnds_type(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lat_bnds' variable has type NC_FLOAT."""
    return _check_var_type(ds, "lat_bnds", ["f"], "V039", severity)


# V077: lon_bnds type NC_FLOAT
def check_lon_bnds_type(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lon_bnds' variable has type NC_FLOAT."""
    return _check_var_type(ds, "lon_bnds", ["f"], "V077", severity)


# V205: i type NC_INT
def check_i_type(ds, severity=BaseCheck.HIGH):
    """Verify that the 'i' variable has type NC_INT."""
    return _check_var_type(ds, "i", ["i"], "V205", severity)


# V212: j type NC_INT
def check_j_type(ds, severity=BaseCheck.HIGH):
    """Verify that the 'j' variable has type NC_INT."""
    return _check_var_type(ds, "j", ["i"], "V212", severity)


# V219: vertices_latitude type NC_FLOAT
def check_vertices_latitude_type(ds, severity=BaseCheck.HIGH):
    """Verify that the 'vertices_latitude' variable has type NC_FLOAT."""
    return _check_var_type(ds, "vertices_latitude", ["f"], "V219", severity)


# V224: vertices_longitude type NC_FLOAT
def check_vertices_longitude_type(ds, severity=BaseCheck.HIGH):
    """Verify that the 'vertices_longitude' variable has type NC_FLOAT."""
    return _check_var_type(ds, "vertices_longitude", ["f"], "V224", severity)
