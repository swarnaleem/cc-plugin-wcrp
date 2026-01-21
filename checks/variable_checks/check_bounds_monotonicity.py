#!/usr/bin/env python
"""
atomic checks that verify whether bounds values
are monotonically non-decreasing.
"""

from compliance_checker.base import BaseCheck, TestCtx
import numpy as np

from ..utils import get_bounds_data


def _check_bounds_monotonicity(ds, bnds_var_name, check_id, severity):
    """
    Internal helper function to check bounds monotonicity.
    """
    ctx = TestCtx(severity, f"[{check_id}] Bounds Monotonicity: '{bnds_var_name}'")

    bnds, error_msg = get_bounds_data(ds, bnds_var_name)
    if error_msg:
        ctx.add_failure(error_msg)
        return [ctx.to_result()]

    try:
        lower = bnds[:, 0]
        upper = bnds[:, 1]

        # Check monotonicity (non-decreasing: diff >= 0)
        lower_diff = np.diff(lower)
        upper_diff = np.diff(upper)

        lower_monotonic = np.all(lower_diff >= 0)
        upper_monotonic = np.all(upper_diff >= 0)

        failures = []
        if not lower_monotonic:
            decreasing_idx = np.where(lower_diff < 0)[0][:3]
            examples = ", ".join(f"idx {i}: {lower[i]} > {lower[i+1]}" for i in decreasing_idx)
            failures.append(f"Lower bounds not monotonic. Examples: {examples}")

        if not upper_monotonic:
            decreasing_idx = np.where(upper_diff < 0)[0][:3]
            examples = ", ".join(f"idx {i}: {upper[i]} > {upper[i+1]}" for i in decreasing_idx)
            failures.append(f"Upper bounds not monotonic. Examples: {examples}")

        if failures:
            ctx.add_failure("; ".join(failures))
        else:
            ctx.add_pass()

    except Exception as e:
        ctx.add_failure(f"Error checking bounds monotonicity for '{bnds_var_name}': {e}")

    return [ctx.to_result()]


# V042: lat_bnds monotonicity
def check_lat_bnds_monotonicity(ds, severity=BaseCheck.MEDIUM):
    """
    Verify that lat_bnds values are monotonically non-decreasing.
    """
    check_id = "V042"
    return _check_bounds_monotonicity(ds, "lat_bnds", check_id, severity)


# V080: lon_bnds monotonicity
def check_lon_bnds_monotonicity(ds, severity=BaseCheck.MEDIUM):
    """
    Verify that lon_bnds values are monotonically non-decreasing.
    """
    check_id = "V080"
    return _check_bounds_monotonicity(ds, "lon_bnds", check_id, severity)
