import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from decouple import config

# --- R2 Configuration ---
CLOUDFLARE_R2_ENDPOINT = config("CLOUDFLARE_R2_ENDPOINT", default=None)
CLOUDFLARE_R2_ACCESS_KEY = config("CLOUDFLARE_R2_ACCESS_KEY", default=None)
CLOUDFLARE_R2_SECRET_KEY = config("CLOUDFLARE_R2_SECRET_KEY", default=None)
CLOUDFLARE_R2_BUCKET_NAME = config("CLOUDFLARE_R2_BUCKET_NAME", default=None)

def is_r2_configured():
    """Check if all necessary R2 environment variables are set."""
    return all([
        CLOUDFLARE_R2_ENDPOINT,
        CLOUDFLARE_R2_ACCESS_KEY,
        CLOUDFLARE_R2_SECRET_KEY,
        CLOUDFLARE_R2_BUCKET_NAME
    ])

def get_r2_client():
    """Initialize and return a boto3 client for R2."""
    if not is_r2_configured():
        return None
    try:
        return boto3.client(
            's3',
            endpoint_url=CLOUDFLARE_R2_ENDPOINT,
            aws_access_key_id=CLOUDFLARE_R2_ACCESS_KEY,
            aws_secret_access_key=CLOUDFLARE_R2_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )
    except Exception:
        return None

def upload_file_to_r2(file_obj, object_name: str):
    """Upload a file-like object to R2."""
    r2_client = get_r2_client()
    if not r2_client:
        raise ConnectionError("R2 client is not available or configured.")

    try:
        r2_client.upload_fileobj(
            file_obj,
            CLOUDFLARE_R2_BUCKET_NAME,
            object_name
        )
    except ClientError as e:
        print(f"Error uploading to R2: {e}")
        raise IOError("Could not upload file to R2.")

def download_file_from_r2(object_name: str, destination_path: str):
    """Download a file from an R2 bucket."""
    r2_client = get_r2_client()
    if not r2_client:
        raise ConnectionError("R2 client is not available or configured.")

    try:
        r2_client.download_file(CLOUDFLARE_R2_BUCKET_NAME, object_name, destination_path)
    except ClientError as e:
        print(f"Error downloading file from R2: {e}")
        raise IOError(f"Could not download file from R2: {object_name}")

def generate_presigned_url(object_name: str, expiration: int = 3600) -> str:
    """Generate a presigned URL to share an R2 object."""
    r2_client = get_r2_client()
    if not r2_client:
        return None

    try:
        response = r2_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': CLOUDFLARE_R2_BUCKET_NAME, 'Key': object_name},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None

def delete_file_from_r2(object_name: str):
    """Delete a file from an R2 bucket."""
    r2_client = get_r2_client()
    if not r2_client:
        raise ConnectionError("R2 client is not available or configured.")

    try:
        r2_client.delete_object(Bucket=CLOUDFLARE_R2_BUCKET_NAME, Key=object_name)
    except ClientError as e:
        print(f"Error deleting file from R2: {e}")
        raise IOError(f"Could not delete file from R2: {object_name}")

def test_r2_connection():
    """Test the connection to R2 by listing buckets."""
    r2_client = get_r2_client()
    if not r2_client:
        return {"status": "R2 not configured"}
    try:
        # Use head_bucket which is a lower-permission way to check for bucket existence and access
        r2_client.head_bucket(Bucket=CLOUDFLARE_R2_BUCKET_NAME)
        return {"status": "connected"}
    except ClientError as e:
        # If a client error is thrown, check if it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            return {"status": "error", "message": f"Bucket '{CLOUDFLARE_R2_BUCKET_NAME}' not found."}
        return {"status": "error", "message": f"Connection failed: {e.response['Error']['Code']}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}