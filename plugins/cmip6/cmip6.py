#!/usr/bin/env python
# =============================================================================
# WCRP CMIP6 project
# =============================================================================

from __future__ import annotations

import os
import re
from typing import Dict, Optional, List, Literal, Any, Tuple

import toml
from netCDF4 import Dataset
from pydantic import BaseModel, Field, model_validator

from compliance_checker.base import BaseCheck, TestCtx
from plugins.wcrp_base import WCRPBaseCheck
from checks.attribute_checks.check_attribute_suite import check_attribute_suite
from checks.variable_checks.check_variable_existence import check_variable_existence
from checks.variable_checks.check_variable_type import check_variable_type
from checks.dimension_checks.check_dimension_existence import check_dimension_existence
from checks.dimension_checks.check_dimension_positive import check_dimension_positive
from checks.dimension_checks.check_dimension_size import (
    check_dimension_size_is_equals_to,
)
from checks.variable_checks.check_bounds_value_consistency import (
    check_bounds_value_consistency,
)
from checks.consistency_checks.check_drs_filename_cv import (
    check_drs_filename,
    check_drs_directory,
)
from checks.consistency_checks.check_drs_consistency import (
    check_attributes_match_directory_structure,
    check_filename_matches_directory_structure,
)
from checks.consistency_checks.check_attributes_match_filename import (
    check_filename_vs_global_attrs,
)
from checks.consistency_checks.check_variant_label_consistency import (
    check_variant_label_consistency,
)
from checks.consistency_checks.check_frequency_table_consistency import (
    check_frequency_table_id_consistency,
)
from checks.consistency_checks.check_experiment_consistency import (
    check_experiment_consistency,
)
from checks.consistency_checks.check_institution_source_consistency import (
    check_institution_consistency,
    check_source_consistency,
)
from checks.format_checks.check_compression import check_compression
from checks.format_checks.check_format import check_format
from checks.time_checks.check_time_bounds import check_time_bounds
from checks.time_checks.check_time_range_vs_filename import check_time_range_vs_filename
from checks.time_checks.check_time_squareness import check_time_squareness

# Coordinate checks - Regular grid
from checks.coordinate_checks.check_var_existence import (
    check_lat_exists, check_lon_exists, check_lat_bnds_exists, check_lon_bnds_exists,
    check_height_exists, check_i_exists, check_j_exists,
    check_vertices_latitude_exists, check_vertices_longitude_exists,
)
from checks.coordinate_checks.check_var_type import (
    check_lat_type, check_lon_type, check_lat_bnds_type, check_lon_bnds_type,
    check_height_type, check_i_type, check_j_type,
    check_vertices_latitude_type, check_vertices_longitude_type,
)
from checks.coordinate_checks.check_var_shape import (
    check_lat_shape, check_lon_shape, check_lat_bnds_shape, check_lon_bnds_shape,
    check_i_shape, check_j_shape, check_vertices_latitude_shape, check_vertices_longitude_shape,
)
from checks.coordinate_checks.check_no_nan_inf import (
    check_lat_no_nan_inf, check_lon_no_nan_inf, check_lat_bnds_no_nan_inf, check_lon_bnds_no_nan_inf,
    check_i_no_nan_inf, check_j_no_nan_inf,
    check_vertices_latitude_no_nan_inf, check_vertices_longitude_no_nan_inf,
)
from checks.coordinate_checks.check_value_range import (
    check_lat_value_range, check_lon_value_range,
    check_lat_bnds_value_range, check_lon_bnds_value_range,
    check_vertices_latitude_value_range, check_vertices_longitude_value_range,
)
from checks.coordinate_checks.check_strictly_positive import (
    check_height_strictly_positive, check_i_strictly_positive, check_j_strictly_positive,
)
from checks.coordinate_checks.check_bounds_monotonicity import (
    check_lat_bnds_monotonicity, check_lon_bnds_monotonicity,
)
from checks.coordinate_checks.check_bounds_contiguity import (
    check_lat_bnds_contiguity, check_lon_bnds_contiguity,
)
from checks.coordinate_checks.check_values_within_bounds import (
    check_lat_values_within_bounds, check_lon_values_within_bounds,
)
from checks.coordinate_checks.check_data_within_actual_range import (
    check_lat_data_within_actual_range, check_lon_data_within_actual_range,
)
from checks.coordinate_checks.check_fill_value_equals import (
    check_vertices_latitude_missing_value, check_vertices_latitude_fill_value,
    check_vertices_longitude_missing_value, check_vertices_longitude_fill_value,
)
from checks.utils import detect_grid_type, get_cmor_coordinate_info
from checks.coordinate_checks.check_var_attributes import (
    # Height
    check_height_axis_exists, check_height_axis_type, check_height_axis_utf8, check_height_axis_value,
    check_height_standard_name_type, check_height_standard_name_utf8, check_height_standard_name_value,
    check_height_long_name_exists, check_height_long_name_type, check_height_long_name_utf8, check_height_long_name_value,
    check_height_units_type, check_height_units_utf8, check_height_positive_type, check_height_positive_utf8,
    # Lat
    check_lat_axis_type, check_lat_axis_utf8, check_lat_axis_value,
    check_lat_standard_name_type, check_lat_standard_name_utf8,
    check_lat_long_name_exists, check_lat_long_name_type, check_lat_long_name_utf8, check_lat_long_name_value,
    check_lat_units_type, check_lat_units_utf8,
    check_lat_bounds_exists, check_lat_bounds_type, check_lat_bounds_utf8,
    check_lat_actual_range_exists, check_lat_actual_range_type,
    # Lon
    check_lon_axis_type, check_lon_axis_utf8, check_lon_axis_value,
    check_lon_standard_name_type, check_lon_standard_name_utf8,
    check_lon_long_name_exists, check_lon_long_name_type, check_lon_long_name_utf8, check_lon_long_name_value,
    check_lon_units_type, check_lon_units_utf8,
    check_lon_bounds_exists, check_lon_bounds_type, check_lon_bounds_utf8,
    check_lon_actual_range_exists, check_lon_actual_range_type,
    # i/j
    check_i_units_exists, check_i_units_type, check_i_units_utf8, check_i_units_value,
    check_i_long_name_exists, check_i_long_name_type, check_i_long_name_utf8, check_i_long_name_value,
    check_j_units_exists, check_j_units_type, check_j_units_utf8, check_j_units_value,
    check_j_long_name_exists, check_j_long_name_type, check_j_long_name_utf8, check_j_long_name_value,
    # vertices
    check_vertices_latitude_units_exists, check_vertices_latitude_units_type,
    check_vertices_latitude_units_utf8, check_vertices_latitude_units_value,
    check_vertices_latitude_missing_value_exists, check_vertices_latitude_missing_value_type,
    check_vertices_latitude_fillvalue_exists, check_vertices_latitude_fillvalue_type,
    check_vertices_longitude_units_exists, check_vertices_longitude_units_type,
    check_vertices_longitude_units_utf8, check_vertices_longitude_units_value,
    check_vertices_longitude_missing_value_exists, check_vertices_longitude_missing_value_type,
    check_vertices_longitude_fillvalue_exists, check_vertices_longitude_fillvalue_type,
)


# --- CF Checker helpers ---
try:
    from compliance_checker.cf.util import (
        get_geophysical_variables,
        get_coordinate_variables,
        get_auxiliary_coordinate_variables,
    )
except ImportError as e:
    raise ImportError("Unable to import utils from compliance_checker.cf.util.") from e

# --- ESGVOC (Variable Registry) ---
try:
    from esgvoc import api as voc

    ESG_VOCAB_AVAILABLE = True
except Exception:
    ESG_VOCAB_AVAILABLE = False

try:
    from esgvoc.api.universe import find_terms_in_data_descriptor
except Exception:
    find_terms_in_data_descriptor = None


# =============================================================================
# Pydantic models
# =============================================================================

Severity = Literal["H", "M", "L"]
ValueType = Literal["str", "int", "float", "str_array"]
GridType = Literal["regular", "curvilinear", "rotated", "all"]


class SimpleCheck(BaseModel):
    severity: Severity
    grid_type: Optional[List[GridType]] = None


class AttributeRule(BaseModel):
    severity: Severity
    value_type: ValueType
    is_required: bool = True
    attribute_name: Optional[str] = None
    constraint: Optional[str] = None
    cv_source_collection: Optional[str] = None
    cv_source_collection_key: Optional[str] = None

    @model_validator(mode="after")
    def _exclusive_rules(self):
        if self.constraint and self.cv_source_collection:
            raise ValueError(
                "constraint and cv_source_collection are mutually exclusive"
            )
        return self


class FileFormatRule(BaseModel):
    severity: Severity
    expected_format: str
    expected_data_model: str


class FileCompressionRule(BaseModel):
    severity: Severity
    expected_complevel: int
    expected_shuffle: bool


class FileChecks(BaseModel):
    format: Optional[FileFormatRule] = None
    compression: Optional[FileCompressionRule] = None


class DrsChecks(BaseModel):
    filename: Optional[SimpleCheck] = None
    directory: Optional[SimpleCheck] = None
    attributes_vs_directory: Optional[SimpleCheck] = None
    filename_vs_directory: Optional[SimpleCheck] = None


class TimeSquarenessRule(BaseModel):
    severity: Severity
    calendar: str = ""
    ref_time_units: str = ""
    frequency: Dict[str, str] = Field(default_factory=dict)


class TimeSection(BaseModel):
    squareness: Optional[TimeSquarenessRule] = None


class ConsistencyChecks(BaseModel):
    variant_label: Optional[SimpleCheck] = None
    filename_vs_attributes: Optional[SimpleCheck] = None
    experiment_details: Optional[SimpleCheck] = None
    institution_details: Optional[SimpleCheck] = None
    source_details: Optional[SimpleCheck] = None
    freq_tableid: Optional[SimpleCheck] = None


class VariableAttributesSection(BaseModel):
    severity: Optional[Severity] = None
    items: Dict[str, SimpleCheck] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _split_severity_and_items(cls, values):
        if values is None or not isinstance(values, dict):
            return values
        sev = values.get("severity")
        items = {k: v for k, v in values.items() if k != "severity"}
        return {"severity": sev, "items": items}


class VariableSection(BaseModel):
    existence: Optional[SimpleCheck] = None
    type: Optional[SimpleCheck] = None
    dimensions: Optional[SimpleCheck] = None
    attributes: Optional[VariableAttributesSection] = None
    shape_bounds: Optional[SimpleCheck] = None
    bnds_vertices: Optional[SimpleCheck] = None
    time_checks: Optional[SimpleCheck] = None


class CoordinatesSection(BaseModel):
    auxiliary: Optional[SimpleCheck] = None
    bounds: Optional[SimpleCheck] = None
    properties: Optional[SimpleCheck] = None
    time: Optional[TimeSection] = None


class CMIP6Config(BaseModel):
    project_name: str
    project_version: str
    drs: Optional[DrsChecks] = None
    file: Optional[FileChecks] = None
    global_attributes: Dict[str, AttributeRule] = Field(default_factory=dict)
    variable_attributes: Optional[Dict[str, Dict[str, AttributeRule]]] = None
    variable: Optional[VariableSection] = None
    variable_checks: Optional[Dict[str, SimpleCheck]] = None
    coordinates: Optional[CoordinatesSection] = None
    consistency_checks: Optional[ConsistencyChecks] = None
    frequency_table_id_mapping: Optional[Dict[str, List[str]]] = None


# =============================================================================
# CMIP6 Project Checker
# =============================================================================


class Cmip6ProjectCheck(WCRPBaseCheck):
    _cc_spec = "wcrp_cmip6"
    _cc_spec_version = "1.0"
    _cc_description = "WCRP Project Checks"
    supported_ds = [Dataset]

    def __init__(self, options=None):
        super().__init__(options)
        self.project_name = "cmip6"
        self.config: Optional[CMIP6Config] = None
        self._geo_var_cache = None
        self._vr_expected_cache = None
        self._vr_expected_dims_cache = None
        self._grid_type_cache = None
        self._detected_coords_cache = None

        if options and "project_config_path" in options:
            self.project_config_path = options["project_config_path"]
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            self.project_config_path = os.path.join(
                this_dir, "resources", "wcrp_config.toml"
            )

    def setup(self, ds):
        super().setup(ds)
        self._load_project_config()
        self._load_mapping()
        if self.consistency_output:
            self._write_consistency_output()
        self._geo_var_cache = None
        self._vr_expected_cache = None
        self._vr_expected_dims_cache = None
        self._grid_type_cache = None
        self._detected_coords_cache = None

    def _load_project_config(self):
        if not os.path.exists(self.project_config_path):
            raise RuntimeError(f"Config not found: {self.project_config_path}")
        with open(self.project_config_path, "r", encoding="utf-8") as f:
            self.config = CMIP6Config(**toml.load(f))

    def _load_mapping(self):
        root_dir = os.path.dirname(os.path.abspath(__file__))
        path_root = os.path.join(root_dir, "mapping_variables.toml")
        config_dir = os.path.dirname(self.project_config_path)
        path_resources = os.path.join(config_dir, "mapping_variables.toml")

        path_to_use = None
        if os.path.exists(path_root):
            path_to_use = path_root
        elif os.path.exists(path_resources):
            path_to_use = path_resources

        if not path_to_use:
            print(
                f"WARNING: mapping_variables.toml not found in {root_dir} or {config_dir}"
            )
            self.variable_mapping = {}
            return

        try:
            with open(path_to_use, "r", encoding="utf-8") as f:
                data = toml.load(f)
                self.variable_mapping = data.get("mapping_variables", {})
                if not self.variable_mapping:
                    print(
                        f"WARNING: File {path_to_use} loaded but [mapping_variables] section is empty."
                    )
        except Exception as e:
            print(f"CRITICAL ERROR loading mapping {path_to_use}: {e}")
            self.variable_mapping = {}

    # --- Helpers ---
    def _get_geo_var(self, ds, severity) -> Tuple[Optional[str], List[Any]]:
        if self._geo_var_cache and self._geo_var_cache in ds.variables:
            return self._geo_var_cache, []
        results = []
        try:
            geo_vars = list(get_geophysical_variables(ds))
        except Exception as e:
            ctx = TestCtx(severity, "Geophysical Variable Detection")
            ctx.add_failure(f"Error detecting variables: {e}")
            results.append(ctx.to_result())
            return None, results

        if len(geo_vars) != 1:
            ctx = TestCtx(severity, "Geophysical Variable Detection")
            ctx.add_failure(
                f"Expected exactly 1 geophysical variable, found {len(geo_vars)}: {geo_vars}"
            )
            results.append(ctx.to_result())
            return None, results

        self._geo_var_cache = geo_vars[0]
        return self._geo_var_cache, results

    def _get_expected_from_registry(self, ds, severity):
        if self._vr_expected_cache is not None:
            return self._vr_expected_cache, self._vr_expected_dims_cache, []

        results = []

        if not ESG_VOCAB_AVAILABLE or find_terms_in_data_descriptor is None:
            return None, None, results

        try:
            variable_id = ds.getncattr("variable_id")
            table_id = ds.getncattr("table_id")
        except Exception as e:
            ctx = TestCtx(severity, "Variable Registry")
            ctx.add_failure(f"Missing required attributes for VR lookup: {e}")
            results.append(ctx.to_result())
            return None, None, results

        mapping_key = f"{table_id}.{variable_id}"
        branded = getattr(self, "variable_mapping", {}).get(mapping_key)

        if not branded:
            ctx = TestCtx(severity, "Variable Registry")
            ctx.add_failure(
                f"No mapping found for '{mapping_key}' in mapping_variables.toml"
            )
            results.append(ctx.to_result())
            return None, None, results

        fields_to_get = [
            "cf_standard_name",
            "cf_units",
            "dimensions",
            "cell_methods",
            "cell_measures",
            "description",
            "long_name",
        ]

        expected = None
        try:
            terms = find_terms_in_data_descriptor(
                expression=str(branded),
                data_descriptor_id="known_branded_variable",
                only_id=True,
                selected_term_fields=fields_to_get,
            )
            if terms:
                expected = terms[0]
        except Exception as e:
            ctx = TestCtx(severity, "Variable Registry")
            ctx.add_failure(f"Error querying ESGVOC (find_terms) for '{branded}': {e}")
            results.append(ctx.to_result())
            return None, None, results

        if not expected:
            ctx = TestCtx(severity, "Variable Registry")
            ctx.add_failure(f"Term '{branded}' not found in Variable Registry.")
            results.append(ctx.to_result())
            return None, None, results

        try:
            expected_dims = getattr(expected, "dimensions", []) or []
        except Exception:
            expected_dims = []

        self._vr_expected_cache = expected
        self._vr_expected_dims_cache = expected_dims

        return expected, expected_dims, results

    @staticmethod
    def _fuzzy_match_dim(expected, actuals):
        if expected in actuals:
            return expected
        for a in actuals:
            if a in expected or expected in a:
                return a
        return None

    def _detect_grid_type(self, ds, severity) -> Tuple[Optional[str], Dict[str, bool], List[Any]]:
        """
        Detect grid type using operation-based inspection.

        Uses standard_name attributes and coordinate dimensionality:
        - Regular: 1-D lat/lon with standard_name latitude/longitude
        - Rotated: 1-D lat/lon with standard_name grid_latitude/grid_longitude
                   (i.e. rectangular + rlat/rlon present)
        - Curvilinear: 2-D lat/lon coordinates
        - Unstructured: cf_role='mesh_topology' present
        """
        if self._grid_type_cache is not None:
            return self._grid_type_cache, self._detected_coords_cache, []

        results = []
        variables = set(ds.variables.keys())

        # Track which coordinates are present (used by downstream checks)
        detected = {
            "lat": "lat" in variables, "lon": "lon" in variables,
            "lat_bnds": "lat_bnds" in variables, "lon_bnds": "lon_bnds" in variables,
            "rlat": "rlat" in variables, "rlon": "rlon" in variables,
            "i": "i" in variables, "j": "j" in variables,
            "vertices_latitude": "vertices_latitude" in variables,
            "vertices_longitude": "vertices_longitude" in variables,
            "height": "height" in variables,
        }

        # Use operation-based detection
        detection = detect_grid_type(self.xrds, ds)

        # Map generic result to CMIP6-specific grid type
        grid_type = None
        if detection.grid_type == "rectangular":
            # Distinguish regular vs rotated: rotated has rlat/rlon
            if detected["rlat"] and detected["rlon"]:
                grid_type = "rotated"
            else:
                grid_type = "regular"
        elif detection.grid_type == "curvilinear":
            grid_type = "curvilinear"
        elif detection.grid_type == "unstructured":
            grid_type = "unstructured"

        if grid_type is None:
            if detection.lat_var is not None or detection.lon_var is not None:
                # Found some coordinates but couldn't classify — worth warning about
                ctx = TestCtx(severity, "[GRID001] Grid Type Detection")
                ctx.add_failure(
                    f"Cannot determine grid type. {detection.method}"
                )
                results.append(ctx.to_result())
            else:
                # No horizontal coordinates found — file may be a zonal mean,
                # timeseries, etc. Grid-gated checks will simply be skipped.
                print(f"[INFO] No horizontal grid detected — skipping grid-specific checks. "
                      f"({detection.method})")
        else:
            print(f"[INFO] Detected grid type: {grid_type} ({detection.method})")

        self._grid_type_cache = grid_type
        self._detected_coords_cache = detected
        return grid_type, detected, results

    def _should_run_check(self, check_name: str, ds) -> Tuple[bool, int]:
        """Check if a check should run based on config and grid type."""
        if not self.config or not self.config.variable_checks:
            return False, BaseCheck.HIGH

        check_config = self.config.variable_checks.get(check_name)
        if not check_config:
            return False, BaseCheck.HIGH

        sev = self.get_severity(check_config.severity)

        if not check_config.grid_type:
            return True, sev

        if self._grid_type_cache is None:
            self._detect_grid_type(ds, BaseCheck.HIGH)

        if self._grid_type_cache is None:
            return False, sev

        if "all" in check_config.grid_type or self._grid_type_cache in check_config.grid_type:
            return True, sev

        return False, sev

    # --- File Checks ---
    def check_File_Format(self, ds):
        if not self.config or not self.config.file or not self.config.file.format:
            return []
        r = self.config.file.format
        return check_format(
            ds, r.expected_format, r.expected_data_model, self.get_severity(r.severity)
        )

    def check_File_Compression(self, ds):
        if not self.config or not self.config.file or not self.config.file.compression:
            return []
        r = self.config.file.compression
        return check_compression(
            ds,
            None,
            r.expected_complevel,
            r.expected_shuffle,
            self.get_severity(r.severity),
        )

    def check_Drs_Vocabulary(self, ds):
        res = []
        if self.config and self.config.drs:
            if self.config.drs.filename:
                res.extend(
                    check_drs_filename(
                        ds,
                        self.get_severity(self.config.drs.filename.severity),
                        self.project_name,
                    )
                )
            if self.config.drs.directory:
                res.extend(
                    check_drs_directory(
                        ds,
                        self.get_severity(self.config.drs.directory.severity),
                        self.project_name,
                    )
                )
        return res

    # --- Attribute Checks ---
    def check_Global_Variable_Attributes(self, ds):
        res = []
        if not self.config:
            return res

        for k, r in self.config.global_attributes.items():
            res.extend(
                check_attribute_suite(
                    ds=ds,
                    attribute_name=k,
                    attribute_nc_name=r.attribute_name,
                    severity=self.get_severity(r.severity),
                    value_type=r.value_type,
                    is_required=r.is_required,
                    constraint=r.constraint,
                    cv_collection=r.cv_source_collection,
                    cv_collection_key=r.cv_source_collection_key,
                    var_name=None,
                    project_name=self.project_name,
                )
            )

        if self.config.variable_attributes:
            for v, attrs in self.config.variable_attributes.items():
                for k, r in attrs.items():
                    res.extend(
                        check_attribute_suite(
                            ds=ds,
                            attribute_name=k,
                            attribute_nc_name=r.attribute_name,
                            severity=self.get_severity(r.severity),
                            value_type=r.value_type,
                            is_required=r.is_required,
                            constraint=r.constraint,
                            cv_collection=r.cv_source_collection,
                            cv_collection_key=r.cv_source_collection_key,
                            var_name=v,
                            project_name=self.project_name,
                        )
                    )
        return res

    # --- Variable Checks ---
    def check_variable_existence(self, ds):
        res = []
        if (
            not self.config
            or not self.config.variable
            or not self.config.variable.existence
        ):
            return res
        sev = self.get_severity(self.config.variable.existence.severity)
        geo, r = self._get_geo_var(ds, sev)
        res.extend(r)
        if geo:
            res.extend(check_variable_existence(ds, geo, sev))
        return res

    def check_variable_type(self, ds):
        res = []
        if not self.config or not self.config.variable or not self.config.variable.type:
            return res
        sev = self.get_severity(self.config.variable.type.severity)
        geo, r = self._get_geo_var(ds, sev)
        res.extend(r)
        if geo:
            res.extend(check_variable_type(ds, geo, allowed_types=["f"], severity=sev))
        return res

    def check_variable_dimensions(self, ds):
        res = []
        if (
            not self.config
            or not self.config.variable
            or not self.config.variable.dimensions
        ):
            return res

        sev = self.get_severity(self.config.variable.dimensions.severity)
        geo, r = self._get_geo_var(ds, sev)
        res.extend(r)
        if not geo:
            return res

        act = list(ds.variables[geo].dimensions)
        for d in act:
            res.extend(check_dimension_existence(ds, d, sev))
            res.extend(check_dimension_positive(ds, d, sev))
            res.extend(check_variable_existence(ds, d, sev))

        exp, exp_dims, vr_r = self._get_expected_from_registry(ds, sev)
        res.extend(vr_r)

        if exp_dims:
            ctx_len = TestCtx(BaseCheck.MEDIUM, "[VAR000] Dimensions count vs VR")

            if len(act) == len(exp_dims):
                ctx_len.add_pass()
            else:
                ctx_len.add_failure(
                    f"Variable '{geo}' has {len(act)} dims {act}, "
                    f"but VR expects {len(exp_dims)} {exp_dims}. "
                    "(Note: Scalar coordinates like 'height' are often counted in VR but absent from dims)"
                )
            res.append(ctx_len.to_result())

            for ed in exp_dims:
                eds = str(ed)
                if eds in {"bnds", "axis_nbounds", "vertices", "nv4"}:
                    continue
                if self._fuzzy_match_dim(eds, act):
                    continue
                if eds.lower().startswith("height") and "height" in ds.variables:
                    continue

                res.extend(check_dimension_existence(ds, eds, sev))

        return res

    def check_variable_attributes_registry(self, ds):
        res = []
        if (
            not self.config
            or not self.config.variable
            or not self.config.variable.attributes
        ):
            return res
        d_sev = (
            self.get_severity(self.config.variable.attributes.severity)
            if self.config.variable.attributes.severity
            else BaseCheck.HIGH
        )
        geo, r = self._get_geo_var(ds, d_sev)
        res.extend(r)
        if not geo:
            return res
        exp, _, vr_r = self._get_expected_from_registry(ds, d_sev)
        res.extend(vr_r)
        if not exp:
            return res

        mapping = {
            "units": ("cf_units", "units"),
            "standard_name": ("cf_standard_name", "standard_name"),
            "cell_methods": ("cell_methods", "cell_methods"),
            "cell_measures": ("cell_measures", "cell_measures"),
            "description": ("description", "description"),
            "long_name": ("long_name", "long_name"),
        }

        for k, item in self.config.variable.attributes.items.items():
            sev = self.get_severity(item.severity) if item else d_sev
            if k in mapping:
                vr_f, nc_a = mapping[k]
                val = getattr(exp, vr_f, None)
                if val and str(val).strip():
                    res.extend(
                        check_attribute_suite(
                            ds=ds,
                            attribute_name=nc_a,
                            attribute_nc_name=None,
                            severity=sev,
                            value_type="str",
                            is_required=True,
                            constraint=re.escape(str(val).strip()),
                            cv_collection=None,
                            cv_collection_key=None,
                            var_name=geo,
                            project_name=self.project_name,
                        )
                    )
        return res

    def check_variable_bounds(self, ds):
        res = []
        if self.config and self.config.variable and self.config.variable.shape_bounds:
            sev = self.get_severity(self.config.variable.shape_bounds.severity)
            geo, r = self._get_geo_var(ds, sev)
            if geo:
                res.extend(check_bounds_value_consistency(ds, geo, sev))
        return res

    def check_variable_bnds_vertices(self, ds):
        res = []
        if self.config and self.config.variable and self.config.variable.bnds_vertices:
            sev = self.get_severity(self.config.variable.bnds_vertices.severity)
            for d, s in [("bnds", 2), ("axis_nbounds", 2), ("vertices", 4), ("nv4", 4)]:
                if d in ds.dimensions:
                    res.extend(check_dimension_size_is_equals_to(ds, d, s, sev))
        return res

    def check_variable_time_checks(self, ds):
        res = []
        if self.config and self.config.variable and self.config.variable.time_checks:
            sev = self.get_severity(self.config.variable.time_checks.severity)
            if "time" in ds.variables:
                res.extend(check_time_range_vs_filename(ds, sev))
                res.extend(check_time_bounds(ds, sev))
        return res

    # --- Coordinates Checks ---
    def check_coordinates_auxiliary(self, ds):
        res = []
        if (
            not self.config
            or not self.config.coordinates
            or not self.config.coordinates.auxiliary
        ):
            return res
        sev = self.get_severity(self.config.coordinates.auxiliary.severity)
        geo, r = self._get_geo_var(ds, sev)
        res.extend(r)
        if geo:
            try:
                for n in str(ds.variables[geo].getncattr("coordinates")).split():
                    res.extend(check_variable_existence(ds, n.strip(), sev))
            except Exception:
                pass
        return res

    def check_coordinates_bounds(self, ds):
        res = []
        if (
            not self.config
            or not self.config.coordinates
            or not self.config.coordinates.bounds
        ):
            return res
        sev = self.get_severity(self.config.coordinates.bounds.severity)
        geo, r = self._get_geo_var(ds, sev)
        if not geo:
            return res
        cand = set()
        try:
            cand.update(ds.variables[geo].dimensions)
        except (AttributeError, KeyError):
            pass
        try:
            cand.update(str(ds.variables[geo].getncattr("coordinates")).split())
        except (AttributeError, KeyError):
            pass
        for c in cand:
            if c in ds.variables and hasattr(ds.variables[c], "bounds"):
                res.extend(check_variable_existence(ds, ds.variables[c].bounds, sev))
        return res

    def check_coordinates_properties(self, ds):
        res = []
        if (
            not self.config
            or not self.config.coordinates
            or not self.config.coordinates.properties
        ):
            return res

        sev = self.get_severity(self.config.coordinates.properties.severity)

        try:
            coords_dim = get_coordinate_variables(ds)
            coords_aux = get_auxiliary_coordinate_variables(ds)
            all_coords = set(coords_dim + coords_aux)
        except Exception as e:
            ctx = TestCtx(sev, "Coordinates Discovery")
            ctx.add_failure(f"Failed to identify coordinates: {e}")
            res.append(ctx.to_result())
            return res

        for cname in all_coords:
            if cname not in ds.variables:
                continue
            var = ds.variables[cname]

            if var.dtype.kind in ["S", "U", "O"]:
                continue

            res.extend(
                check_variable_type(ds, cname, allowed_types=["f", "i"], severity=sev)
            )

            if hasattr(var, "compress") or "bnds" in cname or "bounds" in cname:
                continue

            res.extend(
                check_attribute_suite(
                    ds=ds,
                    attribute_name="units",
                    severity=sev,
                    is_required=True,
                    var_name=cname,
                    project_name=self.project_name,
                )
            )

        return res

    def check_coordinates_time_squareness(self, ds):
        res = []

        if (
            not self.config
            or not self.config.coordinates
            or not self.config.coordinates.time
            or not self.config.coordinates.time.squareness
        ):
            return res

        rule = self.config.coordinates.time.squareness
        sev = self.get_severity(rule.severity)

        res.extend(
            check_time_squareness(
                ds,
                severity=sev,
                calendar=rule.calendar or "",
                ref_time_units=rule.ref_time_units or "",
                frequency=rule.frequency or {},
            )
        )
        return res

    # --- Consistency Checks ---

    def check_consistency_drs_from_config(self, ds):
        res = []
        if not self.config or not self.config.drs:
            return res

        if self.config.drs.attributes_vs_directory:
            sev = self.get_severity(self.config.drs.attributes_vs_directory.severity)
            res.extend(
                check_attributes_match_directory_structure(ds, sev, self.project_name)
            )

        if self.config.drs.filename_vs_directory:
            sev = self.get_severity(self.config.drs.filename_vs_directory.severity)
            res.extend(
                check_filename_matches_directory_structure(ds, sev, self.project_name)
            )

        return res

    def check_consistency_filename(self, ds):
        res = []
        if (
            self.config
            and self.config.consistency_checks
            and self.config.consistency_checks.filename_vs_attributes
        ):
            sev = self.get_severity(
                self.config.consistency_checks.filename_vs_attributes.severity
            )
            res.extend(check_filename_vs_global_attrs(ds, sev))
        return res

    def check_frequency_consistency(self, ds):
        res = []
        if (
            self.config
            and self.config.consistency_checks
            and self.config.consistency_checks.freq_tableid
        ):
            sev = self.get_severity(
                self.config.consistency_checks.freq_tableid.severity
            )
            res.extend(
                check_frequency_table_id_consistency(
                    ds, self.config.frequency_table_id_mapping or {}, sev
                )
            )
        return res

    def check_experiment_consistency(self, ds):
        res = []
        if (
            self.config
            and self.config.consistency_checks
            and self.config.consistency_checks.experiment_details
        ):
            sev = self.get_severity(
                self.config.consistency_checks.experiment_details.severity
            )
            res.extend(check_experiment_consistency(ds, sev, self.project_name))
        return res

    def check_variantlabel_consistency(self, ds):
        res = []
        if (
            self.config
            and self.config.consistency_checks
            and self.config.consistency_checks.variant_label
        ):
            sev = self.get_severity(
                self.config.consistency_checks.variant_label.severity
            )
            res.extend(check_variant_label_consistency(ds, sev))
        return res

    def check_consistency_institution_source(self, ds):
        res = []
        if not self.config or not self.config.consistency_checks:
            return res
        if self.config.consistency_checks.institution_details:
            sev = self.get_severity(
                self.config.consistency_checks.institution_details.severity
            )
            res.extend(check_institution_consistency(ds, sev, self.project_name))
        if self.config.consistency_checks.source_details:
            sev = self.get_severity(
                self.config.consistency_checks.source_details.severity
            )
            res.extend(check_source_consistency(ds, sev, self.project_name))
        return res

    # =========================================================================
    # COORDINATE CHECKS - GRID TYPE DETECTION
    # =========================================================================

    def check_Grid_Type(self, ds):
        """Detect grid type and cache for subsequent coordinate checks."""
        grid_type, _, results = self._detect_grid_type(ds, BaseCheck.HIGH)
        if grid_type:
            ctx = TestCtx(BaseCheck.HIGH, "[GRID001] Grid Type Detection")
            ctx.add_pass()
            results.append(ctx.to_result())
        return results

    def check_Coordinate_Attributes_CMOR(self, ds):
        """
        Validate coordinate attributes against CMOR definitions.

        Checks standard_name, units, axis, long_name for coordinates
        based on what's defined in CMIP7_coordinate.json.
        """
        res = []
        grid_type, detected, detection_res = self._detect_grid_type(ds, BaseCheck.MEDIUM)
        res.extend(detection_res)

        if not grid_type:
            return res

        # Determine which coordinates to check based on grid type
        coords_to_check = []
        if grid_type == "regular":
            coords_to_check = ["lat", "lon"]
        elif grid_type == "rotated":
            coords_to_check = ["rlat", "rlon"]
        elif grid_type == "curvilinear":
            coords_to_check = ["i", "j"]

        for coord_name in coords_to_check:
            if coord_name not in ds.variables:
                continue

            expected = get_cmor_coordinate_info(coord_name)
            if not expected:
                continue

            var = ds.variables[coord_name]

            # Check standard_name
            if expected.get("standard_name"):
                actual = getattr(var, "standard_name", None)
                ctx = TestCtx(BaseCheck.MEDIUM, f"[CMOR] {coord_name}.standard_name")
                if actual is None:
                    ctx.add_failure(f"Missing standard_name. Expected '{expected['standard_name']}'.")
                elif str(actual).strip() != expected["standard_name"]:
                    ctx.add_failure(f"Expected '{expected['standard_name']}', got '{actual}'.")
                else:
                    ctx.add_pass()
                res.append(ctx.to_result())

            # Check units
            if expected.get("units"):
                actual = getattr(var, "units", None)
                ctx = TestCtx(BaseCheck.MEDIUM, f"[CMOR] {coord_name}.units")
                if actual is None:
                    ctx.add_failure(f"Missing units. Expected '{expected['units']}'.")
                elif str(actual).strip() != expected["units"]:
                    ctx.add_failure(f"Expected '{expected['units']}', got '{actual}'.")
                else:
                    ctx.add_pass()
                res.append(ctx.to_result())

            # Check axis
            if expected.get("axis"):
                actual = getattr(var, "axis", None)
                ctx = TestCtx(BaseCheck.LOW, f"[CMOR] {coord_name}.axis")
                if actual is None:
                    ctx.add_failure(f"Missing axis. Expected '{expected['axis']}'.")
                elif str(actual).strip() != expected["axis"]:
                    ctx.add_failure(f"Expected '{expected['axis']}', got '{actual}'.")
                else:
                    ctx.add_pass()
                res.append(ctx.to_result())

            # Check long_name (case-insensitive)
            if expected.get("long_name"):
                actual = getattr(var, "long_name", None)
                ctx = TestCtx(BaseCheck.LOW, f"[CMOR] {coord_name}.long_name")
                if actual is None:
                    ctx.add_failure(f"Missing long_name. Expected '{expected['long_name']}'.")
                elif str(actual).strip().lower() != expected["long_name"].lower():
                    ctx.add_failure(f"Expected '{expected['long_name']}', got '{actual}'.")
                else:
                    ctx.add_pass()
                res.append(ctx.to_result())

        return res

    # =========================================================================
    # COORDINATE CHECKS - HORIZONTAL REGULAR (lat, lon, lat_bnds, lon_bnds)
    # =========================================================================

    def check_Horizontal_Regular_Coords(self, ds):
        """All checks for regular grid coordinates: lat, lon, lat_bnds, lon_bnds."""
        res = []

        grid_type, detected, detection_res = self._detect_grid_type(ds, BaseCheck.HIGH)
        res.extend(detection_res)

        if grid_type != "regular":
            return res

        # LAT checks
        if detected.get("lat"):
            run, sev = self._should_run_check("check_lat_exists", ds)
            if run: res.extend(check_lat_exists(ds, sev))
            run, sev = self._should_run_check("check_lat_type", ds)
            if run: res.extend(check_lat_type(ds, sev))
            run, sev = self._should_run_check("check_lat_shape", ds)
            if run: res.extend(check_lat_shape(ds, sev))
            run, sev = self._should_run_check("check_lat_no_nan_inf", ds)
            if run: res.extend(check_lat_no_nan_inf(ds, sev))
            run, sev = self._should_run_check("check_lat_value_range", ds)
            if run: res.extend(check_lat_value_range(ds, sev))
            run, sev = self._should_run_check("check_lat_within_bounds", ds)
            if run: res.extend(check_lat_values_within_bounds(ds, sev))
            run, sev = self._should_run_check("check_lat_data_within_actual_range", ds)
            if run: res.extend(check_lat_data_within_actual_range(ds, sev))
            # Lat attributes
            run, sev = self._should_run_check("check_lat_axis_type", ds)
            if run: res.extend(check_lat_axis_type(ds, sev))
            run, sev = self._should_run_check("check_lat_axis_utf8", ds)
            if run: res.extend(check_lat_axis_utf8(ds, sev))
            run, sev = self._should_run_check("check_lat_axis_value", ds)
            if run: res.extend(check_lat_axis_value(ds, sev))
            run, sev = self._should_run_check("check_lat_units_type", ds)
            if run: res.extend(check_lat_units_type(ds, sev))
            run, sev = self._should_run_check("check_lat_units_utf8", ds)
            if run: res.extend(check_lat_units_utf8(ds, sev))
            run, sev = self._should_run_check("check_lat_long_name_exists", ds)
            if run: res.extend(check_lat_long_name_exists(ds, sev))
            run, sev = self._should_run_check("check_lat_long_name_type", ds)
            if run: res.extend(check_lat_long_name_type(ds, sev))
            run, sev = self._should_run_check("check_lat_long_name_utf8", ds)
            if run: res.extend(check_lat_long_name_utf8(ds, sev))
            run, sev = self._should_run_check("check_lat_long_name_value", ds)
            if run: res.extend(check_lat_long_name_value(ds, sev))
            run, sev = self._should_run_check("check_lat_bounds_exists", ds)
            if run: res.extend(check_lat_bounds_exists(ds, sev))
            run, sev = self._should_run_check("check_lat_bounds_type", ds)
            if run: res.extend(check_lat_bounds_type(ds, sev))
            run, sev = self._should_run_check("check_lat_bounds_utf8", ds)
            if run: res.extend(check_lat_bounds_utf8(ds, sev))

        # LON checks
        if detected.get("lon"):
            run, sev = self._should_run_check("check_lon_exists", ds)
            if run: res.extend(check_lon_exists(ds, sev))
            run, sev = self._should_run_check("check_lon_type", ds)
            if run: res.extend(check_lon_type(ds, sev))
            run, sev = self._should_run_check("check_lon_shape", ds)
            if run: res.extend(check_lon_shape(ds, sev))
            run, sev = self._should_run_check("check_lon_no_nan_inf", ds)
            if run: res.extend(check_lon_no_nan_inf(ds, sev))
            run, sev = self._should_run_check("check_lon_value_range", ds)
            if run: res.extend(check_lon_value_range(ds, sev))
            run, sev = self._should_run_check("check_lon_within_bounds", ds)
            if run: res.extend(check_lon_values_within_bounds(ds, sev))
            run, sev = self._should_run_check("check_lon_data_within_actual_range", ds)
            if run: res.extend(check_lon_data_within_actual_range(ds, sev))
            # Lon attributes
            run, sev = self._should_run_check("check_lon_axis_type", ds)
            if run: res.extend(check_lon_axis_type(ds, sev))
            run, sev = self._should_run_check("check_lon_axis_utf8", ds)
            if run: res.extend(check_lon_axis_utf8(ds, sev))
            run, sev = self._should_run_check("check_lon_axis_value", ds)
            if run: res.extend(check_lon_axis_value(ds, sev))
            run, sev = self._should_run_check("check_lon_units_type", ds)
            if run: res.extend(check_lon_units_type(ds, sev))
            run, sev = self._should_run_check("check_lon_units_utf8", ds)
            if run: res.extend(check_lon_units_utf8(ds, sev))
            run, sev = self._should_run_check("check_lon_long_name_exists", ds)
            if run: res.extend(check_lon_long_name_exists(ds, sev))
            run, sev = self._should_run_check("check_lon_long_name_type", ds)
            if run: res.extend(check_lon_long_name_type(ds, sev))
            run, sev = self._should_run_check("check_lon_long_name_utf8", ds)
            if run: res.extend(check_lon_long_name_utf8(ds, sev))
            run, sev = self._should_run_check("check_lon_long_name_value", ds)
            if run: res.extend(check_lon_long_name_value(ds, sev))
            run, sev = self._should_run_check("check_lon_bounds_exists", ds)
            if run: res.extend(check_lon_bounds_exists(ds, sev))
            run, sev = self._should_run_check("check_lon_bounds_type", ds)
            if run: res.extend(check_lon_bounds_type(ds, sev))
            run, sev = self._should_run_check("check_lon_bounds_utf8", ds)
            if run: res.extend(check_lon_bounds_utf8(ds, sev))

        # LAT_BNDS checks
        if detected.get("lat_bnds"):
            run, sev = self._should_run_check("check_lat_bnds_exists", ds)
            if run: res.extend(check_lat_bnds_exists(ds, sev))
            run, sev = self._should_run_check("check_lat_bnds_type", ds)
            if run: res.extend(check_lat_bnds_type(ds, sev))
            run, sev = self._should_run_check("check_lat_bnds_shape", ds)
            if run: res.extend(check_lat_bnds_shape(ds, sev))
            run, sev = self._should_run_check("check_lat_bnds_no_nan_inf", ds)
            if run: res.extend(check_lat_bnds_no_nan_inf(ds, sev))
            run, sev = self._should_run_check("check_lat_bnds_value_range", ds)
            if run: res.extend(check_lat_bnds_value_range(ds, sev))
            run, sev = self._should_run_check("check_lat_bnds_monotonicity", ds)
            if run: res.extend(check_lat_bnds_monotonicity(ds, sev))
            run, sev = self._should_run_check("check_lat_bnds_contiguity", ds)
            if run: res.extend(check_lat_bnds_contiguity(ds, sev))

        # LON_BNDS checks
        if detected.get("lon_bnds"):
            run, sev = self._should_run_check("check_lon_bnds_exists", ds)
            if run: res.extend(check_lon_bnds_exists(ds, sev))
            run, sev = self._should_run_check("check_lon_bnds_type", ds)
            if run: res.extend(check_lon_bnds_type(ds, sev))
            run, sev = self._should_run_check("check_lon_bnds_shape", ds)
            if run: res.extend(check_lon_bnds_shape(ds, sev))
            run, sev = self._should_run_check("check_lon_bnds_no_nan_inf", ds)
            if run: res.extend(check_lon_bnds_no_nan_inf(ds, sev))
            run, sev = self._should_run_check("check_lon_bnds_value_range", ds)
            if run: res.extend(check_lon_bnds_value_range(ds, sev))
            run, sev = self._should_run_check("check_lon_bnds_monotonicity", ds)
            if run: res.extend(check_lon_bnds_monotonicity(ds, sev))
            run, sev = self._should_run_check("check_lon_bnds_contiguity", ds)
            if run: res.extend(check_lon_bnds_contiguity(ds, sev))

        return res

    # =========================================================================
    # COORDINATE CHECKS - HORIZONTAL CURVILINEAR (i, j, vertices)
    # =========================================================================

    def check_Horizontal_Curvilinear_Coords(self, ds):
        """All checks for curvilinear grid coordinates: i, j, vertices_latitude, vertices_longitude."""
        res = []

        grid_type, detected, detection_res = self._detect_grid_type(ds, BaseCheck.HIGH)
        res.extend(detection_res)

        if grid_type != "curvilinear":
            return res

        # I checks
        if detected.get("i"):
            run, sev = self._should_run_check("check_i_exists", ds)
            if run: res.extend(check_i_exists(ds, sev))
            run, sev = self._should_run_check("check_i_type", ds)
            if run: res.extend(check_i_type(ds, sev))
            run, sev = self._should_run_check("check_i_shape", ds)
            if run: res.extend(check_i_shape(ds, sev))
            run, sev = self._should_run_check("check_i_no_nan_inf", ds)
            if run: res.extend(check_i_no_nan_inf(ds, sev))
            run, sev = self._should_run_check("check_i_strictly_positive", ds)
            if run: res.extend(check_i_strictly_positive(ds, sev))
            # I attributes
            run, sev = self._should_run_check("check_i_units_exists", ds)
            if run: res.extend(check_i_units_exists(ds, sev))
            run, sev = self._should_run_check("check_i_units_type", ds)
            if run: res.extend(check_i_units_type(ds, sev))
            run, sev = self._should_run_check("check_i_units_utf8", ds)
            if run: res.extend(check_i_units_utf8(ds, sev))
            run, sev = self._should_run_check("check_i_units_value", ds)
            if run: res.extend(check_i_units_value(ds, sev))
            run, sev = self._should_run_check("check_i_long_name_exists", ds)
            if run: res.extend(check_i_long_name_exists(ds, sev))
            run, sev = self._should_run_check("check_i_long_name_type", ds)
            if run: res.extend(check_i_long_name_type(ds, sev))
            run, sev = self._should_run_check("check_i_long_name_utf8", ds)
            if run: res.extend(check_i_long_name_utf8(ds, sev))
            run, sev = self._should_run_check("check_i_long_name_value", ds)
            if run: res.extend(check_i_long_name_value(ds, sev))

        # J checks
        if detected.get("j"):
            run, sev = self._should_run_check("check_j_exists", ds)
            if run: res.extend(check_j_exists(ds, sev))
            run, sev = self._should_run_check("check_j_type", ds)
            if run: res.extend(check_j_type(ds, sev))
            run, sev = self._should_run_check("check_j_shape", ds)
            if run: res.extend(check_j_shape(ds, sev))
            run, sev = self._should_run_check("check_j_no_nan_inf", ds)
            if run: res.extend(check_j_no_nan_inf(ds, sev))
            run, sev = self._should_run_check("check_j_strictly_positive", ds)
            if run: res.extend(check_j_strictly_positive(ds, sev))
            # J attributes
            run, sev = self._should_run_check("check_j_units_exists", ds)
            if run: res.extend(check_j_units_exists(ds, sev))
            run, sev = self._should_run_check("check_j_units_type", ds)
            if run: res.extend(check_j_units_type(ds, sev))
            run, sev = self._should_run_check("check_j_units_utf8", ds)
            if run: res.extend(check_j_units_utf8(ds, sev))
            run, sev = self._should_run_check("check_j_units_value", ds)
            if run: res.extend(check_j_units_value(ds, sev))
            run, sev = self._should_run_check("check_j_long_name_exists", ds)
            if run: res.extend(check_j_long_name_exists(ds, sev))
            run, sev = self._should_run_check("check_j_long_name_type", ds)
            if run: res.extend(check_j_long_name_type(ds, sev))
            run, sev = self._should_run_check("check_j_long_name_utf8", ds)
            if run: res.extend(check_j_long_name_utf8(ds, sev))
            run, sev = self._should_run_check("check_j_long_name_value", ds)
            if run: res.extend(check_j_long_name_value(ds, sev))

        # VERTICES_LATITUDE checks
        if detected.get("vertices_latitude"):
            run, sev = self._should_run_check("check_vertices_latitude_exists", ds)
            if run: res.extend(check_vertices_latitude_exists(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_type", ds)
            if run: res.extend(check_vertices_latitude_type(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_shape", ds)
            if run: res.extend(check_vertices_latitude_shape(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_no_nan_inf", ds)
            if run: res.extend(check_vertices_latitude_no_nan_inf(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_value_range", ds)
            if run: res.extend(check_vertices_latitude_value_range(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_missing_value", ds)
            if run: res.extend(check_vertices_latitude_missing_value(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_fill_value", ds)
            if run: res.extend(check_vertices_latitude_fill_value(ds, sev))
            # Vertices_latitude attributes
            run, sev = self._should_run_check("check_vertices_latitude_units_exists", ds)
            if run: res.extend(check_vertices_latitude_units_exists(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_units_type", ds)
            if run: res.extend(check_vertices_latitude_units_type(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_units_utf8", ds)
            if run: res.extend(check_vertices_latitude_units_utf8(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_units_value", ds)
            if run: res.extend(check_vertices_latitude_units_value(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_missing_value_exists", ds)
            if run: res.extend(check_vertices_latitude_missing_value_exists(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_missing_value_type", ds)
            if run: res.extend(check_vertices_latitude_missing_value_type(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_fillvalue_exists", ds)
            if run: res.extend(check_vertices_latitude_fillvalue_exists(ds, sev))
            run, sev = self._should_run_check("check_vertices_latitude_fillvalue_type", ds)
            if run: res.extend(check_vertices_latitude_fillvalue_type(ds, sev))

        # VERTICES_LONGITUDE checks
        if detected.get("vertices_longitude"):
            run, sev = self._should_run_check("check_vertices_longitude_exists", ds)
            if run: res.extend(check_vertices_longitude_exists(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_type", ds)
            if run: res.extend(check_vertices_longitude_type(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_shape", ds)
            if run: res.extend(check_vertices_longitude_shape(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_no_nan_inf", ds)
            if run: res.extend(check_vertices_longitude_no_nan_inf(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_value_range", ds)
            if run: res.extend(check_vertices_longitude_value_range(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_missing_value", ds)
            if run: res.extend(check_vertices_longitude_missing_value(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_fill_value", ds)
            if run: res.extend(check_vertices_longitude_fill_value(ds, sev))
            # Vertices_longitude attributes
            run, sev = self._should_run_check("check_vertices_longitude_units_exists", ds)
            if run: res.extend(check_vertices_longitude_units_exists(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_units_type", ds)
            if run: res.extend(check_vertices_longitude_units_type(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_units_utf8", ds)
            if run: res.extend(check_vertices_longitude_units_utf8(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_units_value", ds)
            if run: res.extend(check_vertices_longitude_units_value(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_missing_value_exists", ds)
            if run: res.extend(check_vertices_longitude_missing_value_exists(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_missing_value_type", ds)
            if run: res.extend(check_vertices_longitude_missing_value_type(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_fillvalue_exists", ds)
            if run: res.extend(check_vertices_longitude_fillvalue_exists(ds, sev))
            run, sev = self._should_run_check("check_vertices_longitude_fillvalue_type", ds)
            if run: res.extend(check_vertices_longitude_fillvalue_type(ds, sev))

        return res

    # =========================================================================
    # COORDINATE CHECKS - VERTICAL (height)
    # =========================================================================

    def check_Vertical_Coords(self, ds):
        """All checks for vertical coordinates: height."""
        res = []

        _, detected, detection_res = self._detect_grid_type(ds, BaseCheck.HIGH)
        res.extend(detection_res)

        if not detected.get("height"):
            return res

        # HEIGHT checks
        run, sev = self._should_run_check("check_height_exists", ds)
        if run: res.extend(check_height_exists(ds, sev))
        run, sev = self._should_run_check("check_height_type", ds)
        if run: res.extend(check_height_type(ds, sev))
        run, sev = self._should_run_check("check_height_strictly_positive", ds)
        if run: res.extend(check_height_strictly_positive(ds, sev))
        # Height attributes
        run, sev = self._should_run_check("check_height_axis_exists", ds)
        if run: res.extend(check_height_axis_exists(ds, sev))
        run, sev = self._should_run_check("check_height_axis_type", ds)
        if run: res.extend(check_height_axis_type(ds, sev))
        run, sev = self._should_run_check("check_height_axis_utf8", ds)
        if run: res.extend(check_height_axis_utf8(ds, sev))
        run, sev = self._should_run_check("check_height_axis_value", ds)
        if run: res.extend(check_height_axis_value(ds, sev))
        run, sev = self._should_run_check("check_height_standard_name_type", ds)
        if run: res.extend(check_height_standard_name_type(ds, sev))
        run, sev = self._should_run_check("check_height_standard_name_utf8", ds)
        if run: res.extend(check_height_standard_name_utf8(ds, sev))
        run, sev = self._should_run_check("check_height_standard_name_value", ds)
        if run: res.extend(check_height_standard_name_value(ds, sev))
        run, sev = self._should_run_check("check_height_long_name_exists", ds)
        if run: res.extend(check_height_long_name_exists(ds, sev))
        run, sev = self._should_run_check("check_height_long_name_type", ds)
        if run: res.extend(check_height_long_name_type(ds, sev))
        run, sev = self._should_run_check("check_height_long_name_utf8", ds)
        if run: res.extend(check_height_long_name_utf8(ds, sev))
        run, sev = self._should_run_check("check_height_long_name_value", ds)
        if run: res.extend(check_height_long_name_value(ds, sev))
        run, sev = self._should_run_check("check_height_units_type", ds)
        if run: res.extend(check_height_units_type(ds, sev))
        run, sev = self._should_run_check("check_height_units_utf8", ds)
        if run: res.extend(check_height_units_utf8(ds, sev))
        run, sev = self._should_run_check("check_height_positive_type", ds)
        if run: res.extend(check_height_positive_type(ds, sev))
        run, sev = self._should_run_check("check_height_positive_utf8", ds)
        if run: res.extend(check_height_positive_utf8(ds, sev))

        return res
