"""Network cleanup and optimization tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_unused_nat_gateways(
    session: Any, region_name: str, period: int = 32, max_results: int = 100
) -> dict[str, Any]:
    """Find NAT Gateways with no traffic in the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days (default: 32)
        max_results: Maximum results to return
    
    Returns:
        Dictionary with unused NAT Gateways
    """
    ec2_client = session.client("ec2", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding unused NAT Gateways in {region_name}")
    
    try:
        # Get all NAT Gateways
        response = ec2_client.describe_nat_gateways(MaxResults=max_results)
        
        for nat_gateway in response["NatGateways"]:
            nat_gateway_id = nat_gateway["NatGatewayId"]
            state = nat_gateway["State"]
            
            # Skip if not available
            if state != "available":
                continue
            
            # Check if associated with any route tables
            route_tables_response = ec2_client.describe_route_tables(
                Filters=[{"Name": "route.nat-gateway-id", "Values": [nat_gateway_id]}]
            )
            has_route_table = len(route_tables_response["RouteTables"]) > 0
            
            # Check CloudWatch metrics for traffic
            metrics_to_check = [
                "ActiveConnectionCount",
                "PacketsInFromSource",
                "PacketsInFromDestination"
            ]
            
            has_traffic = False
            for metric_name in metrics_to_check:
                try:
                    metric_response = cloudwatch_client.get_metric_statistics(
                        Namespace="AWS/NATGateway",
                        MetricName=metric_name,
                        Dimensions=[{"Name": "NatGatewayId", "Value": nat_gateway_id}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=86400,
                        Statistics=["Sum"],
                    )
                    
                    if metric_response["Datapoints"]:
                        for datapoint in metric_response["Datapoints"]:
                            if datapoint.get("Sum", 0) > 0:
                                has_traffic = True
                                break
                    
                    if has_traffic:
                        break
                except Exception as e:
                    logger.warning(f"Error checking metric {metric_name} for {nat_gateway_id}: {e}")
            
            # If no traffic and not in route tables, it's unused
            if not has_traffic and not has_route_table:
                # Get NAT Gateway details
                vpc_id = nat_gateway.get("VpcId", "N/A")
                subnet_id = nat_gateway.get("SubnetId", "N/A")
                connectivity_type = nat_gateway.get("ConnectivityType", "public")
                create_time = nat_gateway.get("CreateTime")
                
                # Get Elastic IP
                elastic_ip = "None"
                private_ip = "None"
                for address in nat_gateway.get("NatGatewayAddresses", []):
                    if address.get("PublicIp"):
                        elastic_ip = address["PublicIp"]
                    if address.get("PrivateIp"):
                        private_ip = address["PrivateIp"]
                
                # Calculate age
                age_days = 0
                if create_time:
                    age_days = (datetime.now(create_time.tzinfo) - create_time).days
                
                # NAT Gateway cost: ~$0.045/hour = ~$32.40/month
                monthly_cost = 0.045 * 24 * 30
                
                # Get tags
                tags = nat_gateway.get("Tags", [])
                tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
                
                output_data.append({
                    "NatGatewayId": nat_gateway_id,
                    "State": state,
                    "VpcId": vpc_id,
                    "SubnetId": subnet_id,
                    "ConnectivityType": connectivity_type,
                    "ElasticIp": elastic_ip,
                    "PrivateIp": private_ip,
                    "CreateTime": create_time.strftime("%Y-%m-%d %H:%M:%S") if create_time else "N/A",
                    "AgeDays": age_days,
                    "HasRouteTableAssociation": has_route_table,
                    "EstimatedMonthlyCost": f"${monthly_cost:.2f}",
                    "Tags": tags_str,
                    "Description": f"NAT Gateway with no traffic in the last {period} days",
                })
        
        # Calculate total potential savings
        total_monthly_cost = len(output_data) * 32.40
        
        fields = {
            "1": "NatGatewayId",
            "2": "State",
            "3": "VpcId",
            "4": "SubnetId",
            "5": "ConnectivityType",
            "6": "ElasticIp",
            "7": "PrivateIp",
            "8": "CreateTime",
            "9": "AgeDays",
            "10": "HasRouteTableAssociation",
            "11": "EstimatedMonthlyCost",
            "12": "Tags",
            "13": "Description",
        }
        
        return {
            "id": 201,
            "name": "Unused NAT Gateways",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused NAT Gateways: {e}")
        raise


def find_unused_vpc_endpoints(
    session: Any, region_name: str, period: int = 90, max_results: int = 100
) -> dict[str, Any]:
    """Find VPC endpoints with no traffic in the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
        max_results: Maximum results to return
    
    Returns:
        Dictionary with unused VPC endpoints
    """
    ec2_client = session.client("ec2", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding unused VPC endpoints in {region_name}")
    
    try:
        # Get all VPC endpoints
        paginator = ec2_client.get_paginator("describe_vpc_endpoints")
        page_iterator = paginator.paginate(
            PaginationConfig={"MaxItems": max_results}
        )
        
        for page in page_iterator:
            for endpoint in page["VpcEndpoints"]:
                endpoint_id = endpoint["VpcEndpointId"]
                endpoint_type = endpoint["VpcEndpointType"]
                state = endpoint["State"]
                service_name = endpoint["ServiceName"]
                vpc_id = endpoint.get("VpcId", "N/A")
                
                # Skip if not available
                if state != "available":
                    continue
                
                is_unused = False
                
                # For Gateway endpoints, check route table associations
                if endpoint_type == "Gateway":
                    route_table_ids = endpoint.get("RouteTableIds", [])
                    if not route_table_ids:
                        is_unused = True
                
                # For Interface endpoints, check network interfaces and CloudWatch metrics
                elif endpoint_type == "Interface":
                    network_interface_ids = endpoint.get("NetworkInterfaceIds", [])
                    
                    # Check if there's traffic through the endpoint
                    has_traffic = False
                    for eni_id in network_interface_ids:
                        try:
                            # Check bytes in/out metrics
                            for metric_name in ["BytesIn", "BytesOut"]:
                                metric_response = cloudwatch_client.get_metric_statistics(
                                    Namespace="AWS/PrivateLinkEndpoints",
                                    MetricName=metric_name,
                                    Dimensions=[{"Name": "VPC Endpoint Id", "Value": endpoint_id}],
                                    StartTime=start_time,
                                    EndTime=end_time,
                                    Period=86400,
                                    Statistics=["Sum"],
                                )
                                
                                if metric_response["Datapoints"]:
                                    for datapoint in metric_response["Datapoints"]:
                                        if datapoint.get("Sum", 0) > 0:
                                            has_traffic = True
                                            break
                                
                                if has_traffic:
                                    break
                        except Exception as e:
                            logger.debug(f"Error checking metrics for {endpoint_id}: {e}")
                    
                    if not has_traffic:
                        is_unused = True
                
                if is_unused:
                    # Get subnet IDs
                    subnet_ids = endpoint.get("SubnetIds", [])
                    subnet_ids_str = ", ".join(subnet_ids) if subnet_ids else "None"
                    
                    # Get network interface IDs
                    network_interface_ids = endpoint.get("NetworkInterfaceIds", [])
                    eni_str = ", ".join(network_interface_ids) if network_interface_ids else "None"
                    
                    # Calculate cost (Interface endpoints: ~$0.01/hour = ~$7.20/month per AZ)
                    monthly_cost = 0
                    if endpoint_type == "Interface":
                        num_azs = len(subnet_ids) if subnet_ids else 1
                        monthly_cost = 0.01 * 24 * 30 * num_azs
                    
                    # Get creation time
                    create_time = endpoint.get("CreationTimestamp")
                    age_days = 0
                    if create_time:
                        age_days = (datetime.now(create_time.tzinfo) - create_time).days
                    
                    # Get tags
                    tags = endpoint.get("Tags", [])
                    tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
                    
                    output_data.append({
                        "VpcEndpointId": endpoint_id,
                        "VpcEndpointType": endpoint_type,
                        "ServiceName": service_name,
                        "State": state,
                        "VpcId": vpc_id,
                        "SubnetIds": subnet_ids_str,
                        "NetworkInterfaceIds": eni_str,
                        "CreateTime": create_time.strftime("%Y-%m-%d %H:%M:%S") if create_time else "N/A",
                        "AgeDays": age_days,
                        "EstimatedMonthlyCost": f"${monthly_cost:.2f}" if monthly_cost > 0 else "N/A",
                        "Tags": tags_str,
                        "Description": f"VPC endpoint with no traffic in the last {period} days",
                    })
        
        # Calculate total potential savings
        total_monthly_cost = sum(
            float(ep["EstimatedMonthlyCost"].replace("$", ""))
            for ep in output_data
            if ep["EstimatedMonthlyCost"] != "N/A"
        )
        
        fields = {
            "1": "VpcEndpointId",
            "2": "VpcEndpointType",
            "3": "ServiceName",
            "4": "State",
            "5": "VpcId",
            "6": "SubnetIds",
            "7": "NetworkInterfaceIds",
            "8": "CreateTime",
            "9": "AgeDays",
            "10": "EstimatedMonthlyCost",
            "11": "Tags",
            "12": "Description",
        }
        
        return {
            "id": 202,
            "name": "Unused VPC Endpoints",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused VPC endpoints: {e}")
        raise


def find_unused_internet_gateways(
    session: Any, region_name: str, max_results: int = 100
) -> dict[str, Any]:
    """Find Internet Gateways not attached to VPCs or attached to VPCs with no resources.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        max_results: Maximum results to return
    
    Returns:
        Dictionary with unused Internet Gateways
    """
    ec2_client = session.client("ec2", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding unused Internet Gateways in {region_name}")
    
    try:
        # Get all Internet Gateways
        response = ec2_client.describe_internet_gateways(MaxResults=max_results)
        
        for igw in response["InternetGateways"]:
            igw_id = igw["InternetGatewayId"]
            attachments = igw.get("Attachments", [])
            
            is_unused = False
            vpc_id = "None"
            attachment_state = "detached"
            
            # Check if detached
            if not attachments:
                is_unused = True
            else:
                # Check if attached VPC has any resources
                attachment = attachments[0]
                vpc_id = attachment.get("VpcId", "None")
                attachment_state = attachment.get("State", "unknown")
                
                if attachment_state == "available" and vpc_id != "None":
                    # Check if VPC has any instances
                    instances_response = ec2_client.describe_instances(
                        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
                    )
                    
                    has_instances = False
                    for reservation in instances_response["Reservations"]:
                        if reservation["Instances"]:
                            has_instances = True
                            break
                    
                    if not has_instances:
                        is_unused = True
            
            if is_unused:
                # Get tags
                tags = igw.get("Tags", [])
                tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
                
                output_data.append({
                    "InternetGatewayId": igw_id,
                    "State": attachment_state,
                    "VpcId": vpc_id,
                    "AttachmentCount": len(attachments),
                    "Tags": tags_str,
                    "Description": "Internet Gateway not attached or attached to VPC with no resources",
                })
        
        fields = {
            "1": "InternetGatewayId",
            "2": "State",
            "3": "VpcId",
            "4": "AttachmentCount",
            "5": "Tags",
            "6": "Description",
        }
        
        return {
            "id": 203,
            "name": "Unused Internet Gateways",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused Internet Gateways: {e}")
        raise



def find_unused_cloudfront_distributions(
    session: Any, region_name: str = "us-east-1", period: int = 90
) -> dict[str, Any]:
    """Find CloudFront distributions with no requests in the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region (CloudFront is global but uses us-east-1)
        period: Lookback period in days
    
    Returns:
        Dictionary with unused CloudFront distributions
    """
    cloudfront_client = session.client("cloudfront", region_name="us-east-1")
    cloudwatch_client = session.client("cloudwatch", region_name="us-east-1")
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info("Finding unused CloudFront distributions")
    
    try:
        # Get all distributions
        paginator = cloudfront_client.get_paginator("list_distributions")
        
        for page in paginator.paginate():
            for distribution in page.get("DistributionList", {}).get("Items", []):
                distribution_id = distribution["Id"]
                domain_name = distribution["DomainName"]
                status = distribution["Status"]
                enabled = distribution["Enabled"]
                
                # Check CloudWatch metrics for requests
                requests_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/CloudFront",
                    MetricName="Requests",
                    Dimensions=[{"Name": "DistributionId", "Value": distribution_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Sum"]
                )
                
                total_requests = 0
                if requests_metric["Datapoints"]:
                    total_requests = sum(dp["Sum"] for dp in requests_metric["Datapoints"])
                
                if total_requests == 0:
                    # Get distribution details
                    aliases = distribution.get("Aliases", {}).get("Items", [])
                    aliases_str = ", ".join(aliases) if aliases else "None"
                    
                    # Get origins
                    origins = distribution.get("Origins", {}).get("Items", [])
                    origin_domains = [origin.get("DomainName", "Unknown") for origin in origins]
                    origins_str = ", ".join(origin_domains) if origin_domains else "None"
                    
                    # Estimate cost ($0.085 per month minimum)
                    estimated_monthly_cost = 0.085
                    
                    output_data.append({
                        "DistributionId": distribution_id,
                        "DomainName": domain_name,
                        "Aliases": aliases_str,
                        "Origins": origins_str,
                        "Status": status,
                        "Enabled": "Yes" if enabled else "No",
                        "TotalRequests": int(total_requests),
                        "EstimatedMonthlyCost": f"${estimated_monthly_cost:.2f}",
                        "Recommendation": "Disable or delete distribution if no longer needed",
                    })
        
        total_monthly_cost = sum(
            float(item["EstimatedMonthlyCost"].replace("$", ""))
            for item in output_data
        )
        
        fields = {
            "1": "DistributionId",
            "2": "DomainName",
            "3": "Aliases",
            "4": "Origins",
            "5": "Status",
            "6": "Enabled",
            "7": "TotalRequests",
            "8": "EstimatedMonthlyCost",
            "9": "Recommendation",
        }
        
        return {
            "id": 205,
            "name": "Unused CloudFront Distributions",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused CloudFront distributions: {e}")
        raise


def find_unused_route53_hosted_zones(
    session: Any, region_name: str = "us-east-1", period: int = 90
) -> dict[str, Any]:
    """Find Route53 hosted zones with no query activity.
    
    Args:
        session: Boto3 session
        region_name: AWS region (Route53 is global but uses us-east-1)
        period: Lookback period in days
    
    Returns:
        Dictionary with unused Route53 hosted zones
    """
    route53_client = session.client("route53", region_name="us-east-1")
    cloudwatch_client = session.client("cloudwatch", region_name="us-east-1")
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info("Finding unused Route53 hosted zones")
    
    try:
        # Get all hosted zones
        paginator = route53_client.get_paginator("list_hosted_zones")
        
        for page in paginator.paginate():
            for hosted_zone in page["HostedZones"]:
                hosted_zone_id = hosted_zone["Id"].split("/")[-1]
                name = hosted_zone["Name"]
                is_private = hosted_zone.get("Config", {}).get("PrivateZone", False)
                resource_record_set_count = hosted_zone.get("ResourceRecordSetCount", 0)
                
                # Check CloudWatch metrics for queries (only available for public zones)
                total_queries = 0
                if not is_private:
                    try:
                        queries_metric = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/Route53",
                            MetricName="QueryCount",
                            Dimensions=[{"Name": "HostedZoneId", "Value": hosted_zone_id}],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=86400,
                            Statistics=["Sum"]
                        )
                        
                        if queries_metric["Datapoints"]:
                            total_queries = sum(dp["Sum"] for dp in queries_metric["Datapoints"])
                    except Exception as e:
                        logger.warning(f"Could not get metrics for hosted zone {hosted_zone_id}: {e}")
                
                # Flag if no queries or very few record sets
                is_unused = (total_queries == 0 and not is_private) or resource_record_set_count <= 2
                
                if is_unused:
                    # Get tags
                    tags = {}
                    try:
                        tags_response = route53_client.list_tags_for_resource(
                            ResourceType="hostedzone",
                            ResourceId=hosted_zone_id
                        )
                        tags = {tag["Key"]: tag["Value"] for tag in tags_response.get("Tags", [])}
                    except Exception:
                        pass
                    
                    # Calculate cost ($0.50 per hosted zone per month)
                    estimated_monthly_cost = 0.50
                    
                    output_data.append({
                        "HostedZoneId": hosted_zone_id,
                        "Name": name,
                        "Type": "Private" if is_private else "Public",
                        "ResourceRecordSetCount": resource_record_set_count,
                        "TotalQueries": int(total_queries) if not is_private else "N/A (Private)",
                        "EstimatedMonthlyCost": f"${estimated_monthly_cost:.2f}",
                        "Tags": str(tags),
                        "Recommendation": "Delete hosted zone if no longer needed",
                    })
        
        total_monthly_cost = sum(
            float(item["EstimatedMonthlyCost"].replace("$", ""))
            for item in output_data
        )
        
        fields = {
            "1": "HostedZoneId",
            "2": "Name",
            "3": "Type",
            "4": "ResourceRecordSetCount",
            "5": "TotalQueries",
            "6": "EstimatedMonthlyCost",
            "7": "Recommendation",
            "8": "Tags",
        }
        
        return {
            "id": 206,
            "name": "Unused Route53 Hosted Zones",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused Route53 hosted zones: {e}")
        raise
