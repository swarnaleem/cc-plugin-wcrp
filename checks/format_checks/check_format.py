#!/usr/bin/env python


from compliance_checker.base import BaseCheck, TestCtx


def check_format(ds, expected_format, expected_data_model, severity=BaseCheck.HIGH):
    """
    Checks if the file is in the expected format.

    Args
    ----
    ds : xarray.Dataset
        The dataset being checked.
    expected_format: str
        The expected disk format, eg. "HDF5".
    expected_data_model: str
        The expected data model, eg. "NETCDF4_CLASSIC".
    severity : str
        The severity of the check. Default: BaseCheck.HIGH.

    Returns
    -------
    List of compliance_checker.base.Result
    """
    print(expected_format, expected_data_model, severity)
    check_id = "FILE002"
    desc = f"[{check_id}] File Format"
    testctx = TestCtx(severity, desc)

    if ds.disk_format != expected_format or ds.data_model != expected_data_model:
        testctx.add_failure(
            f"File format differs from expectation ({expected_data_model}/{expected_format}): "
            f"'{ds.data_model}/{ds.disk_format}'."
        )
    else:
        testctx.add_pass()

    return [testctx.to_result()]
