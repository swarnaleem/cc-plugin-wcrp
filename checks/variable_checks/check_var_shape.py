#!/usr/bin/env python
"""
This module provides atomic checks that verify whether specific variables
have shapes that align with their declared dimensions. Each function uses a specific check ID.
"""

from compliance_checker.base import BaseCheck, TestCtx


def _check_var_shape(ds, var_name, check_id, severity):
    """Internal helper to check variable shape with a specific check ID."""
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
    """Verify that the 'lat' variable shape aligns with its declared dimensions."""
    return _check_var_shape(ds, "lat", "V032", severity)


# V070: lon shape aligns with lon dimension
def check_lon_shape(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lon' variable shape aligns with its declared dimensions."""
    return _check_var_shape(ds, "lon", "V070", severity)


# V040: lat_bnds shape aligns with bnds dimension
def check_lat_bnds_shape(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lat_bnds' variable shape aligns with its declared dimensions."""
    return _check_var_shape(ds, "lat_bnds", "V040", severity)


# V078: lon_bnds shape aligns with bnds dimension
def check_lon_bnds_shape(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lon_bnds' variable shape aligns with its declared dimensions."""
    return _check_var_shape(ds, "lon_bnds", "V078", severity)


# V206: i shape aligns with i dimension
def check_i_shape(ds, severity=BaseCheck.HIGH):
    """Verify that the 'i' variable shape aligns with its declared dimensions."""
    return _check_var_shape(ds, "i", "V206", severity)


# V213: j shape aligns with j dimension
def check_j_shape(ds, severity=BaseCheck.HIGH):
    """Verify that the 'j' variable shape aligns with its declared dimensions."""
    return _check_var_shape(ds, "j", "V213", severity)


# V220: vertices_latitude shape aligns with i, j, nv4/vertices
def check_vertices_latitude_shape(ds, severity=BaseCheck.HIGH):
    """Verify that the 'vertices_latitude' variable shape aligns with its declared dimensions."""
    return _check_var_shape(ds, "vertices_latitude", "V220", severity)


# V225: vertices_longitude shape aligns with i, j, nv4/vertices
def check_vertices_longitude_shape(ds, severity=BaseCheck.HIGH):
    """Verify that the 'vertices_longitude' variable shape aligns with its declared dimensions."""
    return _check_var_shape(ds, "vertices_longitude", "V225", severity)
