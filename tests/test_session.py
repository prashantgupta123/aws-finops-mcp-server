"""Tests for AWS session management."""

import pytest
from unittest.mock import Mock, patch
from aws_finops_mcp.session import get_aws_session


def test_get_aws_session_with_profile():
    """Test session creation with profile name."""
    with patch("boto3.Session") as mock_session:
        get_aws_session(profile_name="test-profile", region_name="us-east-1")
        mock_session.assert_called_once_with(
            profile_name="test-profile", region_name="us-east-1"
        )


def test_get_aws_session_with_access_keys():
    """Test session creation with access keys."""
    with patch("boto3.Session") as mock_session:
        get_aws_session(
            access_key="AKIATEST",
            secret_access_key="secret",
            region_name="us-west-2",
        )
        mock_session.assert_called_once_with(
            aws_access_key_id="AKIATEST",
            aws_secret_access_key="secret",
            region_name="us-west-2",
        )


def test_get_aws_session_with_temporary_credentials():
    """Test session creation with temporary credentials."""
    with patch("boto3.Session") as mock_session:
        get_aws_session(
            access_key="ASIATEST",
            secret_access_key="secret",
            session_token="token123",
            region_name="eu-west-1",
        )
        mock_session.assert_called_once_with(
            aws_access_key_id="ASIATEST",
            aws_secret_access_key="secret",
            aws_session_token="token123",
            region_name="eu-west-1",
        )


def test_get_aws_session_default():
    """Test session creation with default credentials."""
    with patch("boto3.Session") as mock_session:
        get_aws_session(region_name="ap-southeast-1")
        mock_session.assert_called_once_with(region_name="ap-southeast-1")
