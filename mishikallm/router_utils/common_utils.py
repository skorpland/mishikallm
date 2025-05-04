import hashlib
import json

from mishikallm.types.router import CredentialMishikaLLMParams


def get_mishikallm_params_sensitive_credential_hash(mishikallm_params: dict) -> str:
    """
    Hash of the credential params, used for mapping the file id to the right model
    """
    sensitive_params = CredentialMishikaLLMParams(**mishikallm_params)
    return hashlib.sha256(
        json.dumps(sensitive_params.model_dump()).encode()
    ).hexdigest()
