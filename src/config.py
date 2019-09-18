from os.path import join

from cerberus import Validator
from toml import decoder, load

from src.exceptions import SchemaError, ValidationError


def load_config(name: str = "settings"):
    """Load TOML config file and validate it with the associated schema"""

    # Enforce standard directory structure and a schema for each config file
    filename = f"{name}.toml"
    schema = load(join("config", "schemas", filename))

    # Allow non-existent files to handle default-valued only schemas
    file_not_found = None
    try:
        config = load(join("config", filename))
    except FileNotFoundError as error:
        config, file_not_found = {}, error

    validator = Validator(_preprocess_schema_rec(schema, name))
    if not validator.validate(config):
        if file_not_found is not None:
            raise FileNotFoundError(file_not_found)
        else:
            errors = validator.errors
            raise ValidationError(_format_validation_errors(name, errors))

    config_with_empty_sections = _create_empty_sections_rec(schema, config)

    return validator.normalized(config_with_empty_sections)


# ---------------------------- Private functions ------------------------------
# ! Recursive for arbitrary nesting (use shallow configs to avoid overflow)
def _preprocess_schema_rec(schema, name):
    for key, value in schema.items():
        # Cerberus requires some extra fields for nested schemas
        if type(value) is dict:
            schema[key] = dict(
                type="dict",
                allow_unknown=True,
                required=_is_section_required_rec(value),
                schema=_preprocess_schema_rec(value, name),
            )

        # Shorthand for fields with a default value and no other options
        elif not issubclass(type(value), decoder.InlineTableDict):
            schema[key] = dict(type=_get_cerberus_type(value), default=value)

        # Infer required type from default value
        elif "default" in value:
            if "type" in value:
                err = f'Redundant "type" field for key "{key}" in "{name}"'
                raise SchemaError(err)
            schema[key]["type"] = _get_cerberus_type(value["default"])

        elif "type" not in value:
            err = f'No type or default set for key "{key}" in "{name}"'
            raise SchemaError(err)

        # Fields with no default value should be required by default
        # This reduces both null checks and unused fields
        elif "required" not in value:
            value["required"] = True

    return schema


# ! Recursive for arbitrary nesting (use shallow configs to avoid overflow)
def _is_section_required_rec(section):
    for key, value in section.items():
        if issubclass(type(value), decoder.InlineTableDict):
            if "required" not in value or value["required"]:
                return True
        elif type(value) is dict and _is_section_required_rec(value):
            return True
    return False


# Cerberus type names, found in validator.BareValidator.types_mapping (v1.3.1)
def _get_cerberus_type(value):
    types = {"bool": "boolean", "int": "integer", "str": "string"}
    return types.get(type(value).__name__, type(value).__name__)


# Cerberus does not create default values for missing sections
# ! Recursive for arbitrary nesting (use shallow configs to avoid overflow)
def _create_empty_sections_rec(schema, config):
    for key, value in schema.items():
        if value["type"] == "dict" and key not in config:
            config[key] = _create_empty_sections_rec(value["schema"], {})
    return config


# Improve legibility of validation errors reported by Cerberus
def _format_validation_errors(name, errors):
    newline = "\n"  # Can't use "\n" in f-strings

    # ! Recursive for arbitrary nesting (use shallow configs to avoid overflow)
    def format_rec(errors, indent=1):
        msg = ""
        for key, values in errors.items():
            print(values)
            # There is always at least one error
            if type(values[0]) is dict:
                msg += f"{'  ' * indent}- {key}:{newline}"
                msg += "".join(format_rec(e, indent + 1) for e in values)
            else:
                msg += f"{'  ' * indent}- {key}: {', '.join(values)}{newline}"
        return msg

    msg = format_rec(errors)[:-1]  # Remove trailing newline

    raise ValidationError(f'found in "{name}" config file:{newline}{msg}')
