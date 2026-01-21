#!/usr/bin/env python
"""
atomic checks that verify whether bounds intervals
are contiguous (no gaps or overlaps between adjacent intervals).
"""

from compliance_checker.base import BaseCheck, TestCtx
import numpy as np

from ..utils import get_bounds_data


def _check_bounds_contiguity(ds, bnds_var_name, check_id, severity):
    """
    Internal helper function to check bounds contiguity.
    """
    ctx = TestCtx(severity, f"[{check_id}] Bounds Contiguity: '{bnds_var_name}'")

    bnds, error_msg = get_bounds_data(ds, bnds_var_name)
    if error_msg:
        ctx.add_failure(error_msg)
        return [ctx.to_result()]

    try:
        if bnds.shape[0] < 2:
            # Only one interval, nothing to check for contiguity
            ctx.add_pass()
            return [ctx.to_result()]

        # Upper bound of interval i should equal lower bound of interval i+1
        upper = bnds[:-1, 1]  # Upper bounds of all intervals except last
        lower_next = bnds[1:, 0]  # Lower bounds of all intervals except first

        # Use isclose for floating point comparison
        contiguous = np.isclose(upper, lower_next)

        if not contiguous.all():
            non_contiguous_idx = np.where(~contiguous)[0]
            count = len(non_contiguous_idx)

            # Show examples of gaps/overlaps
            examples = []
            for i in non_contiguous_idx[:3]:
                gap = lower_next[i] - upper[i]
                if gap > 0:
                    examples.append(f"gap at idx {i}: [{upper[i]}, {lower_next[i]}] (gap={gap})")
                else:
                    examples.append(f"overlap at idx {i}: [{upper[i]}, {lower_next[i]}] (overlap={-gap})")

            ctx.add_failure(
                f"{count} gap(s)/overlap(s) found between intervals. "
                f"Examples: {'; '.join(examples)}"
            )
        else:
            ctx.add_pass()

    except Exception as e:
        ctx.add_failure(f"Error checking bounds contiguity for '{bnds_var_name}': {e}")

    return [ctx.to_result()]


# V043: lat_bnds contiguity
def check_lat_bnds_contiguity(ds, severity=BaseCheck.MEDIUM):
    """
    Verify that lat_bnds intervals are contiguous (no gaps or overlaps).
    """
    check_id = "V043"
    return _check_bounds_contiguity(ds, "lat_bnds", check_id, severity)


# V081: lon_bnds contiguity
def check_lon_bnds_contiguity(ds, severity=BaseCheck.MEDIUM):
    """
    Verify that lon_bnds intervals are contiguous (no gaps or overlaps).
    """
    check_id = "V081"
    return _check_bounds_contiguity(ds, "lon_bnds", check_id, severity)
