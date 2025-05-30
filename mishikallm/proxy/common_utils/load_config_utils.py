import yaml

from mishikallm._logging import verbose_proxy_logger


def get_file_contents_from_s3(bucket_name, object_key):
    try:
        # v0 rely on boto3 for authentication - allowing boto3 to handle IAM credentials etc
        import tempfile

        import boto3
        from botocore.credentials import Credentials

        from mishikallm.main import bedrock_converse_chat_completion

        credentials: Credentials = bedrock_converse_chat_completion.get_credentials()
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_session_token=credentials.token,  # Optional, if using temporary credentials
        )
        verbose_proxy_logger.debug(
            f"Retrieving {object_key} from S3 bucket: {bucket_name}"
        )
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        verbose_proxy_logger.debug(f"Response: {response}")

        # Read the file contents
        file_contents = response["Body"].read().decode("utf-8")
        verbose_proxy_logger.debug("File contents retrieved from S3")

        # Create a temporary file with YAML extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as temp_file:
            temp_file.write(file_contents.encode("utf-8"))
            temp_file_path = temp_file.name
            verbose_proxy_logger.debug(f"File stored temporarily at: {temp_file_path}")

        # Load the YAML file content
        with open(temp_file_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)

        return config
    except ImportError as e:
        # this is most likely if a user is not using the mishikallm docker container
        verbose_proxy_logger.error(f"ImportError: {str(e)}")
        pass
    except Exception as e:
        verbose_proxy_logger.error(f"Error retrieving file contents: {str(e)}")
        return None


async def get_config_file_contents_from_gcs(bucket_name, object_key):
    try:
        from mishikallm.integrations.gcs_bucket.gcs_bucket import GCSBucketLogger

        gcs_bucket = GCSBucketLogger(
            bucket_name=bucket_name,
        )
        file_contents = await gcs_bucket.download_gcs_object(object_key)
        if file_contents is None:
            raise Exception(f"File contents are None for {object_key}")
        # file_contentis is a bytes object, so we need to convert it to yaml
        file_contents = file_contents.decode("utf-8")
        # convert to yaml
        config = yaml.safe_load(file_contents)
        return config

    except Exception as e:
        verbose_proxy_logger.error(f"Error retrieving file contents: {str(e)}")
        return None


# # Example usage
# bucket_name = 'mishikallm-proxy'
# object_key = 'mishikallm_proxy_config.yaml'
