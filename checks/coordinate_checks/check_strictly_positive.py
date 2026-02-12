#!/usr/bin/env python
"""
This module provides atomic checks that verify whether all values of a
variable are strictly positive (> 0).
"""

from compliance_checker.base import BaseCheck, TestCtx

from ..utils import get_variable_data


def _check_strictly_positive(ds, var_name, check_id, severity):
    """
    Internal helper to verify all values of a variable are strictly positive (> 0).

    Parameters
    ----------
    ds : netCDF4.Dataset
        An open netCDF dataset.
    var_name : str
        The name of the variable to check (e.g., 'height', 'i', 'j').
    check_id : str
        The unique check identifier (e.g., 'V003' for height).
    severity : int
        The severity level (BaseCheck.HIGH, BaseCheck.MEDIUM, BaseCheck.LOW).

    Returns
    -------
    list[Result]
        A list containing one Result object with pass/fail status.
    """
    ctx = TestCtx(severity, f"[{check_id}] Strictly Positive: '{var_name}'")

    data, error_msg = get_variable_data(ds, var_name)
    if error_msg:
        ctx.add_failure(error_msg)
        return [ctx.to_result()]

    try:
        if len(data) == 0:
            ctx.add_pass()
            return [ctx.to_result()]

        non_positive = data <= 0

        if non_positive.any():
            count = non_positive.sum()
            non_positive_values = data[non_positive]
            examples = non_positive_values[:5]
            examples_str = ", ".join(f"{v}" for v in examples)
            ctx.add_failure(
                f"{count} value(s) are not strictly positive (<=0). "
                f"Examples: {examples_str}"
            )
        else:
            ctx.add_pass()

    except Exception as e:
        ctx.add_failure(f"Error checking strictly positive for '{var_name}': {e}")

    return [ctx.to_result()]


# V003: height values strictly positive
def check_height_strictly_positive(ds, severity=BaseCheck.HIGH):
    return _check_strictly_positive(ds, "height", "V003", severity)


# V208: i values strictly positive
def check_i_strictly_positive(ds, severity=BaseCheck.HIGH):
    return _check_strictly_positive(ds, "i", "V208", severity)


# V215: j values strictly positive
def check_j_strictly_positive(ds, severity=BaseCheck.HIGH):
    return _check_strictly_positive(ds, "j", "V215", severity)


# Generic function for dynamic coordinate checks
def check_strictly_positive(ds, var_name, severity=BaseCheck.HIGH):
    return _check_strictly_positive(ds, var_name, "VAR", severity)
