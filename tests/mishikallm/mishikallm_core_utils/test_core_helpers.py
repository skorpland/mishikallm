import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(
    0, os.path.abspath("../../..")
)  # Adds the parent directory to the system path

from mishikallm.mishikallm_core_utils.core_helpers import get_mishikallm_metadata_from_kwargs


def test_get_mishikallm_metadata_from_kwargs():
    kwargs = {
        "mishikallm_params": {
            "mishikallm_metadata": {},
            "metadata": {"user_api_key": "1234567890"},
        },
    }
    assert get_mishikallm_metadata_from_kwargs(kwargs) == {"user_api_key": "1234567890"}
