#!/usr/bin/env python

# =============================================================================
# WCRP CORDEX-CMIP6 project
#
# This module defines the WCRP CORDEX-CMIP6 compliance checker, which serves as
# the main entry point for executing a series of validation checks on
# climate data submitted to the CORDEX-CMIP6 Archive.
# It relies on configuration defined in a TOML file.
# =============================================================================


# --- Standard library imports ---
import os

import toml

from checks.attribute_checks.check_attrs_cordex_cmip6 import (
    check_domain_id,
    check_driving_attributes,
    check_grid,
    check_grid_mapping,
    check_institution,
    check_references,
    check_version_realization,
    check_version_realization_info,
)
from checks.format_checks.check_compression import check_compression
from checks.format_checks.check_format import check_format
from checks.time_checks.check_time_cordex_cmip6 import (
    check_calendar,
    check_time_chunking,
    check_time_range,
    check_time_units,
)

# --- Import of checks and utils ---
from checks.utils import retrieve
from checks.variable_checks.check_coords_cordex_cmip6 import (
    check_horizontal_axes_bounds,
    check_lat_lon_bounds,
    check_lon_value_range,
)
from checks.variable_checks.check_data_types import (
    check_coord_data_types,
    check_var_data_type,
)
from plugins.wcrp_base import WCRPBaseCheck

# --- Esgvoc universe import ---
try:
    from esgvoc.api.universe import find_terms_in_data_descriptor

    ESG_VOCAB_AVAILABLE = True
except ImportError:
    ESG_VOCAB_AVAILABLE = False


# --- CMOR tables URL ---
CORDEX_CMIP6_CMOR_TABLES_URL = "https://raw.githubusercontent.com/WCRP-CORDEX/cordex-cmip6-cmor-tables/main/Tables/"


# --- Class definition of the CORDEX-CMIP6 checker from cc-plugin-wcrp ---
class CordexCmip6ProjectCheck(WCRPBaseCheck):
    """
    Class for WCRP CORDEX-CMIP6 project-specific compliance checks.
    """

    _cc_spec = "wcrp_cordex_cmip6"
    _cc_spec_version = "1.0"
    _cc_description = "WCRP CORDEX-CMIP6 Project Checks"
    _cc__url = "https://doi.org/10.5281/zenodo.15047096"
    _cc_display_headers = {3: "Required", 2: "Recommended", 1: "Suggested"}

    def __init__(self, options=None):
        super().__init__(options)
        if options and "project_config_path" in options:
            self.project_config_path = options["project_config_path"]
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            self.project_config_path = os.path.join(
                this_dir, "resources", "wcrp_config.toml"
            )

        # Define project name here for vocabulary checks
        self.project_name = "cordex-cmip6"

    def setup(self, ds):
        """Loads the main configuration and the variable mapping file before running checks."""
        super().setup(ds)
        self._load_project_config()
        # print(self.config)
        # for k,v in vars(self).items(): print(k,v); print()

        # Load variable mapping directly from 'mapping_variables.toml' located in the same folder as the config
        base_dir = os.path.dirname(self.project_config_path)
        mapping_filepath = os.path.join(base_dir, "mapping_variables.toml")

        try:
            with open(mapping_filepath) as f:
                self.variable_mapping = toml.load(f).get("mapping_variables", {})

        except FileNotFoundError:
            print(f"Mapping file '{mapping_filepath}' not found.")
            self.variable_mapping = {}
        except Exception as e:
            print(f"Error while loading variable mapping: {e}")
            self.variable_mapping = {}

        # Make use of CMOR tables for variable checks
        #  at a later time ESGVOC will be used for variable checks
        if not self.options.get("tables", False):
            tables_path = self.options.get(
                "tables_dir", "~/.wcrp_metadata/cordex-cmip6-cmor-tables"
            )
            for table in [
                "coordinate",
                "grids",
                "formula_terms",
                "CV",
                "1hr",
                "6hr",
                "day",
                "mon",
                "fx",
            ]:
                filename = "CORDEX-CMIP6_" + table + ".json"
                url = CORDEX_CMIP6_CMOR_TABLES_URL + filename
                filename_retrieved = retrieve(
                    CORDEX_CMIP6_CMOR_TABLES_URL + "CORDEX-CMIP6_" + table + ".json",
                    filename,
                    tables_path,
                    force=self.options.get("force_table_download", False),
                )
                if os.path.basename(os.path.realpath(filename_retrieved)) != filename:
                    raise AssertionError(
                        f"Download failed for CV table '{filename_retrieved}' (source: '{url}')."
                    )

            self._initialize_CV_info(tables_path)
            self._initialize_time_info()
            self._initialize_coords_info()
        if self.consistency_output:
            self._write_consistency_output()

    def check_format(self, ds):
        """
        [FILE002] Checks if the file is in the expected format according to the CORDEX-CMIP6 Archive Specifications.
        """
        results = []
        if "format_checks" not in self.config:
            return results

        config = self.config.get("format_checks", {})

        if "check_format" in config:
            check_config = config["check_format"]
            results.extend(
                check_format(
                    ds=ds,
                    expected_format=check_config.get("expected_format"),
                    expected_data_model=check_config.get("expected_data_model"),
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results

    def check_compression(self, ds):
        """
        [FILE003] Checks if the data compression is as expected according to the CORDEX-CMIP6 Archive Specifications.
        """
        results = []
        if "format_checks" not in self.config:
            return results

        config = self.config.get("format_checks", {})

        if "check_compression" in config:
            check_config = config["check_compression"]
            results.extend(
                check_compression(
                    ds=ds,
                    variable_name=self.varname[0] if self.varname != [] else None,
                    expected_complevel=check_config.get("expected_complevel"),
                    expected_shuffle=check_config.get("expected_shuffle"),
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results

    def check_data_types(self, ds):
        """
        [VAR011] Checks if the coordinate and variable data types are as expected according to the CORDEX-CMIP6 Archive Specifications.
        """
        results = []
        if "variable_checks" not in self.config:
            return results

        config = self.config.get("variable_checks", {})

        if "check_coord_data_types" in config:
            check_config = config["check_coord_data_types"]
            results.extend(
                check_coord_data_types(
                    CheckerObject=self,
                    ctype=check_config.get("ctype"),
                    auxtype=check_config.get("auxtype"),
                    severity=self.get_severity(check_config.get("severity")),
                )
            )
        if "check_var_data_type" in config:
            check_config = config["check_var_data_type"]
            results.extend(
                check_var_data_type(
                    CheckerObject=self,
                    var=check_config.get("var"),
                    vartype=check_config.get("vartype"),
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results

    def check_time_chunking(self, ds):
        """
        [CDXT001] Checks if the chunking with respect to the time dimension is in accordance with the CORDEX-CMIP6 Archive Specifications.
        """
        results = []
        if "time_checks" not in self.config:
            return results

        config = self.config.get("time_checks", {})

        if "check_time_chunking_cordex" in config:
            check_config = config["check_time_chunking_cordex"]
            results.extend(
                check_time_chunking(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results

    def check_time_range(self, ds):
        """
        [CDXT002] Checks if the time range is as expected according to the CORDEX-CMIP6 Archive Specifications.
        """
        results = []
        if "time_checks" not in self.config:
            return results

        config = self.config.get("time_checks", {})

        if "check_time_range_cordex" in config:
            check_config = config["check_time_range_cordex"]
            results.extend(
                check_time_range(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results

    def check_calendar(self, ds):
        """
        [CDXT003] Checks if the calendar is as expected according to the CORDEX-CMIP6 Archive Specifications.
        """
        results = []
        if "time_checks" not in self.config:
            return results

        config = self.config.get("time_checks", {})

        if "check_calendar_cordex" in config:
            check_config = config["check_calendar_cordex"]
            results.extend(
                check_calendar(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results

    def check_time_units(self, ds):
        """
        [CDXT004] Checks if the time units are as expected according to the CORDEX-CMIP6 Archive Specifications.
        """
        results = []
        if "time_checks" not in self.config:
            return results

        config = self.config.get("time_checks", {})

        if "check_time_units_cordex" in config:
            check_config = config["check_time_units_cordex"]
            results.extend(
                check_time_units(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results

    def check_attributes_cordex(self, ds):
        """
        [CDXA001] Checks compliance of certain CORDEX-CMIP6 global attributes with the CORDEX-CMIP6 Archive Specifications.
        """
        results = []
        if "attribute_checks" not in self.config:
            return results

        config = self.config.get("attribute_checks", {})

        if "check_grid_mapping" in config:
            check_config = config["check_grid_mapping"]
            results.extend(
                check_grid_mapping(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        if "check_domain_id" in config:
            check_config = config["check_domain_id"]
            results.extend(
                check_domain_id(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        if "check_institution" in config:
            check_config = config["check_institution"]
            results.extend(
                check_institution(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        if "check_references" in config:
            check_config = config["check_references"]
            results.extend(
                check_references(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        if "check_version_realization" in config:
            check_config = config["check_version_realization"]
            results.extend(
                check_version_realization(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        if "check_version_realization_info" in config:
            check_config = config["check_version_realization_info"]
            results.extend(
                check_version_realization_info(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        if "check_grid" in config:
            check_config = config["check_grid"]
            results.extend(
                check_grid(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        if "check_driving_attributes" in config:
            check_config = config["check_driving_attributes"]
            results.extend(
                check_driving_attributes(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results

    def check_lat_lon_bounds(self, ds):
        """
        [CDXV001] Checks existence of latitude and longitude bounds as recommended in the CORDEX-CMIP6 Archive Specifications.
        """
        results = []
        if "variable_checks" not in self.config:
            return results

        config = self.config.get("variable_checks", {})

        if "check_lat_lon_bounds" in config:
            check_config = config["check_lat_lon_bounds"]
            results.extend(
                check_lat_lon_bounds(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results

    def check_horizontal_axes_bounds(self, ds):
        """
        [CDXV002] Checks existence of rlat/rlon or x/y bounds as recommended in the CORDEX-CMIP6 Archive Specifications.
        """
        results = []
        if "variable_checks" not in self.config:
            return results

        config = self.config.get("variable_checks", {})

        if "check_horizontal_axes_bounds" in config:
            check_config = config["check_horizontal_axes_bounds"]
            results.extend(
                check_horizontal_axes_bounds(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results

    def check_lon_value_range(self, ds):
        """
        [CDXV003] Checks if longitude values are within the range required by the CORDEX-CMIP6 Archive Specifications.
        """
        results = []
        if "variable_checks" not in self.config:
            return results

        config = self.config.get("variable_checks", {})

        if "check_lon_value_range" in config:
            check_config = config["check_lon_value_range"]
            results.extend(
                check_lon_value_range(
                    self,
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results
