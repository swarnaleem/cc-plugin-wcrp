
# Simplified base class for WCRP plugins.

import toml
import os
import json
import re
from compliance_checker.base import BaseCheck, Result, TestCtx
from netCDF4 import Dataset
import xarray as xr

class WCRPBaseCheck(BaseCheck):
    """
    Base class for WCRP project-specific compliance checks.
    Provides common utilities for loading TOML configurations and mapping severities.
    """
    supported_ds = [Dataset]

    SEVERITY_MAP = {
        "HIGH": BaseCheck.HIGH,
        "H":    BaseCheck.HIGH,
        "MEDIUM": BaseCheck.MEDIUM,
        "M":      BaseCheck.MEDIUM,
        "LOW": BaseCheck.LOW,
        "L":      BaseCheck.LOW,
    }

    def __init__(self, options=None):
        super().__init__(options)
        self.config = None
        self.project_config_path = None # To be set by the specific WCRP plugin class
        self.xrds = None
        self.consistency_output = options.get('consistency_output', None) if options else None

    def setup(self, ds):
        """
        Loads the dataset into an xarray object and initializes basic info.
        Subclasses should call super().setup(ds) *first* and then load their specific config.
        """
        super().setup(ds) # Call parent's setup
        # Load dataset into xarray for easier metadata access
        # Use decode_times=False initially to handle potential calendar issues,
        # but decode CF conventions for attribute access.
        try:
            # Use the already open netCDF4 Dataset object 'ds'
            self.xrds = xr.open_dataset(xr.backends.NetCDF4DataStore(ds), decode_cf=True, decode_times=False)
        except Exception as e:
            print(f"Warning: Could not open dataset with xarray: {e}")
            self.xrds = None
            # If xarray fails, we cannot proceed with consistency output
            self.consistency_output = None

    def _load_project_config(self):
        """Loads the project-specific TOML configuration file using self.project_config_path."""
        if not self.project_config_path or not os.path.exists(self.project_config_path):
            print(f"Warning: Configuration file path not set or file not found at {self.project_config_path}")
            self.config = {}
            return
        try:
            with open(self.project_config_path, 'r', encoding="utf-8") as f:
                self.config = toml.load(f)
        except Exception as e:
            self.config = {}
            print(f"Error parsing TOML configuration from {self.project_config_path}: {e}")

    def get_severity(self, severity_str, default_severity_str="MEDIUM"):
        """Converts a severity string (from TOML) to a BaseCheck constant."""
        default_severity_const = self.SEVERITY_MAP.get(default_severity_str.upper(), BaseCheck.MEDIUM)
        if severity_str is None:
            return default_severity_const
        return self.SEVERITY_MAP.get(str(severity_str).upper(), default_severity_const)
    

    def _write_consistency_output(self):
        """
        Extracts key metadata from the dataset (using self.xrds) and writes it to the
        JSON file specified by self.consistency_output.
        This file is used by cc-qa for dataset-level checks.
        """
        if not self.consistency_output or self.xrds is None:
            # Do nothing if path not specified or xarray failed in setup
            return

        print(f"    -> Writing consistency output to: {self.consistency_output}")
        output_data = {}

        # --- Global Attributes ---
        # Separate required (defined in self.config loaded by subclass) and non-required
        required_global_attrs = self.config.get('global_attributes', {}).keys() if hasattr(self, 'config') and self.config else []
        output_data["global_attributes"] = {}
        output_data["global_attributes_non_required"] = {}
        output_data["global_attributes_dtypes"] = {}

        for attr_name, attr_value in self.xrds.attrs.items():
            # Convert numpy types to standard Python types for JSON
            if hasattr(attr_value, 'item'):
                 attr_value_json = attr_value.item()
            elif isinstance(attr_value, (list, tuple)) and attr_value and hasattr(attr_value[0], 'item'):
                 attr_value_json = [v.item() for v in attr_value]
            # Handle potential non-serializable types gracefully
            elif isinstance(attr_value, (str, int, float, bool, list, tuple, dict)) or attr_value is None:
                 attr_value_json = attr_value
            else:
                 attr_value_json = str(attr_value) # Fallback to string representation

            if attr_name in required_global_attrs:
                output_data["global_attributes"][attr_name] = attr_value_json
            else:
                output_data["global_attributes_non_required"][attr_name] = attr_value_json
            output_data["global_attributes_dtypes"][attr_name] = str(type(attr_value).__name__).replace("numpy.", "") # Clean type name


        # --- Dimensions ---
        output_data["dimensions"] = {dim: size for dim, size in self.xrds.dims.items()}

        # --- Coordinates ---
        output_data["coordinates"] = list(self.xrds.coords.keys())

        # --- Variable Attributes ---
        output_data["variable_attributes"] = {}
        output_data["variable_attributes_dtypes"] = {}
        for var_name, variable in self.xrds.variables.items():
            output_data["variable_attributes"][var_name] = {}
            output_data["variable_attributes_dtypes"][var_name] = {}
            for attr_name, attr_value in variable.attrs.items():
                 if hasattr(attr_value, 'item'):
                     attr_value_json = attr_value.item()
                 elif isinstance(attr_value, (list, tuple)) and attr_value and hasattr(attr_value[0], 'item'):
                     attr_value_json = [v.item() for v in attr_value]
                 elif isinstance(attr_value, (str, int, float, bool, list, tuple, dict)) or attr_value is None:
                     attr_value_json = attr_value
                 else:
                     attr_value_json = str(attr_value)

                 output_data["variable_attributes"][var_name][attr_name] = attr_value_json
                 output_data["variable_attributes_dtypes"][var_name][attr_name] = str(type(attr_value).__name__).replace("numpy.", "")

        # --- Time Information ---
        time_info = {"units": None, "calendar": None, "frequency": None,
                     "time0": None, "timen": None, "bound0": None, "boundn": None}
        if 'time' in self.xrds.coords:
            time_var = self.xrds['time']
            time_info["units"] = time_var.attrs.get("units")
            time_info["calendar"] = time_var.attrs.get("calendar", "standard")
            # Get frequency from global attributes, fallback to None
            time_info["frequency"] = self.xrds.attrs.get("frequency")

            # Extract first/last time values (as numbers for JSON)
            if time_var.size > 0:
                 # Ensure values are basic types
                 t0_val = time_var.values[0]
                 tn_val = time_var.values[-1]
                 time_info["time0"] = t0_val.item() if hasattr(t0_val, 'item') else t0_val
                 time_info["timen"] = tn_val.item() if hasattr(tn_val, 'item') else tn_val

            # Extract first/last bounds values (as numbers for JSON)
            bounds_name = time_var.attrs.get("bounds")
            if bounds_name in self.xrds and self.xrds[bounds_name].ndim == 2 and self.xrds[bounds_name].shape[1] == 2:
                 bounds_var = self.xrds[bounds_name]
                 if bounds_var.size >= 2: # Check if bounds actually have data
                      b0_val = bounds_var.values[0, 0]
                      bn_val = bounds_var.values[-1, 1]
                      time_info["bound0"] = b0_val.item() if hasattr(b0_val, 'item') else b0_val
                      time_info["boundn"] = bn_val.item() if hasattr(bn_val, 'item') else bn_val

        output_data["time_info"] = time_info

        # --- Write to JSON file ---
        try:
            # Ensure the directory exists before writing
            os.makedirs(os.path.dirname(self.consistency_output), exist_ok=True)
            with open(self.consistency_output, 'w', encoding='utf-8') as f:
                # Use default=str as a fallback for non-serializable types
                json.dump(output_data, f, indent=4, ensure_ascii=False, default=str)
        except Exception as e:
            # Print error but don't stop the whole check process
            print(f"    [ERROR] Failed to write consistency output JSON to {self.consistency_output}: {e}")
