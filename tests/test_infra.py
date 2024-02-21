import os
import boto3
import pytest
import time


@pytest.fixture
def s3_client():
    return boto3.client(
        "s3",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


@pytest.fixture
def dynamodb_client():
    return boto3.client(
        "dynamodb",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


def test_cdk(s3_client, dynamodb_client):
    # Assert CDK outputs
    assert os.path.exists("cdk.out")
    assert os.path.exists("cdk.out/manifest.json")

    # Check S3 bucket existence
    target_bucket_prefix = "sqsblogstack-inventoryupdatesbucketfe-"
    response = s3_client.list_buckets()
    target_bucket = next(
        (
            bucket["Name"]
            for bucket in response["Buckets"]
            if bucket["Name"].startswith(target_bucket_prefix)
        ),
        None,
    )
    assert target_bucket is not None

    # Upload file to S3
    local_file_path = "sqs_blog/sample_file.csv"
    s3_object_key = "sample_file.csv"
    s3_client.upload_file(local_file_path, target_bucket, s3_object_key)

    # Check DynamoDB table existence
    target_ddb_prefix = "SqsBlogStack-InventoryUpdates"
    response = dynamodb_client.list_tables()
    target_ddb = next(
        (
            table
            for table in response["TableNames"]
            if table.startswith(target_ddb_prefix)
        ),
        None,
    )
    assert target_ddb is not None

    # Wait for eventual consistency in DynamoDB
    time.sleep(10)

    # Check if there is at least one item in the DynamoDB table
    response = dynamodb_client.scan(TableName=target_ddb)
    assert response.get("Count", 0) > 0
