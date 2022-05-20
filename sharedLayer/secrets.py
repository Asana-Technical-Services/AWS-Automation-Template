"""
sharedLater/secrets.py
A set of functions to manage the secrets used in this workflow
"""
import json
import boto3
import hmac
import hashlib

# Gets the value of a secret
def get_secret_value(name, version=None):
    secrets_client = boto3.client("secretsmanager")
    kwargs = {"SecretId": name}
    if version is not None:
        kwargs["VersionStage"] = version
    response = secrets_client.get_secret_value(**kwargs)
    return json.loads(response["SecretString"])


# Updates the value of an existing secret
def update_secret(name, secret_value):
    secrets_client = boto3.client("secretsmanager")

    kwargs = {"SecretId": name}
    kwargs["SecretString"] = secret_value

    response = secrets_client.update_secret(**kwargs)
    return response


# Verifies that a signature is valid
def verify_signature(signature, secret, data):
    msg_encoded = str(data).encode("ascii", "ignore")
    our_signature = hmac.new(
        secret.encode("ascii", "ignore"), msg=msg_encoded, digestmod=hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(
        our_signature.encode("ascii", "ignore"), signature.encode("ascii", "ignore")
    ):
        print(
            "Calculated digest does not match digest from API. This event is not trusted."
        )
        return False
    return True
