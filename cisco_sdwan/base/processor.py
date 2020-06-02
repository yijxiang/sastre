
import json
from collections import namedtuple
from copy import deepcopy


Operation = namedtuple('Operation', ['handler_fn', 'param_keys'])


class Processor:
    recipe_file = None
    mandatory_keys = {
    }

    def __init__(self, data, **kwargs):
        self.data = data

    @classmethod
    def validate_recipe_data(cls, recipe_data):
        violations_list = []

        def validate(json_obj, violations, mandatory_keys_dict, bread_crumbs):
            if isinstance(json_obj, dict):
                for key in mandatory_keys_dict:
                    if key not in json_obj:
                        violations.append('{key} @ {crumbs}'.format(key=key, crumbs='/'.join(map(str, bread_crumbs))))
                    else:
                        validate(json_obj[key], violations, mandatory_keys_dict[key], bread_crumbs + [key])

            elif isinstance(json_obj, list):
                for index, elem in enumerate(json_obj):
                    validate(elem, violations, mandatory_keys_dict, bread_crumbs + [index])

            return violations

        return validate(recipe_data, violations_list, cls.mandatory_keys, [])

    @classmethod
    def load(cls, **kwargs):
        try:
            with open(cls.recipe_file, 'r') as read_f:
                data = json.load(read_f)
            assert isinstance(data, list)
        except FileNotFoundError:
            raise ProcessorException('Migration recipe file not found: {file}'.format(file=cls.recipe_file))
        except json.decoder.JSONDecodeError as ex:
            raise ProcessorException('Invalid JSON in recipe file: {file}: {msg}'.format(file=cls.recipe_file, msg=ex))
        except AssertionError:
            raise ProcessorException('Invalid recipe file: {file}: Top level must be a list'.format(
                file=cls.recipe_file)
            )

        # Enforce mandatory_keys
        violations = cls.validate_recipe_data(data)
        if violations:
            raise ProcessorException('Invalid recipe file: {file}: Missing mandatory keys: {details}'.format(
                file=cls.recipe_file, details=', '.join(violations)))

        return cls(data, **kwargs)

    def eval(self, template_obj, new_name):
        migrated_payload = deepcopy(template_obj.data)
        trace_log = []

        return migrated_payload, trace_log


class ProcessorException(Exception):
    """ Exception for Migration Processor errors """
    pass
