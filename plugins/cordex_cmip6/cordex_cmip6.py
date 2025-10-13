#!/usr/bin/env python

# =============================================================================
# WCRP CORDEX-CMIP6 project
#
# This module defines a WCRP example compliance checker, which serves as
# the main entry point for executing a series of validation checks on
# climate data. It relies on configuration defined in a TOML file and
# calls a suite of checks developed for quality control

import os

import toml

# =============================================================================
from netCDF4 import Dataset

from checks.format_checks.check_format import check_format
from plugins.wcrp_base import WCRPBaseCheck

# --- Esgvoc universe import---
try:
    from esgvoc.api.universe import find_terms_in_data_descriptor

    ESG_VOCAB_AVAILABLE = True
except ImportError:
    ESG_VOCAB_AVAILABLE = False


class CordexCmip6ProjectCheck(WCRPBaseCheck):

    _cc_spec = "plugin_cc6"
    _cc_spec_version = "1.0"
    _cc_description = "WCRP CORDEX-CMIP6 Project Checks"
    supported_ds = [Dataset]

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

    def _load_project_config(self):
        """Loads the TOML configuration file."""
        if not self.project_config_path or not os.path.exists(self.project_config_path):
            print(
                f"Warning: Configuration file path not set or file not found at {self.project_config_path}"
            )
            self.config = {}
            return
        try:
            with open(self.project_config_path, encoding="utf-8") as f:
                self.config = toml.load(f)
        except Exception as e:
            self.config = {}
            print(
                f"Error parsing TOML configuration from {self.project_config_path}: {e}"
            )

    def setup(self, ds):
        """Loads the main configuration and the variable mapping file before running checks."""
        super().setup(ds)
        self._load_project_config()
        # print(self.config)

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

    def check_format(self, ds):
        """
        Runs file format checks defined in the TOML.
        """
        results = []
        if "format_checks" not in self.config:
            return results

        config = self.config.get("format_checks", {})

        # --- Call for variant_label consistency check ---
        if "check_format" in config:
            check_config = config["check_format"]
            print(check_config)
            results.extend(
                check_format(
                    ds=ds,
                    expected_format=check_config.get("expected_format"),
                    expected_data_model=check_config.get("expected_data_model"),
                    severity=self.get_severity(check_config.get("severity")),
                )
            )

        return results
