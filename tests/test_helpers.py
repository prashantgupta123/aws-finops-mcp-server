"""Tests for helper functions."""

import pytest
from aws_finops_mcp.utils.helpers import (
    format_header,
    fields_to_headers,
    safe_float,
    remove_percent_sign,
)


def test_format_header():
    """Test header formatting."""
    assert format_header("instance_id") == "Instance Id"
    assert format_header("InstanceId") == "Instance Id"
    assert format_header("AMIId") == "AMI ID"
    assert format_header("MaxCPUUtilization") == "Max CPU Utilization"
    assert format_header("vpc_id") == "Vpc Id"


def test_fields_to_headers():
    """Test fields to headers conversion."""
    fields = {"1": "InstanceId", "2": "InstanceName", "3": "MaxCPUUtilization"}
    headers = fields_to_headers(fields)
    
    assert len(headers) == 3
    assert headers[0]["accessor"] == "InstanceId"
    assert headers[1]["accessor"] == "InstanceName"
    assert headers[2]["accessor"] == "MaxCPUUtilization"


def test_safe_float():
    """Test safe float conversion."""
    assert safe_float("10.5") == 10.5
    assert safe_float("20%") == 20.0
    assert safe_float(None) == 0.0
    assert safe_float("invalid", 5.0) == 5.0
    assert safe_float(15) == 15.0


def test_remove_percent_sign():
    """Test percent sign removal."""
    assert remove_percent_sign("50%") == "50"
    assert remove_percent_sign("75.5%") == "75.5"
    assert remove_percent_sign("100") == "100"
    assert remove_percent_sign(None) == ""
