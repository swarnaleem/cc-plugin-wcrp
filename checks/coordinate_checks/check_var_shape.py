#!/usr/bin/env python
"""
This module provides atomic checks that verify whether specific variables
have shapes that align with their declared dimensions. Each function uses a specific check ID.
"""

from compliance_checker.base import BaseCheck, TestCtx


def _check_var_shape(ds, var_name, check_id, severity):
    """
    Internal helper to verify a variable's shape matches its declared dimensions.

    Checks that the number of dimensions matches the shape length and that
    each dimension size corresponds to the declared dimension size in the dataset.

    Parameters
    ----------
    ds : netCDF4.Dataset
        An open netCDF dataset.
    var_name : str
        The name of the variable to check (e.g., 'lat', 'lon', 'i').
    check_id : str
        The unique check identifier (e.g., 'V032' for lat shape).
    severity : int
        The severity level (BaseCheck.HIGH, BaseCheck.MEDIUM, BaseCheck.LOW).

    Returns
    -------
    list[Result]
        A list containing one Result object with pass/fail status.
    """
    ctx = TestCtx(severity, f"[{check_id}] Variable Shape: '{var_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    try:
        var = ds.variables[var_name]
        dims = var.dimensions
        shape = var.shape

        if len(dims) != len(shape):
            ctx.add_failure(
                f"Variable '{var_name}' has {len(dims)} dimensions but shape has {len(shape)} elements."
            )
        else:
            mismatch = False
            for dim_name, size in zip(dims, shape):
                if dim_name in ds.dimensions:
                    expected_size = len(ds.dimensions[dim_name])
                    if size != expected_size:
                        ctx.add_failure(
                            f"Variable '{var_name}' dimension '{dim_name}' has size {size}, "
                            f"expected {expected_size}."
                        )
                        mismatch = True
            if not mismatch:
                ctx.add_pass()
    except Exception as e:
        ctx.add_failure(f"Error checking shape for '{var_name}': {e}")

    return [ctx.to_result()]


# V032: lat shape aligns with lat dimension
def check_lat_shape(ds, severity=BaseCheck.HIGH):
    return _check_var_shape(ds, "lat", "V032", severity)


# V070: lon shape aligns with lon dimension
def check_lon_shape(ds, severity=BaseCheck.HIGH):
    return _check_var_shape(ds, "lon", "V070", severity)


# V040: lat_bnds shape aligns with bnds dimension
def check_lat_bnds_shape(ds, severity=BaseCheck.HIGH):
    return _check_var_shape(ds, "lat_bnds", "V040", severity)


# V078: lon_bnds shape aligns with bnds dimension
def check_lon_bnds_shape(ds, severity=BaseCheck.HIGH):
    return _check_var_shape(ds, "lon_bnds", "V078", severity)


# V206: i shape aligns with i dimension
def check_i_shape(ds, severity=BaseCheck.HIGH):
    return _check_var_shape(ds, "i", "V206", severity)


# V213: j shape aligns with j dimension
def check_j_shape(ds, severity=BaseCheck.HIGH):
    return _check_var_shape(ds, "j", "V213", severity)


# V220: vertices_latitude shape aligns with i, j, nv4/vertices
def check_vertices_latitude_shape(ds, severity=BaseCheck.HIGH):
    return _check_var_shape(ds, "vertices_latitude", "V220", severity)


# V225: vertices_longitude shape aligns with i, j, nv4/vertices
def check_vertices_longitude_shape(ds, severity=BaseCheck.HIGH):
    return _check_var_shape(ds, "vertices_longitude", "V225", severity)
