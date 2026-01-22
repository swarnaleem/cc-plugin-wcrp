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
from checks.variable_checks.check_variable_shape_vs_dimensions import (
    check_variable_shape,
)
from checks.data_plausibility_checks.check_nan_inf import check_nan_inf
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
from checks.variable_checks.check_value_range import (
    check_lat_value_range,
    check_lon_value_range,
    check_lat_bnds_value_range,
    check_lon_bnds_value_range,
    check_vertices_latitude_value_range,
    check_vertices_longitude_value_range,
)
from checks.variable_checks.check_strictly_positive import (
    check_height_strictly_positive,
    check_i_strictly_positive,
    check_j_strictly_positive,
)
from checks.variable_checks.check_bounds_monotonicity import (
    check_lat_bnds_monotonicity,
    check_lon_bnds_monotonicity,
)
from checks.variable_checks.check_bounds_contiguity import (
    check_lat_bnds_contiguity,
    check_lon_bnds_contiguity,
)
from checks.variable_checks.check_data_within_actual_range import (
    check_lat_data_within_actual_range,
    check_lon_data_within_actual_range,
)
from checks.variable_checks.check_fill_value_equals import (
    check_vertices_latitude_missing_value,
    check_vertices_latitude_fill_value,
    check_vertices_longitude_missing_value,
    check_vertices_longitude_fill_value,
)
from checks.variable_checks.check_var_existence import (
    check_lat_exists,
    check_lon_exists,
    check_height_exists,
    check_lat_bnds_exists,
    check_lon_bnds_exists,
    check_i_exists,
    check_j_exists,
    check_vertices_latitude_exists,
    check_vertices_longitude_exists,
)
from checks.variable_checks.check_var_type import (
    check_lat_type,
    check_lon_type,
    check_height_type,
    check_lat_bnds_type,
    check_lon_bnds_type,
    check_i_type,
    check_j_type,
    check_vertices_latitude_type,
    check_vertices_longitude_type,
)
from checks.variable_checks.check_var_shape import (
    check_lat_shape,
    check_lon_shape,
    check_lat_bnds_shape,
    check_lon_bnds_shape,
    check_i_shape,
    check_j_shape,
    check_vertices_latitude_shape,
    check_vertices_longitude_shape,
)
from checks.variable_checks.check_no_nan_inf import (
    check_lat_no_nan_inf,
    check_lon_no_nan_inf,
    check_lat_bnds_no_nan_inf,
    check_lon_bnds_no_nan_inf,
    check_i_no_nan_inf,
    check_j_no_nan_inf,
    check_vertices_latitude_no_nan_inf,
    check_vertices_longitude_no_nan_inf,
)
from checks.variable_checks.check_values_within_bounds import (
    check_lat_values_within_bounds,
    check_lon_values_within_bounds,
)
from checks.variable_checks.check_var_attributes import (
    # Height attribute checks
    check_height_axis_exists,
    check_height_axis_type,
    check_height_axis_utf8,
    check_height_axis_value,
    check_height_standard_name_type,
    check_height_standard_name_utf8,
    check_height_standard_name_value,
    check_height_long_name_exists,
    check_height_long_name_type,
    check_height_long_name_utf8,
    check_height_long_name_value,
    check_height_units_type,
    check_height_units_utf8,
    check_height_positive_type,
    check_height_positive_utf8,
    # Lat attribute checks
    check_lat_axis_type,
    check_lat_axis_utf8,
    check_lat_axis_value,
    check_lat_standard_name_type,
    check_lat_standard_name_utf8,
    check_lat_long_name_exists,
    check_lat_long_name_type,
    check_lat_long_name_utf8,
    check_lat_long_name_value,
    check_lat_units_type,
    check_lat_units_utf8,
    check_lat_bounds_exists,
    check_lat_bounds_type,
    check_lat_bounds_utf8,
    check_lat_actual_range_exists,
    check_lat_actual_range_type,
    # Lon attribute checks
    check_lon_axis_type,
    check_lon_axis_utf8,
    check_lon_axis_value,
    check_lon_standard_name_type,
    check_lon_standard_name_utf8,
    check_lon_long_name_exists,
    check_lon_long_name_type,
    check_lon_long_name_utf8,
    check_lon_long_name_value,
    check_lon_units_type,
    check_lon_units_utf8,
    check_lon_bounds_exists,
    check_lon_bounds_type,
    check_lon_bounds_utf8,
    check_lon_actual_range_exists,
    check_lon_actual_range_type,
    # i attribute checks
    check_i_units_exists,
    check_i_units_type,
    check_i_units_utf8,
    check_i_units_value,
    check_i_long_name_exists,
    check_i_long_name_type,
    check_i_long_name_utf8,
    check_i_long_name_value,
    # j attribute checks
    check_j_units_exists,
    check_j_units_type,
    check_j_units_utf8,
    check_j_units_value,
    check_j_long_name_exists,
    check_j_long_name_type,
    check_j_long_name_utf8,
    check_j_long_name_value,
    # vertices_latitude attribute checks
    check_vertices_latitude_units_exists,
    check_vertices_latitude_units_type,
    check_vertices_latitude_units_utf8,
    check_vertices_latitude_units_value,
    check_vertices_latitude_missing_value_exists,
    check_vertices_latitude_missing_value_type,
    check_vertices_latitude_fillvalue_exists,
    check_vertices_latitude_fillvalue_type,
    # vertices_longitude attribute checks
    check_vertices_longitude_units_exists,
    check_vertices_longitude_units_type,
    check_vertices_longitude_units_utf8,
    check_vertices_longitude_units_value,
    check_vertices_longitude_missing_value_exists,
    check_vertices_longitude_missing_value_type,
    check_vertices_longitude_fillvalue_exists,
    check_vertices_longitude_fillvalue_type,
)


# --- CF Checker helpers ---
try:
    from compliance_checker.cf.util import (
        get_geophysical_variables,
        get_coordinate_variables,  # To find lat(lat), lon(lon), time(time)
        get_auxiliary_coordinate_variables,  # To find height, etc.
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


class SimpleCheck(BaseModel):
    severity: Severity


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
    attributes_vs_directory: Optional[SimpleCheck] = None  # PATH001
    filename_vs_directory: Optional[SimpleCheck] = None  # PATH002


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

    def _load_project_config(self):
        if not os.path.exists(self.project_config_path):
            raise RuntimeError(f"Config not found: {self.project_config_path}")
        with open(self.project_config_path, "r", encoding="utf-8") as f:
            self.config = CMIP6Config(**toml.load(f))

    def _load_mapping(self):
        """
        Load the mapping file by searching in two locations:
        1. Root directory (where cmip6.py is located)
        2. Resources directory
        """
        # 1. Search in root directory
        root_dir = os.path.dirname(os.path.abspath(__file__))
        path_root = os.path.join(root_dir, "mapping_variables.toml")

        # 2. Search in resources directory
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
            # If library is missing, we just return empty
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

        # Extract dimensions
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

        # 1. Global Attributes
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
            # For geophysical variable, we expect strict float ('f')
            res.extend(check_variable_type(ds, geo, allowed_types=["f"], severity=sev))
        return res

    def check_variable_dimensions(self, ds):
        """
        [variable.dimensions]
        Checks existence of dimensions and compares with Variable Registry.
        """
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

        # 1. Checks on actual dimensions
        act = list(ds.variables[geo].dimensions)
        for d in act:
            res.extend(check_dimension_existence(ds, d, sev))
            res.extend(check_dimension_positive(ds, d, sev))
            res.extend(check_variable_existence(ds, d, sev))

        # 2. Comparison with Variable Registry (VR)
        exp, exp_dims, vr_r = self._get_expected_from_registry(ds, sev)
        res.extend(vr_r)

        if exp_dims:
            # --- VAR000: Count comparison ---
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
            # --------------------------------------

            # 3. Fuzzy Match of names
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
                    # Explicit format
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
        """
        Checks type (float/int) and units for all coordinate variables.
        """
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

            # Skip string labels
            if var.dtype.kind in ["S", "U", "O"]:
                continue

            # Check Type (allow float or int)
            res.extend(
                check_variable_type(ds, cname, allowed_types=["f", "i"], severity=sev)
            )

            # Skip technical variables for units check
            if hasattr(var, "compress") or "bnds" in cname or "bounds" in cname:
                continue

            # Check Units
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

        # 1. Check PATH001
        if self.config.drs.attributes_vs_directory:
            sev = self.get_severity(self.config.drs.attributes_vs_directory.severity)
            res.extend(
                check_attributes_match_directory_structure(ds, sev, self.project_name)
            )

        # 2. Check PATH002
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

    # --- Variable Value Checks ---

    def check_lat_value_range(self, ds):
        """[V036] Check lat values are within -90 to 90 degrees."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_value_range")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_value_range(ds, sev))
        return res

    def check_lon_value_range(self, ds):
        """[V074] Check lon values are within 0 to 360 degrees."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_value_range")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_value_range(ds, sev))
        return res

    def check_lat_bnds_value_range(self, ds):
        """[V044] Check lat_bnds values are within -90 to 90 degrees."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_bnds_value_range")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_bnds_value_range(ds, sev))
        return res

    def check_lon_bnds_value_range(self, ds):
        """[V082] Check lon_bnds values are within 0 to 360 degrees."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_bnds_value_range")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_bnds_value_range(ds, sev))
        return res

    def check_vertices_latitude_value_range(self, ds):
        """[V222] Check vertices_latitude values are within -90 to 90 degrees."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_value_range")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_latitude_value_range(ds, sev))
        return res

    def check_vertices_longitude_value_range(self, ds):
        """[V227] Check vertices_longitude values are within 0 to 360 degrees."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_value_range")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_longitude_value_range(ds, sev))
        return res

    def check_height_strictly_positive(self, ds):
        """[V003] Check height values are strictly positive."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_strictly_positive")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_strictly_positive(ds, sev))
        return res

    def check_i_strictly_positive(self, ds):
        """[V208] Check i values are strictly positive."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_strictly_positive")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_i_strictly_positive(ds, sev))
        return res

    def check_j_strictly_positive(self, ds):
        """[V215] Check j values are strictly positive."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_strictly_positive")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_j_strictly_positive(ds, sev))
        return res

    def check_lat_bnds_monotonicity(self, ds):
        """[V042] Check lat_bnds values are monotonically non-decreasing."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_bnds_monotonicity")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_bnds_monotonicity(ds, sev))
        return res

    def check_lon_bnds_monotonicity(self, ds):
        """[V080] Check lon_bnds values are monotonically non-decreasing."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_bnds_monotonicity")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_bnds_monotonicity(ds, sev))
        return res

    def check_lat_bnds_contiguity(self, ds):
        """[V043] Check lat_bnds intervals have no gaps or overlaps."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_bnds_contiguity")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_bnds_contiguity(ds, sev))
        return res

    def check_lon_bnds_contiguity(self, ds):
        """[V081] Check lon_bnds intervals have no gaps or overlaps."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_bnds_contiguity")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_bnds_contiguity(ds, sev))
        return res

    def check_lat_data_within_actual_range(self, ds):
        """[V067] Check lat data falls within declared actual_range."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_data_within_actual_range")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_data_within_actual_range(ds, sev))
        return res

    def check_lon_data_within_actual_range(self, ds):
        """[V105] Check lon data falls within declared actual_range."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_data_within_actual_range")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_data_within_actual_range(ds, sev))
        return res

    def check_vertices_latitude_missing_value(self, ds):
        """[V250] Check vertices_latitude missing_value equals 1.e+20."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_missing_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_latitude_missing_value(ds, sev))
        return res

    def check_vertices_latitude_fill_value(self, ds):
        """[V253] Check vertices_latitude _FillValue equals 1.e+20."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_fill_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_latitude_fill_value(ds, sev))
        return res

    def check_vertices_longitude_missing_value(self, ds):
        """[V260] Check vertices_longitude missing_value equals 1.e+20."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_missing_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_longitude_missing_value(ds, sev))
        return res

    def check_vertices_longitude_fill_value(self, ds):
        """[V263] Check vertices_longitude _FillValue equals 1.e+20."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_fill_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_longitude_fill_value(ds, sev))
        return res

    # --- Variable Existence Checks ---

    def check_height_exists_v(self, ds):
        """[V001] Check height variable exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_existence(ds, "height", sev))
        return res

    def check_lat_exists_v(self, ds):
        """[V030] Check lat variable exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_existence(ds, "lat", sev))
        return res

    def check_lat_bnds_exists_v(self, ds):
        """[V038] Check lat_bnds variable exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_bnds_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_existence(ds, "lat_bnds", sev))
        return res

    def check_lon_exists_v(self, ds):
        """[V068] Check lon variable exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_existence(ds, "lon", sev))
        return res

    def check_lon_bnds_exists_v(self, ds):
        """[V076] Check lon_bnds variable exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_bnds_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_existence(ds, "lon_bnds", sev))
        return res

    def check_i_exists_v(self, ds):
        """[V204] Check i variable exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_existence(ds, "i", sev))
        return res

    def check_j_exists_v(self, ds):
        """[V211] Check j variable exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_existence(ds, "j", sev))
        return res

    def check_vertices_latitude_exists_v(self, ds):
        """[V218] Check vertices_latitude variable exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_existence(ds, "vertices_latitude", sev))
        return res

    def check_vertices_longitude_exists_v(self, ds):
        """[V223] Check vertices_longitude variable exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_existence(ds, "vertices_longitude", sev))
        return res

    # --- Variable Type Checks ---

    def check_height_type_v(self, ds):
        """[V002] Check height variable type is NC_DOUBLE (float)."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_type(ds, "height", allowed_types=["f"], severity=sev))
        return res

    def check_lat_type_v(self, ds):
        """[V031] Check lat variable type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_type(ds, "lat", allowed_types=["f"], severity=sev))
        return res

    def check_lat_bnds_type_v(self, ds):
        """[V039] Check lat_bnds variable type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_bnds_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_type(ds, "lat_bnds", allowed_types=["f"], severity=sev))
        return res

    def check_lon_type_v(self, ds):
        """[V069] Check lon variable type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_type(ds, "lon", allowed_types=["f"], severity=sev))
        return res

    def check_lon_bnds_type_v(self, ds):
        """[V077] Check lon_bnds variable type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_bnds_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_type(ds, "lon_bnds", allowed_types=["f"], severity=sev))
        return res

    def check_i_type_v(self, ds):
        """[V205] Check i variable type is NC_INT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_type(ds, "i", allowed_types=["i"], severity=sev))
        return res

    def check_j_type_v(self, ds):
        """[V212] Check j variable type is NC_INT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_type(ds, "j", allowed_types=["i"], severity=sev))
        return res

    def check_vertices_latitude_type_v(self, ds):
        """[V219] Check vertices_latitude variable type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_type(ds, "vertices_latitude", allowed_types=["f"], severity=sev))
        return res

    def check_vertices_longitude_type_v(self, ds):
        """[V224] Check vertices_longitude variable type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_type(ds, "vertices_longitude", allowed_types=["f"], severity=sev))
        return res

    # --- Variable Shape Checks ---

    def check_lat_shape_v(self, ds):
        """[V032] Check lat shape aligns with lat dimension."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_shape")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_shape("lat", ds, sev))
        return res

    def check_lat_bnds_shape_v(self, ds):
        """[V040] Check lat_bnds shape aligns with dimensions."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_bnds_shape")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_shape("lat_bnds", ds, sev))
        return res

    def check_lon_shape_v(self, ds):
        """[V070] Check lon shape aligns with lon dimension."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_shape")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_shape("lon", ds, sev))
        return res

    def check_lon_bnds_shape_v(self, ds):
        """[V078] Check lon_bnds shape aligns with dimensions."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_bnds_shape")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_shape("lon_bnds", ds, sev))
        return res

    def check_i_shape_v(self, ds):
        """[V206] Check i shape aligns with i dimension."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_shape")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_shape("i", ds, sev))
        return res

    def check_j_shape_v(self, ds):
        """[V213] Check j shape aligns with j dimension."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_shape")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_shape("j", ds, sev))
        return res

    def check_vertices_latitude_shape_v(self, ds):
        """[V220] Check vertices_latitude shape aligns with dimensions."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_shape")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_shape("vertices_latitude", ds, sev))
        return res

    def check_vertices_longitude_shape_v(self, ds):
        """[V225] Check vertices_longitude shape aligns with dimensions."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_shape")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_variable_shape("vertices_longitude", ds, sev))
        return res

    # --- No NaN/Inf/Missing Checks ---

    def check_lat_no_nan_inf_v(self, ds):
        """[V033] Check lat has no missing, Inf, or NaN values."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_no_nan_inf")
        if check_config:
            sev = self.get_severity(check_config.severity)
            if "lat" in ds.variables:
                ctx = check_nan_inf(ds, "lat", parameter="NaN", severity=sev)
                res.append(ctx.to_result())
                ctx = check_nan_inf(ds, "lat", parameter="Inf", severity=sev)
                res.append(ctx.to_result())
        return res

    def check_lat_bnds_no_nan_inf_v(self, ds):
        """[V041] Check lat_bnds has no missing, Inf, or NaN values."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_bnds_no_nan_inf")
        if check_config:
            sev = self.get_severity(check_config.severity)
            if "lat_bnds" in ds.variables:
                ctx = check_nan_inf(ds, "lat_bnds", parameter="NaN", severity=sev)
                res.append(ctx.to_result())
                ctx = check_nan_inf(ds, "lat_bnds", parameter="Inf", severity=sev)
                res.append(ctx.to_result())
        return res

    def check_lon_no_nan_inf_v(self, ds):
        """[V071] Check lon has no missing, Inf, or NaN values."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_no_nan_inf")
        if check_config:
            sev = self.get_severity(check_config.severity)
            if "lon" in ds.variables:
                ctx = check_nan_inf(ds, "lon", parameter="NaN", severity=sev)
                res.append(ctx.to_result())
                ctx = check_nan_inf(ds, "lon", parameter="Inf", severity=sev)
                res.append(ctx.to_result())
        return res

    def check_lon_bnds_no_nan_inf_v(self, ds):
        """[V079] Check lon_bnds has no missing, Inf, or NaN values."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_bnds_no_nan_inf")
        if check_config:
            sev = self.get_severity(check_config.severity)
            if "lon_bnds" in ds.variables:
                ctx = check_nan_inf(ds, "lon_bnds", parameter="NaN", severity=sev)
                res.append(ctx.to_result())
                ctx = check_nan_inf(ds, "lon_bnds", parameter="Inf", severity=sev)
                res.append(ctx.to_result())
        return res

    def check_i_no_nan_inf_v(self, ds):
        """[V207] Check i has no missing, Inf, or NaN values."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_no_nan_inf")
        if check_config:
            sev = self.get_severity(check_config.severity)
            if "i" in ds.variables:
                ctx = check_nan_inf(ds, "i", parameter="NaN", severity=sev)
                res.append(ctx.to_result())
                ctx = check_nan_inf(ds, "i", parameter="Inf", severity=sev)
                res.append(ctx.to_result())
        return res

    def check_j_no_nan_inf_v(self, ds):
        """[V214] Check j has no missing, Inf, or NaN values."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_no_nan_inf")
        if check_config:
            sev = self.get_severity(check_config.severity)
            if "j" in ds.variables:
                ctx = check_nan_inf(ds, "j", parameter="NaN", severity=sev)
                res.append(ctx.to_result())
                ctx = check_nan_inf(ds, "j", parameter="Inf", severity=sev)
                res.append(ctx.to_result())
        return res

    def check_vertices_latitude_no_nan_inf_v(self, ds):
        """[V221] Check vertices_latitude has no missing, Inf, or NaN values."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_no_nan_inf")
        if check_config:
            sev = self.get_severity(check_config.severity)
            if "vertices_latitude" in ds.variables:
                ctx = check_nan_inf(ds, "vertices_latitude", parameter="NaN", severity=sev)
                res.append(ctx.to_result())
                ctx = check_nan_inf(ds, "vertices_latitude", parameter="Inf", severity=sev)
                res.append(ctx.to_result())
        return res

    def check_vertices_longitude_no_nan_inf_v(self, ds):
        """[V226] Check vertices_longitude has no missing, Inf, or NaN values."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_no_nan_inf")
        if check_config:
            sev = self.get_severity(check_config.severity)
            if "vertices_longitude" in ds.variables:
                ctx = check_nan_inf(ds, "vertices_longitude", parameter="NaN", severity=sev)
                res.append(ctx.to_result())
                ctx = check_nan_inf(ds, "vertices_longitude", parameter="Inf", severity=sev)
                res.append(ctx.to_result())
        return res

    # --- Values Within Bounds Checks ---

    def check_lat_within_bounds_v(self, ds):
        """[V037] Check lat values lie within lat_bnds range."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_within_bounds")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_bounds_value_consistency(ds, "lat", sev))
        return res

    def check_lon_within_bounds_v(self, ds):
        """[V075] Check lon values lie within lon_bnds range."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_within_bounds")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_bounds_value_consistency(ds, "lon", sev))
        return res

    # ===========================================================================
    # HEIGHT ATTRIBUTE CHECKS
    # ===========================================================================

    def check_height_axis_exists_v(self, ds):
        """[V004] Check height.axis attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_axis_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_axis_exists(ds, sev))
        return res

    def check_height_axis_type_v(self, ds):
        """[V005] Check height.axis attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_axis_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_axis_type(ds, sev))
        return res

    def check_height_axis_utf8_v(self, ds):
        """[V006] Check height.axis attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_axis_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_axis_utf8(ds, sev))
        return res

    def check_height_axis_value_v(self, ds):
        """[V007] Check height.axis attribute value equals 'Z'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_axis_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_axis_value(ds, sev))
        return res

    def check_height_standard_name_type_v(self, ds):
        """[V009] Check height.standard_name attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_standard_name_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_standard_name_type(ds, sev))
        return res

    def check_height_standard_name_utf8_v(self, ds):
        """[V010] Check height.standard_name attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_standard_name_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_standard_name_utf8(ds, sev))
        return res

    def check_height_standard_name_value_v(self, ds):
        """[V011] Check height.standard_name attribute value equals 'height'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_standard_name_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_standard_name_value(ds, sev))
        return res

    def check_height_long_name_exists_v(self, ds):
        """[V012] Check height.long_name attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_long_name_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_long_name_exists(ds, sev))
        return res

    def check_height_long_name_type_v(self, ds):
        """[V013] Check height.long_name attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_long_name_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_long_name_type(ds, sev))
        return res

    def check_height_long_name_utf8_v(self, ds):
        """[V014] Check height.long_name attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_long_name_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_long_name_utf8(ds, sev))
        return res

    def check_height_long_name_value_v(self, ds):
        """[V015] Check height.long_name attribute value equals 'height'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_long_name_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_long_name_value(ds, sev))
        return res

    def check_height_units_type_v(self, ds):
        """[V017] Check height.units attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_units_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_units_type(ds, sev))
        return res

    def check_height_units_utf8_v(self, ds):
        """[V018] Check height.units attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_units_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_units_utf8(ds, sev))
        return res

    def check_height_positive_type_v(self, ds):
        """[V021] Check height.positive attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_positive_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_positive_type(ds, sev))
        return res

    def check_height_positive_utf8_v(self, ds):
        """[V022] Check height.positive attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_height_positive_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_height_positive_utf8(ds, sev))
        return res

    # ===========================================================================
    # LAT ATTRIBUTE CHECKS
    # ===========================================================================

    def check_lat_axis_type_v(self, ds):
        """[V046] Check lat.axis attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_axis_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_axis_type(ds, sev))
        return res

    def check_lat_axis_utf8_v(self, ds):
        """[V047] Check lat.axis attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_axis_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_axis_utf8(ds, sev))
        return res

    def check_lat_axis_value_v(self, ds):
        """[V048] Check lat.axis attribute value equals 'Y'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_axis_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_axis_value(ds, sev))
        return res

    def check_lat_standard_name_type_v(self, ds):
        """[V050] Check lat.standard_name attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_standard_name_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_standard_name_type(ds, sev))
        return res

    def check_lat_standard_name_utf8_v(self, ds):
        """[V051] Check lat.standard_name attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_standard_name_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_standard_name_utf8(ds, sev))
        return res

    def check_lat_long_name_exists_v(self, ds):
        """[V053] Check lat.long_name attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_long_name_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_long_name_exists(ds, sev))
        return res

    def check_lat_long_name_type_v(self, ds):
        """[V054] Check lat.long_name attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_long_name_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_long_name_type(ds, sev))
        return res

    def check_lat_long_name_utf8_v(self, ds):
        """[V055] Check lat.long_name attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_long_name_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_long_name_utf8(ds, sev))
        return res

    def check_lat_long_name_value_v(self, ds):
        """[V056] Check lat.long_name attribute value equals 'latitude'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_long_name_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_long_name_value(ds, sev))
        return res

    def check_lat_units_type_v(self, ds):
        """[V058] Check lat.units attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_units_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_units_type(ds, sev))
        return res

    def check_lat_units_utf8_v(self, ds):
        """[V059] Check lat.units attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_units_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_units_utf8(ds, sev))
        return res

    def check_lat_bounds_exists_v(self, ds):
        """[V061] Check lat.bounds attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_bounds_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_bounds_exists(ds, sev))
        return res

    def check_lat_bounds_type_v(self, ds):
        """[V062] Check lat.bounds attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_bounds_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_bounds_type(ds, sev))
        return res

    def check_lat_bounds_utf8_v(self, ds):
        """[V063] Check lat.bounds attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_bounds_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_bounds_utf8(ds, sev))
        return res

    def check_lat_actual_range_exists_v(self, ds):
        """[V065] Check lat.actual_range attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_actual_range_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_actual_range_exists(ds, sev))
        return res

    def check_lat_actual_range_type_v(self, ds):
        """[V066] Check lat.actual_range attribute type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lat_actual_range_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lat_actual_range_type(ds, sev))
        return res

    # ===========================================================================
    # LON ATTRIBUTE CHECKS
    # ===========================================================================

    def check_lon_axis_type_v(self, ds):
        """[V084] Check lon.axis attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_axis_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_axis_type(ds, sev))
        return res

    def check_lon_axis_utf8_v(self, ds):
        """[V085] Check lon.axis attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_axis_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_axis_utf8(ds, sev))
        return res

    def check_lon_axis_value_v(self, ds):
        """[V086] Check lon.axis attribute value equals 'X'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_axis_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_axis_value(ds, sev))
        return res

    def check_lon_standard_name_type_v(self, ds):
        """[V088] Check lon.standard_name attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_standard_name_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_standard_name_type(ds, sev))
        return res

    def check_lon_standard_name_utf8_v(self, ds):
        """[V089] Check lon.standard_name attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_standard_name_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_standard_name_utf8(ds, sev))
        return res

    def check_lon_long_name_exists_v(self, ds):
        """[V091] Check lon.long_name attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_long_name_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_long_name_exists(ds, sev))
        return res

    def check_lon_long_name_type_v(self, ds):
        """[V092] Check lon.long_name attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_long_name_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_long_name_type(ds, sev))
        return res

    def check_lon_long_name_utf8_v(self, ds):
        """[V093] Check lon.long_name attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_long_name_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_long_name_utf8(ds, sev))
        return res

    def check_lon_long_name_value_v(self, ds):
        """[V094] Check lon.long_name attribute value equals 'longitude'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_long_name_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_long_name_value(ds, sev))
        return res

    def check_lon_units_type_v(self, ds):
        """[V096] Check lon.units attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_units_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_units_type(ds, sev))
        return res

    def check_lon_units_utf8_v(self, ds):
        """[V097] Check lon.units attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_units_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_units_utf8(ds, sev))
        return res

    def check_lon_bounds_exists_v(self, ds):
        """[V099] Check lon.bounds attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_bounds_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_bounds_exists(ds, sev))
        return res

    def check_lon_bounds_type_v(self, ds):
        """[V100] Check lon.bounds attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_bounds_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_bounds_type(ds, sev))
        return res

    def check_lon_bounds_utf8_v(self, ds):
        """[V101] Check lon.bounds attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_bounds_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_bounds_utf8(ds, sev))
        return res

    def check_lon_actual_range_exists_v(self, ds):
        """[V103] Check lon.actual_range attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_actual_range_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_actual_range_exists(ds, sev))
        return res

    def check_lon_actual_range_type_v(self, ds):
        """[V104] Check lon.actual_range attribute type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_lon_actual_range_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_lon_actual_range_type(ds, sev))
        return res

    # ===========================================================================
    # I VARIABLE ATTRIBUTE CHECKS
    # ===========================================================================

    def check_i_units_exists_v(self, ds):
        """[V228] Check i.units attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_units_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_i_units_exists(ds, sev))
        return res

    def check_i_units_type_v(self, ds):
        """[V229] Check i.units attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_units_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_i_units_type(ds, sev))
        return res

    def check_i_units_utf8_v(self, ds):
        """[V230] Check i.units attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_units_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_i_units_utf8(ds, sev))
        return res

    def check_i_units_value_v(self, ds):
        """[V231] Check i.units attribute value equals '1'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_units_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_i_units_value(ds, sev))
        return res

    def check_i_long_name_exists_v(self, ds):
        """[V232] Check i.long_name attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_long_name_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_i_long_name_exists(ds, sev))
        return res

    def check_i_long_name_type_v(self, ds):
        """[V233] Check i.long_name attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_long_name_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_i_long_name_type(ds, sev))
        return res

    def check_i_long_name_utf8_v(self, ds):
        """[V234] Check i.long_name attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_long_name_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_i_long_name_utf8(ds, sev))
        return res

    def check_i_long_name_value_v(self, ds):
        """[V235] Check i.long_name attribute value equals 'cell index'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_i_long_name_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_i_long_name_value(ds, sev))
        return res

    # ===========================================================================
    # J VARIABLE ATTRIBUTE CHECKS
    # ===========================================================================

    def check_j_units_exists_v(self, ds):
        """[V236] Check j.units attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_units_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_j_units_exists(ds, sev))
        return res

    def check_j_units_type_v(self, ds):
        """[V237] Check j.units attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_units_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_j_units_type(ds, sev))
        return res

    def check_j_units_utf8_v(self, ds):
        """[V238] Check j.units attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_units_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_j_units_utf8(ds, sev))
        return res

    def check_j_units_value_v(self, ds):
        """[V239] Check j.units attribute value equals '1'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_units_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_j_units_value(ds, sev))
        return res

    def check_j_long_name_exists_v(self, ds):
        """[V240] Check j.long_name attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_long_name_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_j_long_name_exists(ds, sev))
        return res

    def check_j_long_name_type_v(self, ds):
        """[V241] Check j.long_name attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_long_name_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_j_long_name_type(ds, sev))
        return res

    def check_j_long_name_utf8_v(self, ds):
        """[V242] Check j.long_name attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_long_name_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_j_long_name_utf8(ds, sev))
        return res

    def check_j_long_name_value_v(self, ds):
        """[V243] Check j.long_name attribute value equals 'cell index'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_j_long_name_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_j_long_name_value(ds, sev))
        return res

    # ===========================================================================
    # VERTICES_LATITUDE ATTRIBUTE CHECKS
    # ===========================================================================

    def check_vertices_latitude_units_exists_v(self, ds):
        """[V244] Check vertices_latitude.units attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_units_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_latitude_units_exists(ds, sev))
        return res

    def check_vertices_latitude_units_type_v(self, ds):
        """[V245] Check vertices_latitude.units attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_units_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_latitude_units_type(ds, sev))
        return res

    def check_vertices_latitude_units_utf8_v(self, ds):
        """[V246] Check vertices_latitude.units attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_units_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_latitude_units_utf8(ds, sev))
        return res

    def check_vertices_latitude_units_value_v(self, ds):
        """[V247] Check vertices_latitude.units attribute value equals 'degrees_north'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_units_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_latitude_units_value(ds, sev))
        return res

    def check_vertices_latitude_missing_value_exists_v(self, ds):
        """[V248] Check vertices_latitude.missing_value attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_missing_value_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_latitude_missing_value_exists(ds, sev))
        return res

    def check_vertices_latitude_missing_value_type_v(self, ds):
        """[V249] Check vertices_latitude.missing_value attribute type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_missing_value_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_latitude_missing_value_type(ds, sev))
        return res

    def check_vertices_latitude_fillvalue_exists_v(self, ds):
        """[V251] Check vertices_latitude._FillValue attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_fillvalue_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_latitude_fillvalue_exists(ds, sev))
        return res

    def check_vertices_latitude_fillvalue_type_v(self, ds):
        """[V252] Check vertices_latitude._FillValue attribute type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_latitude_fillvalue_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_latitude_fillvalue_type(ds, sev))
        return res

    # ===========================================================================
    # VERTICES_LONGITUDE ATTRIBUTE CHECKS
    # ===========================================================================

    def check_vertices_longitude_units_exists_v(self, ds):
        """[V254] Check vertices_longitude.units attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_units_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_longitude_units_exists(ds, sev))
        return res

    def check_vertices_longitude_units_type_v(self, ds):
        """[V255] Check vertices_longitude.units attribute type is NC_CHAR."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_units_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_longitude_units_type(ds, sev))
        return res

    def check_vertices_longitude_units_utf8_v(self, ds):
        """[V256] Check vertices_longitude.units attribute is UTF-8 encoded."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_units_utf8")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_longitude_units_utf8(ds, sev))
        return res

    def check_vertices_longitude_units_value_v(self, ds):
        """[V257] Check vertices_longitude.units attribute value equals 'degrees_east'."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_units_value")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_longitude_units_value(ds, sev))
        return res

    def check_vertices_longitude_missing_value_exists_v(self, ds):
        """[V258] Check vertices_longitude.missing_value attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_missing_value_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_longitude_missing_value_exists(ds, sev))
        return res

    def check_vertices_longitude_missing_value_type_v(self, ds):
        """[V259] Check vertices_longitude.missing_value attribute type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_missing_value_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_longitude_missing_value_type(ds, sev))
        return res

    def check_vertices_longitude_fillvalue_exists_v(self, ds):
        """[V261] Check vertices_longitude._FillValue attribute exists."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_fillvalue_exists")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_longitude_fillvalue_exists(ds, sev))
        return res

    def check_vertices_longitude_fillvalue_type_v(self, ds):
        """[V262] Check vertices_longitude._FillValue attribute type is NC_FLOAT."""
        res = []
        if not self.config or not self.config.variable_checks:
            return res
        check_config = self.config.variable_checks.get("check_vertices_longitude_fillvalue_type")
        if check_config:
            sev = self.get_severity(check_config.severity)
            res.extend(check_vertices_longitude_fillvalue_type(ds, sev))
        return res
