#!/usr/bin/env python
"""
This module provides atomic checks that verify whether specific variables
contain no NaN or Inf values. Reuses check_nan_inf from data_plausibility_checks.
"""

from compliance_checker.base import BaseCheck
from checks.data_plausibility_checks.check_nan_inf import check_nan_inf


def _check_no_nan_inf(ds, var_name, check_id, severity):
    """
    Internal helper to check for NaN and Inf values using existing check_nan_inf.
    Returns combined results for both NaN and Inf checks.
    """
    results = []
    if var_name not in ds.variables:
        return results

    # Check for NaN
    ctx_nan = check_nan_inf(ds, var_name, parameter="NaN", severity=severity)
    results.append(ctx_nan.to_result())

    # Check for Inf
    ctx_inf = check_nan_inf(ds, var_name, parameter="Inf", severity=severity)
    results.append(ctx_inf.to_result())

    return results


# V033: lat no NaN/Inf values
def check_lat_no_nan_inf(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lat' variable contains no NaN or Inf values."""
    return _check_no_nan_inf(ds, "lat", "V033", severity)


# V071: lon no NaN/Inf values
def check_lon_no_nan_inf(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lon' variable contains no NaN or Inf values."""
    return _check_no_nan_inf(ds, "lon", "V071", severity)


# V041: lat_bnds no NaN/Inf values
def check_lat_bnds_no_nan_inf(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lat_bnds' variable contains no NaN or Inf values."""
    return _check_no_nan_inf(ds, "lat_bnds", "V041", severity)


# V079: lon_bnds no NaN/Inf values
def check_lon_bnds_no_nan_inf(ds, severity=BaseCheck.HIGH):
    """Verify that the 'lon_bnds' variable contains no NaN or Inf values."""
    return _check_no_nan_inf(ds, "lon_bnds", "V079", severity)


# V207: i no NaN/Inf values
def check_i_no_nan_inf(ds, severity=BaseCheck.HIGH):
    """Verify that the 'i' variable contains no NaN or Inf values."""
    return _check_no_nan_inf(ds, "i", "V207", severity)


# V214: j no NaN/Inf values
def check_j_no_nan_inf(ds, severity=BaseCheck.HIGH):
    """Verify that the 'j' variable contains no NaN or Inf values."""
    return _check_no_nan_inf(ds, "j", "V214", severity)


# V221: vertices_latitude no NaN/Inf values
def check_vertices_latitude_no_nan_inf(ds, severity=BaseCheck.HIGH):
    """Verify that the 'vertices_latitude' variable contains no NaN or Inf values."""
    return _check_no_nan_inf(ds, "vertices_latitude", "V221", severity)


# V226: vertices_longitude no NaN/Inf values
def check_vertices_longitude_no_nan_inf(ds, severity=BaseCheck.HIGH):
    """Verify that the 'vertices_longitude' variable contains no NaN or Inf values."""
    return _check_no_nan_inf(ds, "vertices_longitude", "V226", severity)
