#!/usr/bin/env python
"""
This module provides atomic checks that verify whether specific variables
exist in a netCDF dataset. Each function uses a specific check ID.
"""

from compliance_checker.base import BaseCheck, TestCtx


def _check_var_exists(ds, var_name, check_id, severity):
    """Internal helper to check if a variable exists with a specific check ID."""
    ctx = TestCtx(severity, f"[{check_id}] Variable Existence: '{var_name}'")
    ctx.assert_true(var_name in ds.variables, f"Variable '{var_name}' is missing.")
    return [ctx.to_result()]


# V030: lat variable exists
def check_lat_exists(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lat' variable exists in the dataset."""
    return _check_var_exists(ds, "lat", "V030", severity)


# V068: lon variable exists
def check_lon_exists(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lon' variable exists in the dataset."""
    return _check_var_exists(ds, "lon", "V068", severity)


# V001: height variable exists
def check_height_exists(ds, severity=BaseCheck.HIGH):
    """Verify that the 'height' variable exists in the dataset."""
    return _check_var_exists(ds, "height", "V001", severity)


# V038: lat_bnds variable exists
def check_lat_bnds_exists(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lat_bnds' variable exists in the dataset."""
    return _check_var_exists(ds, "lat_bnds", "V038", severity)


# V076: lon_bnds variable exists
def check_lon_bnds_exists(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lon_bnds' variable exists in the dataset."""
    return _check_var_exists(ds, "lon_bnds", "V076", severity)


# V204: i variable exists
def check_i_exists(ds, severity=BaseCheck.HIGH):
    """Verify that the 'i' variable exists in the dataset."""
    return _check_var_exists(ds, "i", "V204", severity)


# V211: j variable exists
def check_j_exists(ds, severity=BaseCheck.HIGH):
    """Verify that the 'j' variable exists in the dataset."""
    return _check_var_exists(ds, "j", "V211", severity)


# V218: vertices_latitude variable exists
def check_vertices_latitude_exists(ds, severity=BaseCheck.HIGH):
    """Verify that the 'vertices_latitude' variable exists in the dataset."""
    return _check_var_exists(ds, "vertices_latitude", "V218", severity)


# V223: vertices_longitude variable exists
def check_vertices_longitude_exists(ds, severity=BaseCheck.HIGH):
    """Verify that the 'vertices_longitude' variable exists in the dataset."""
    return _check_var_exists(ds, "vertices_longitude", "V223", severity)
