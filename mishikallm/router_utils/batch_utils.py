import io
import json
from typing import Optional, Tuple, Union


class InMemoryFile(io.BytesIO):
    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name


def replace_model_in_jsonl(
    file_content: Union[bytes, Tuple[str, bytes, str]], new_model_name: str
) -> Optional[InMemoryFile]:
    try:
        # Decode the bytes to a string and split into lines
        # If file_content is a file-like object, read the bytes
        if hasattr(file_content, "read"):
            file_content_bytes = file_content.read()  # type: ignore
        elif isinstance(file_content, tuple):
            file_content_bytes = file_content[1]
        else:
            file_content_bytes = file_content

        # Decode the bytes to a string and split into lines
        if isinstance(file_content_bytes, bytes):
            file_content_str = file_content_bytes.decode("utf-8")
        else:
            file_content_str = file_content_bytes
        lines = file_content_str.splitlines()
        modified_lines = []
        for line in lines:
            # Parse each line as a JSON object
            json_object = json.loads(line.strip())

            # Replace the model name if it exists
            if "body" in json_object:
                json_object["body"]["model"] = new_model_name

            # Convert the modified JSON object back to a string
            modified_lines.append(json.dumps(json_object))

        # Reassemble the modified lines and return as bytes
        modified_file_content = "\n".join(modified_lines).encode("utf-8")
        return InMemoryFile(modified_file_content, name="modified_file.jsonl")  # type: ignore

    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        return None


def _get_router_metadata_variable_name(function_name) -> str:
    """
    Helper to return what the "metadata" field should be called in the request data

    For all /thread or /assistant endpoints we need to call this "mishikallm_metadata"

    For ALL other endpoints we call this "metadata
    """
    ROUTER_METHODS_USING_MISHIKALLM_METADATA = set(["batch", "generic_api_call"])
    if function_name in ROUTER_METHODS_USING_MISHIKALLM_METADATA:
        return "mishikallm_metadata"
    else:
        return "metadata"
