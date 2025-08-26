import json
import re

def parse_persona_template(template_content: str) -> dict:
    """
    Parses a specially formatted text template for a persona's speech style
    and converts it into a structured dictionary.

    Args:
        template_content: A string containing the entire content of the
                          persona template .txt file.

    Returns:
        A dictionary representing the structured persona data.
    """
    persona_dict = {}
    current_section_key = None
    lines = template_content.strip().split('\n')

    # Regex to identify main section headers like "1. Foundational Voice Attributes"
    section_header_pattern = re.compile(r'^\d+\.\s+(.*)')

    for line in lines:
        line = line.strip()
        if not line:
            continue # Skip empty lines

        # Check if the line is a main section header
        section_match = section_header_pattern.match(line)
        if section_match:
            # Convert section name to snake_case for the JSON key
            # E.g., "Foundational Voice Attributes" -> "foundational_voice_attributes"
            section_name = section_match.group(1).lower().replace(' ', '_')
            current_section_key = section_name
            persona_dict[current_section_key] = {}
            continue

        # Check if the line is a field definition (starts with '-')
        if line.startswith('-'):
            if not current_section_key:
                # This field is outside any section, which is an error
                print(f"Warning: Found field outside of a section: {line}")
                continue

            # Split the line into key and value at the first colon
            parts = line.split(':', 1)
            if len(parts) == 2:
                # Clean up the key: remove '-', strip whitespace, convert to snake_case
                key = parts[0].replace('-', '').strip().lower().replace(' ', '_')
                
                # Clean up the value: strip whitespace and remove surrounding brackets
                value = parts[1].strip()
                if value.startswith('[') and value.endswith(']'):
                    value = value[1:-1]
                
                persona_dict[current_section_key][key] = value
            else:
                print(f"Warning: Malformed field line ignored: {line}")

    return persona_dict

# --- Example Usage ---

# This is a small sample of the kind of text that would be in the .txt file.
example_template = """
1. Foundational Voice Attributes

- Core Disposition: [Calm and reassuring]
- Conversational Goal: [To provide clear information]

2. Profanity Usage

- Frequency and Context: [Never uses profanity]
- Vocabulary: [None]

"""

# Call the function with the example template string
parsed_data = parse_persona_template(example_template)

# Print the resulting dictionary, formatted nicely as JSON
print(json.dumps(parsed_data, indent=2))

# Expected Output:
# {
#   "foundational_voice_attributes": {
#     "core_disposition": "Calm and reassuring",
#     "conversational_goal": "To provide clear information"
#   },
#   "profanity_usage": {
#     "frequency_and_context": "Never uses profanity",
#     "vocabulary": "None"
#   }
# }