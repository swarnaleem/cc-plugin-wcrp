#!/usr/bin/env python
"""
This module provides existence checks for specific coordinate variables
(lat, lon, height, i, j, vertices_latitude, vertices_longitude, etc.).                                           

Note: This module uses an internal `_check_var_exists` function rather than 
the generic `check_variable_existence` from `variable_checks/`. This is because 
the generic function uses a fixed check ID (VAR001), whereas coordinate checks 
require specific IDs per variable (V030, V068, V204, etc.).                           
                                                                              
Check IDs:
    V001  - height
    V030  - lat
    V038  - lat_bnds
    V068  - lon
    V076  - lon_bnds
    V204  - i
    V211  - j
    V218  - vertices_latitude
    V223  - vertices_longitude                                                 
"""

from compliance_checker.base import BaseCheck, TestCtx


def _check_var_exists(ds, var_name, check_id, severity):                    
      """                                                                     
      Internal helper to verify if a variable exists in the dataset.          
                                                                              
      This function is used instead of the generic `check_variable_existence` 
      to allow custom check IDs for each coordinate variable, enabling proper 
      traceability in compliance reports.                                     
                                                                              
      Parameters                                                              
      ----------                                                              
      ds : netCDF4.Dataset                                                    
          An open netCDF dataset.                                             
      var_name : str                                                          
          The name of the variable to check (e.g., 'lat', 'lon', 'i').        
      check_id : str                                                          
          The unique check identifier (e.g., 'V030' for lat, 'V068' for lon). 
      severity : int                                                          
          The severity level (BaseCheck.HIGH, BaseCheck.MEDIUM,               
  BaseCheck.LOW).                                                             
                                                                              
      Returns                                                                 
      -------                                                                 
      list[Result]                                                            
          A list containing one Result object with pass/fail status.          
      """                                                                     
      ctx = TestCtx(severity, f"[{check_id}] Variable Existence: '{var_name}'")                                                              
      ctx.assert_true(var_name in ds.variables, f"Variable '{var_name}' is missing.")                                                                  
      return [ctx.to_result()]   


# V030: lat variable exists
def check_lat_exists(ds, severity=BaseCheck.HIGH):
    return _check_var_exists(ds, "lat", "V030", severity)


# V068: lon variable exists
def check_lon_exists(ds, severity=BaseCheck.HIGH):
    return _check_var_exists(ds, "lon", "V068", severity)


# V001: height variable exists
def check_height_exists(ds, severity=BaseCheck.HIGH):
    return _check_var_exists(ds, "height", "V001", severity)


# V038: lat_bnds variable exists
def check_lat_bnds_exists(ds, severity=BaseCheck.HIGH):
    return _check_var_exists(ds, "lat_bnds", "V038", severity)


# V076: lon_bnds variable exists
def check_lon_bnds_exists(ds, severity=BaseCheck.HIGH):
    return _check_var_exists(ds, "lon_bnds", "V076", severity)


# V204: i variable exists
def check_i_exists(ds, severity=BaseCheck.HIGH):
    return _check_var_exists(ds, "i", "V204", severity)


# V211: j variable exists
def check_j_exists(ds, severity=BaseCheck.HIGH):
    return _check_var_exists(ds, "j", "V211", severity)


# V218: vertices_latitude variable exists
def check_vertices_latitude_exists(ds, severity=BaseCheck.HIGH):
    return _check_var_exists(ds, "vertices_latitude", "V218", severity)


# V223: vertices_longitude variable exists
def check_vertices_longitude_exists(ds, severity=BaseCheck.HIGH):
    return _check_var_exists(ds, "vertices_longitude", "V223", severity)
