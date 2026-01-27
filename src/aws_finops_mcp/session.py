"""AWS Session Management Module.

Provides flexible AWS authentication methods including:
- Profile-based authentication
- Assumed role authentication
- Temporary credential authentication
- Access key authentication
- Default credential chain
"""

import boto3
import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_aws_session(
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
    region_name: str = "us-east-1",
) -> boto3.Session:
    """Create AWS session with flexible authentication methods.

    Args:
        profile_name: AWS profile name
        role_arn: IAM role ARN to assume
        access_key: AWS access key ID
        secret_access_key: AWS secret access key
        session_token: AWS session token (for temporary credentials)
        region_name: AWS region name

    Returns:
        boto3.Session: Configured AWS session

    Raises:
        ValueError: If invalid credentials provided
        Exception: If session creation fails
    """
    try:
        if profile_name:
            logger.info("Creating AWS session with profile authentication")
            return boto3.Session(profile_name=profile_name, region_name=region_name)

        elif role_arn:
            logger.info("Creating AWS session with assumed role")
            return _create_assumed_role_session(role_arn, region_name)

        elif session_token:
            logger.info("Creating AWS session with temporary credentials")
            return boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_access_key,
                aws_session_token=session_token,
                region_name=region_name,
            )

        elif access_key and secret_access_key:
            logger.info("Creating AWS session with access keys")
            return boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_access_key,
                region_name=region_name,
            )

        else:
            logger.info("Creating AWS session with default credentials")
            return boto3.Session(region_name=region_name)

    except Exception as e:
        logger.error(f"Failed to create AWS session: {str(e)}")
        raise


def _create_assumed_role_session(role_arn: str, region: str) -> boto3.Session:
    """Create session using assumed role credentials."""
    sts_client = boto3.client("sts", region_name=region)

    response = sts_client.assume_role(
        RoleArn=role_arn, RoleSessionName="AWSFinOpsMCPSession", DurationSeconds=3600
    )

    credentials = response["Credentials"]
    return boto3.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name=region,
    )
