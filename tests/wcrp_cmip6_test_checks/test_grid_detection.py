"""Tests for the operation-based grid detection in checks.utils."""

import numpy as np
import pytest
import xarray as xr
from netCDF4 import Dataset

from checks.utils import GridDetectionResult, detect_grid_type


def _create_and_open(tmp_path, builder_fn):
    """Create a NetCDF file, populate it with *builder_fn*, and return
    (xarray.Dataset, netCDF4.Dataset) handles.
    """
    path = tmp_path / "test.nc"
    ncds = Dataset(str(path), "w")
    builder_fn(ncds)
    ncds.sync()
    xrds = xr.open_dataset(str(path), decode_coords=True, decode_times=False)
    return xrds, ncds


# ---------------------------------------------------------------------------
# Builder helpers
# ---------------------------------------------------------------------------

def _build_regular_1d(ncds):
    """Regular grid: 1-D lat(lat) and lon(lon) with standard_name."""
    ncds.createDimension("lat", 10)
    ncds.createDimension("lon", 20)
    lat = ncds.createVariable("lat", "f4", ("lat",))
    lat.standard_name = "latitude"
    lat[:] = np.linspace(-90, 90, 10)
    lon = ncds.createVariable("lon", "f4", ("lon",))
    lon.standard_name = "longitude"
    lon[:] = np.linspace(0, 360, 20)


def _build_rotated_1d(ncds):
    """Rotated-pole grid: 1-D rlat(rlat) and rlon(rlon) with grid_latitude/grid_longitude."""
    ncds.createDimension("rlat", 10)
    ncds.createDimension("rlon", 20)
    rlat = ncds.createVariable("rlat", "f4", ("rlat",))
    rlat.standard_name = "grid_latitude"
    rlat[:] = np.linspace(-20, 20, 10)
    rlon = ncds.createVariable("rlon", "f4", ("rlon",))
    rlon.standard_name = "grid_longitude"
    rlon[:] = np.linspace(-30, 30, 20)


def _build_curvilinear_2d(ncds):
    """Curvilinear grid: 2-D lat(j,i) and lon(j,i)."""
    ncds.createDimension("j", 10)
    ncds.createDimension("i", 20)
    lat = ncds.createVariable("lat", "f4", ("j", "i"))
    lat.standard_name = "latitude"
    lat[:] = np.random.rand(10, 20)
    lon = ncds.createVariable("lon", "f4", ("j", "i"))
    lon.standard_name = "longitude"
    lon[:] = np.random.rand(10, 20)


def _build_ugrid_mesh(ncds):
    """UGRID unstructured mesh: a variable with cf_role='mesh_topology'."""
    ncds.createDimension("node", 5)
    mesh = ncds.createVariable("mesh", "i4", ())
    mesh.cf_role = "mesh_topology"
    mesh.topology_dimension = 2
    # Also add lat/lon to verify UGRID takes priority
    lat = ncds.createVariable("lat", "f4", ("node",))
    lat.standard_name = "latitude"
    lat[:] = np.arange(5)
    lon = ncds.createVariable("lon", "f4", ("node",))
    lon.standard_name = "longitude"
    lon[:] = np.arange(5)


def _build_no_coordinates(ncds):
    """File with no standard_name on any variable."""
    ncds.createDimension("x", 10)
    ncds.createVariable("data", "f4", ("x",))


def _build_mixed_dimensions(ncds):
    """1-D lat but 2-D lon — should be detected as mixed/unknown."""
    ncds.createDimension("lat", 10)
    ncds.createDimension("j", 10)
    ncds.createDimension("i", 20)
    lat = ncds.createVariable("lat", "f4", ("lat",))
    lat.standard_name = "latitude"
    lat[:] = np.linspace(-90, 90, 10)
    lon = ncds.createVariable("lon", "f4", ("j", "i"))
    lon.standard_name = "longitude"
    lon[:] = np.random.rand(10, 20)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDetectGridType:

    def test_regular_1d(self, tmp_path):
        xrds, ncds = _create_and_open(tmp_path, _build_regular_1d)
        result = detect_grid_type(xrds, ncds)
        assert result.grid_type == "rectangular"
        assert result.lat_var == "lat"
        assert result.lon_var == "lon"
        ncds.close()

    def test_rotated_1d(self, tmp_path):
        xrds, ncds = _create_and_open(tmp_path, _build_rotated_1d)
        result = detect_grid_type(xrds, ncds)
        assert result.grid_type == "rectangular"
        assert result.lat_var == "rlat"
        assert result.lon_var == "rlon"
        ncds.close()

    def test_curvilinear_2d(self, tmp_path):
        xrds, ncds = _create_and_open(tmp_path, _build_curvilinear_2d)
        result = detect_grid_type(xrds, ncds)
        assert result.grid_type == "curvilinear"
        assert result.lat_var == "lat"
        assert result.lon_var == "lon"
        ncds.close()

    def test_ugrid_mesh(self, tmp_path):
        xrds, ncds = _create_and_open(tmp_path, _build_ugrid_mesh)
        result = detect_grid_type(xrds, ncds)
        assert result.grid_type == "unstructured"
        assert result.lat_var is None
        assert result.lon_var is None
        ncds.close()

    def test_no_coordinates(self, tmp_path):
        xrds, ncds = _create_and_open(tmp_path, _build_no_coordinates)
        result = detect_grid_type(xrds, ncds)
        assert result.grid_type is None
        ncds.close()

    def test_mixed_dimensions(self, tmp_path):
        xrds, ncds = _create_and_open(tmp_path, _build_mixed_dimensions)
        result = detect_grid_type(xrds, ncds)
        assert result.grid_type is None
        assert "Mixed" in result.method
        ncds.close()

    def test_ugrid_takes_priority_over_2d(self, tmp_path):
        """UGRID mesh_topology should be detected even if 2D lat/lon exist."""
        def _build(ncds):
            ncds.createDimension("j", 5)
            ncds.createDimension("i", 5)
            # 2D lat/lon that would otherwise be curvilinear
            lat = ncds.createVariable("lat", "f4", ("j", "i"))
            lat.standard_name = "latitude"
            lat[:] = np.random.rand(5, 5)
            lon = ncds.createVariable("lon", "f4", ("j", "i"))
            lon.standard_name = "longitude"
            lon[:] = np.random.rand(5, 5)
            # UGRID mesh topology
            mesh = ncds.createVariable("mesh", "i4", ())
            mesh.cf_role = "mesh_topology"
            mesh.topology_dimension = 2

        xrds, ncds = _create_and_open(tmp_path, _build)
        result = detect_grid_type(xrds, ncds)
        assert result.grid_type == "unstructured"
        ncds.close()

    def test_name_fallback_no_standard_name(self, tmp_path):
        """lat/lon without standard_name should still be detected via name fallback."""
        def _build(ncds):
            ncds.createDimension("lat", 10)
            ncds.createDimension("lon", 20)
            lat = ncds.createVariable("lat", "f4", ("lat",))
            lat[:] = np.linspace(-90, 90, 10)
            lon = ncds.createVariable("lon", "f4", ("lon",))
            lon[:] = np.linspace(0, 360, 20)

        xrds, ncds = _create_and_open(tmp_path, _build)
        result = detect_grid_type(xrds, ncds)
        assert result.grid_type == "rectangular"
        assert result.lat_var == "lat"
        assert result.lon_var == "lon"
        assert "fallback" in result.method
        ncds.close()

    def test_returns_named_tuple(self, tmp_path):
        xrds, ncds = _create_and_open(tmp_path, _build_regular_1d)
        result = detect_grid_type(xrds, ncds)
        assert isinstance(result, GridDetectionResult)
        assert isinstance(result.method, str)
        assert len(result.method) > 0
        ncds.close()
