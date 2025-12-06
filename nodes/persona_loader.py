"""Persona loading node"""
# Use relative imports
from ..utils.persona_utils import (
    load_persona_from_json,
    generate_persona_summary
)
import os
import json


class PersonaLoader:
    """Persona loader (supports file path or JSON string)"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_mode": (["file", "json_string"], {
                    "default": "file",
                    "tooltip": "Select input mode: file=load from file, json_string=enter JSON directly below"
                }),
                "persona_file": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "path/to/persona.json (only used in file mode)"
                }),
                "persona_json": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Complete Persona JSON string (only used in json_string mode)\n\nPaste JSON content directly here, no need for Text Multiline node",
                    "dynamicPrompts": False  # Disable dynamic prompt processing
                }),
                "user_id": ("STRING", {
                    "default": "",
                    "placeholder": "User ID (for logging and output management)"
                }),
            }
        }

    RETURN_TYPES = ("PERSONA", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("persona", "summary", "system_prompt", "user_id")
    FUNCTION = "load"
    CATEGORY = "TwitterChat"
    DESCRIPTION = "Load persona from file path or JSON string (multi-user support)"

    def load(self, input_mode, persona_file, persona_json="", user_id=""):
        """
        Load Character Card persona (supports two modes)

        Args:
            input_mode: "file" or "json_string"
            persona_file: JSON file path (file mode)
            persona_json: JSON string (json_string mode)
            user_id: User ID (for logging and output)

        Returns:
            (persona, summary, system_prompt, user_id)
        """
        try:
            # Load persona based on mode
            if input_mode == "file":
                if not persona_file or not os.path.exists(persona_file):
                    raise ValueError(f"File mode: Please provide valid persona_file path: {persona_file}")
                persona = load_persona_from_json(persona_file)
                print(f"[PersonaLoader] Loaded persona from file: {persona_file}")

            elif input_mode == "json_string":
                if not persona_json or persona_json.strip() == "":
                    raise ValueError("JSON string mode: persona_json cannot be empty")

                # Preprocessing: remove common formatting issues
                persona_json_cleaned = persona_json.lstrip('\ufeff').strip()  # Remove BOM and whitespace

                if not persona_json_cleaned:
                    raise ValueError("Cleaned JSON string is empty")

                # Parse JSON string
                try:
                    persona = json.loads(persona_json_cleaned)
                    print(f"[PersonaLoader] Loaded persona from JSON string (user_id={user_id}, {len(persona_json_cleaned)} characters)")

                except json.JSONDecodeError as e:
                    # Provide detailed error information for debugging
                    error_pos = e.pos if hasattr(e, 'pos') else 0
                    context_start = max(0, error_pos - 100)
                    context_end = min(len(persona_json_cleaned), error_pos + 100)
                    error_context = persona_json_cleaned[context_start:context_end]

                    error_msg = (
                        f"JSON parsing failed: {str(e)}\n"
                        f"Error location: line {e.lineno}, column {e.colno} (position {error_pos})\n"
                        f"Context around error: ...{repr(error_context)}...\n\n"
                        f"Tips:\n"
                        f"- Check if JSON format is correct (use online JSON validator)\n"
                        f"- Ensure it starts with '{{' and ends with '}}'\n"
                        f"- Check if quotes, commas, brackets are matched\n"
                        f"- Original input length: {len(persona_json)} characters, after cleaning: {len(persona_json_cleaned)} characters"
                    )
                    raise ValueError(error_msg)

            else:
                raise ValueError(f"Unsupported input mode: {input_mode}")

            # Validate persona structure
            if "data" not in persona:
                raise ValueError("Persona JSON missing 'data' field, please check format")

            # Generate summary
            summary = generate_persona_summary(persona)

            # Extract system prompt
            system_prompt = persona["data"].get("system_prompt", "")

            # If user_id is empty, try to extract from persona
            if not user_id:
                user_id = persona["data"].get("user_id", "")

            return (persona, summary, system_prompt, user_id)

        except Exception as e:
            raise RuntimeError(f"Failed to load persona: {str(e)}")


# Node registration
NODE_CLASS_MAPPINGS = {
    "PersonaLoader": PersonaLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PersonaLoader": "Load Persona"
}
