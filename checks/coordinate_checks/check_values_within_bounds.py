#!/usr/bin/env python
"""
This module provides atomic checks that verify whether coordinate values
lie within their corresponding bounds variable ranges.
Each function uses a specific check ID.
"""

from compliance_checker.base import BaseCheck, TestCtx
import numpy as np


def _check_values_within_bounds(ds, var_name, check_id, severity):
    """
    Internal helper to verify coordinate values lie within their bounds.

    For each coordinate value, checks that it falls within the corresponding
    bounds interval [lower, upper] from the associated bounds variable.

    Parameters
    ----------
    ds : netCDF4.Dataset
        An open netCDF dataset.
    var_name : str
        The name of the coordinate variable (e.g., 'lat', 'lon').
    check_id : str
        The unique check identifier (e.g., 'V037' for lat).
    severity : int
        The severity level (BaseCheck.HIGH, BaseCheck.MEDIUM, BaseCheck.LOW).

    Returns
    -------
    list[Result]
        A list containing one Result object with pass/fail status.
    """
    ctx = TestCtx(severity, f"[{check_id}] Bounds Consistency: '{var_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    var = ds.variables[var_name]

    # Get bounds variable name
    bounds_name = getattr(var, "bounds", None)
    if bounds_name is None:
        bounds_name = f"{var_name}_bnds"

    if bounds_name not in ds.variables:
        ctx.add_failure(f"Bounds variable '{bounds_name}' not found.")
        return [ctx.to_result()]

    bounds_var = ds.variables[bounds_name]
    values = var[:]
    bounds = bounds_var[:]

    try:
        all_within = True
        for i, (val, bnds) in enumerate(zip(values, bounds)):
            low = min(bnds)
            high = max(bnds)
            if not (low <= val <= high):
                ctx.add_failure(
                    f"Value {val} at index {i} is outside bounds [{low}, {high}]."
                )
                all_within = False
                break  # Report first failure only

        if all_within:
            ctx.add_pass()
    except Exception as e:
        ctx.add_failure(f"Error checking bounds consistency: {e}")

    return [ctx.to_result()]


# V037: lat values within lat_bnds
def check_lat_values_within_bounds(ds, severity=BaseCheck.MEDIUM):
    return _check_values_within_bounds(ds, "lat", "V037", severity)


# V075: lon values within lon_bnds
def check_lon_values_within_bounds(ds, severity=BaseCheck.MEDIUM):
    return _check_values_within_bounds(ds, "lon", "V075", severity)
