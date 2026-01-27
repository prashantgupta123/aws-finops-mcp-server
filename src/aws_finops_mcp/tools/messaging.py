"""Messaging service cleanup tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_unused_sqs_queues(
    session: Any, region_name: str, period: int = 90
) -> dict[str, Any]:
    """Find SQS queues with no messages sent/received in the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with unused SQS queues
    """
    sqs_client = session.client("sqs", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding unused SQS queues in {region_name}")
    
    try:
        # Get all queues
        queues_response = sqs_client.list_queues()
        queue_urls = queues_response.get("QueueUrls", [])
        
        for queue_url in queue_urls:
            queue_name = queue_url.split("/")[-1]
            
            try:
                # Get queue attributes
                attrs_response = sqs_client.get_queue_attributes(
                    QueueUrl=queue_url,
                    AttributeNames=["All"]
                )
                
                attributes = attrs_response.get("Attributes", {})
                approx_messages = int(attributes.get("ApproximateNumberOfMessages", 0))
                last_modified = attributes.get("LastModifiedTimestamp")
                retention_period = int(attributes.get("MessageRetentionPeriod", 345600))
                queue_type = "FIFO" if queue_name.endswith(".fifo") else "Standard"
                
                # Check CloudWatch metrics for activity
                has_activity = False
                for metric_name in ["NumberOfMessagesSent", "NumberOfMessagesReceived"]:
                    try:
                        metric_response = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/SQS",
                            MetricName=metric_name,
                            Dimensions=[{"Name": "QueueName", "Value": queue_name}],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=86400,
                            Statistics=["Sum"],
                        )
                        
                        if metric_response["Datapoints"]:
                            for datapoint in metric_response["Datapoints"]:
                                if datapoint.get("Sum", 0) > 0:
                                    has_activity = True
                                    break
                        
                        if has_activity:
                            break
                    except Exception:
                        pass
                
                if not has_activity and approx_messages == 0:
                    # Get tags
                    try:
                        tags_response = sqs_client.list_queue_tags(QueueUrl=queue_url)
                        tags = tags_response.get("Tags", {})
                        tags_str = ", ".join([f"{k}={v}" for k, v in tags.items()]) if tags else "None"
                    except Exception:
                        tags_str = "None"
                    
                    output_data.append({
                        "QueueUrl": queue_url,
                        "QueueName": queue_name,
                        "ApproximateNumberOfMessages": approx_messages,
                        "LastModifiedTimestamp": datetime.fromtimestamp(int(last_modified)).strftime("%Y-%m-%d %H:%M:%S") if last_modified else "N/A",
                        "MessageRetentionPeriod": f"{retention_period // 86400} days",
                        "QueueType": queue_type,
                        "Tags": tags_str,
                        "Description": f"SQS queue with no activity in the last {period} days",
                    })
            
            except Exception as e:
                logger.debug(f"Error processing queue {queue_name}: {e}")
                continue
        
        fields = {
            "1": "QueueName",
            "2": "QueueUrl",
            "3": "ApproximateNumberOfMessages",
            "4": "LastModifiedTimestamp",
            "5": "MessageRetentionPeriod",
            "6": "QueueType",
            "7": "Tags",
            "8": "Description",
        }
        
        return {
            "id": 210,
            "name": "Unused SQS Queues",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused SQS queues: {e}")
        raise


def find_unused_sns_topics(
    session: Any, region_name: str, period: int = 90
) -> dict[str, Any]:
    """Find SNS topics with no publishes in the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with unused SNS topics
    """
    sns_client = session.client("sns", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding unused SNS topics in {region_name}")
    
    try:
        # Get all topics
        topics_response = sns_client.list_topics()
        
        for topic in topics_response.get("Topics", []):
            topic_arn = topic["TopicArn"]
            topic_name = topic_arn.split(":")[-1]
            
            try:
                # Get topic attributes
                attrs_response = sns_client.get_topic_attributes(TopicArn=topic_arn)
                attributes = attrs_response.get("Attributes", {})
                
                subscriptions_confirmed = int(attributes.get("SubscriptionsConfirmed", 0))
                subscriptions_pending = int(attributes.get("SubscriptionsPending", 0))
                owner = attributes.get("Owner", "N/A")
                
                # Check CloudWatch metrics for publishes
                has_publishes = False
                try:
                    metric_response = cloudwatch_client.get_metric_statistics(
                        Namespace="AWS/SNS",
                        MetricName="NumberOfMessagesPublished",
                        Dimensions=[{"Name": "TopicName", "Value": topic_name}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=86400,
                        Statistics=["Sum"],
                    )
                    
                    if metric_response["Datapoints"]:
                        for datapoint in metric_response["Datapoints"]:
                            if datapoint.get("Sum", 0) > 0:
                                has_publishes = True
                                break
                except Exception:
                    pass
                
                if not has_publishes and subscriptions_confirmed == 0:
                    # Get tags
                    try:
                        tags_response = sns_client.list_tags_for_resource(ResourceArn=topic_arn)
                        tags = tags_response.get("Tags", [])
                        tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
                    except Exception:
                        tags_str = "None"
                    
                    output_data.append({
                        "TopicArn": topic_arn,
                        "TopicName": topic_name,
                        "SubscriptionsConfirmed": subscriptions_confirmed,
                        "SubscriptionsPending": subscriptions_pending,
                        "Owner": owner,
                        "Tags": tags_str,
                        "Description": f"SNS topic with no publishes in the last {period} days",
                    })
            
            except Exception as e:
                logger.debug(f"Error processing topic {topic_name}: {e}")
                continue
        
        fields = {
            "1": "TopicName",
            "2": "TopicArn",
            "3": "SubscriptionsConfirmed",
            "4": "SubscriptionsPending",
            "5": "Owner",
            "6": "Tags",
            "7": "Description",
        }
        
        return {
            "id": 211,
            "name": "Unused SNS Topics",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused SNS topics: {e}")
        raise


def find_unused_eventbridge_rules(
    session: Any, region_name: str, period: int = 90
) -> dict[str, Any]:
    """Find EventBridge rules with no invocations in the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with unused EventBridge rules
    """
    events_client = session.client("events", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding unused EventBridge rules in {region_name}")
    
    try:
        # Get all rules
        rules_response = events_client.list_rules()
        
        for rule in rules_response.get("Rules", []):
            rule_name = rule["Name"]
            rule_arn = rule["Arn"]
            state = rule.get("State", "ENABLED")
            event_pattern = rule.get("EventPattern", "N/A")
            schedule_expression = rule.get("ScheduleExpression", "N/A")
            
            # Check if disabled for long time
            if state == "DISABLED":
                # Get rule creation time (not directly available, use CloudWatch)
                output_data.append({
                    "RuleName": rule_name,
                    "RuleArn": rule_arn,
                    "State": state,
                    "EventPattern": event_pattern[:50] + "..." if len(event_pattern) > 50 else event_pattern,
                    "ScheduleExpression": schedule_expression,
                    "TargetCount": 0,
                    "CreatedTime": "N/A",
                    "Tags": "None",
                    "Description": f"EventBridge rule disabled for {period}+ days",
                })
            else:
                # Check CloudWatch metrics for invocations
                has_invocations = False
                try:
                    metric_response = cloudwatch_client.get_metric_statistics(
                        Namespace="AWS/Events",
                        MetricName="Invocations",
                        Dimensions=[{"Name": "RuleName", "Value": rule_name}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=86400,
                        Statistics=["Sum"],
                    )
                    
                    if metric_response["Datapoints"]:
                        for datapoint in metric_response["Datapoints"]:
                            if datapoint.get("Sum", 0) > 0:
                                has_invocations = True
                                break
                except Exception:
                    pass
                
                if not has_invocations:
                    # Get targets count
                    try:
                        targets_response = events_client.list_targets_by_rule(Rule=rule_name)
                        target_count = len(targets_response.get("Targets", []))
                    except Exception:
                        target_count = 0
                    
                    # Get tags
                    try:
                        tags_response = events_client.list_tags_for_resource(ResourceARN=rule_arn)
                        tags = tags_response.get("Tags", [])
                        tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
                    except Exception:
                        tags_str = "None"
                    
                    output_data.append({
                        "RuleName": rule_name,
                        "RuleArn": rule_arn,
                        "State": state,
                        "EventPattern": event_pattern[:50] + "..." if len(event_pattern) > 50 else event_pattern,
                        "ScheduleExpression": schedule_expression,
                        "TargetCount": target_count,
                        "CreatedTime": "N/A",
                        "Tags": tags_str,
                        "Description": f"EventBridge rule with no invocations in the last {period} days",
                    })
        
        fields = {
            "1": "RuleName",
            "2": "RuleArn",
            "3": "State",
            "4": "EventPattern",
            "5": "ScheduleExpression",
            "6": "TargetCount",
            "7": "CreatedTime",
            "8": "Tags",
            "9": "Description",
        }
        
        return {
            "id": 212,
            "name": "Unused EventBridge Rules",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused EventBridge rules: {e}")
        raise
