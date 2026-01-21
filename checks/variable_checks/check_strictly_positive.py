#!/usr/bin/env python
"""
atomic checks that verify whether all values of a
variable are strictly positive (> 0).
"""

from compliance_checker.base import BaseCheck, TestCtx

from ..utils import get_variable_data


def _check_strictly_positive(ds, var_name, check_id, severity):
    """
    Internal helper function to check strictly positive values.
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
    """
    Verify that all height values are strictly positive (> 0).
    """
    check_id = "V003"
    return _check_strictly_positive(ds, "height", check_id, severity)


# V208: i values strictly positive
def check_i_strictly_positive(ds, severity=BaseCheck.HIGH):
    """
    Verify that all i (cell index) values are strictly positive (> 0).
    """
    check_id = "V208"
    return _check_strictly_positive(ds, "i", check_id, severity)


# V215: j values strictly positive
def check_j_strictly_positive(ds, severity=BaseCheck.HIGH):
    """
    Verify that all j (cell index) values are strictly positive (> 0).
    """
    check_id = "V215"
    return _check_strictly_positive(ds, "j", check_id, severity)
