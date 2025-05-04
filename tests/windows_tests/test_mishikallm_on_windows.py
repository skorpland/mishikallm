
import asyncio
import os
import subprocess
import sys
import time
import traceback
import platform

import pytest

sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path

def test_using_mishikallm_on_windows():
    """Test that MishikaLLM can be imported on Windows systems."""
    
    try:
        import mishikallm
        print(f"mishikallm imported successfully on Windows ({platform.system()} {platform.release()})")

        response = mishikallm.completion(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "This should never fail. Email ishaan@berri.ai if this test ever fails."}
            ],
            mock_response="Hello, how are you?"
        )
        print(response)
    except Exception as e:
        pytest.fail(
            f"Error occurred on Windows: {e}. Installing mishikallm on Windows failed."
        )

