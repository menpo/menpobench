from pyrx import StrType, RecType, ArrType, AnyType


class RxParseError(ValueError):
    pass


# If we are making an incorrect assumption
class RxCheckInternalLogicError(ValueError):
    pass


def _expected_found_str(e, f):
    return "expected {}, found {}".format(e, _f(f))


# format single strings with quotes, pass through anything else
def _f(x):
    return "'{}'".format(x) if isinstance(x, str) else x


def _set_str(s):
    if len(s) == 1:
        (item,) = s
        return _f(item)
    else:
        return "{{{}}}".format(', '.join([_f(i) for i in s]))


def _recursive_check(s, c):
    if s.check(c):  # everything is fine down this path
        return True
    # there is a problem

    if isinstance(s, RecType):
        if not isinstance(c, dict):
            raise RxParseError(_expected_found_str('dict', c))
        present = set(c.keys())
        extra = present - s.known
        if len(extra) != 0:
            key_str = 'key' if len(extra) == 1 else 'keys'
            allowed_key_str = 'key is' if len(s.known) == 1 else 'keys are'
            raise RxParseError("Illegal {} {} - "
                               "allowed {} {}".format(
                key_str, _set_str(extra),
                allowed_key_str, _set_str(s.known)))
        missing = set(s.required.keys()) - present
        if len(missing) != 0:
            key_str = 'key' if len(missing) == 1 else 'keys'
            required_key_str = 'key is' if len(s.required) == 1 else 'keys are'
            raise RxParseError("Missing {} {} - "
                               "required {} {}".format(
                key_str, _set_str(missing),
                required_key_str, _set_str(s.required)))
        errors = []
        for key in present:
            s_x = s.required if key in s.required else s.optional
            s_n, c_n = s_x[key], c[key]
            try:
                _recursive_check(s_n, c_n)
            except RxParseError as e:
                key_error_str = "{}: {} <- {}".format(key, c_n, e.message)
                errors.append(key_error_str)
        if len(errors) > 0:
            raise RxParseError("\n".join(errors))
        else:
            raise RxCheckInternalLogicError("Exhaustively checked problematic "
                                            "dict and found no errors")

    elif isinstance(s, StrType):
        if not isinstance(c, str):
            raise RxParseError(_expected_found_str('str', c))
        if s.value is not None and c != s.value:
            raise RxParseError("{} != {}".format(_f(c), _f(s.value)))
        raise RxParseError("Something wrong with str {} but "
                           "don't know what".format(_f(c)))

    elif isinstance(s, ArrType):
        if not isinstance(c, list):
            raise RxParseError(_expected_found_str('list', c))
        arr_s = s.content_schema
        for i in c:
            _recursive_check(arr_s, i)

    elif isinstance(s, AnyType):
        # all errors may be the same, only show one
        errors = set()
        for alt in s.alts:
            try:
                _recursive_check(alt, c)
            except RxParseError as e:
                # this any branch is not allowed
                # save the error messages up
                errors.add(e.message)
                pass
            else:
                # shouldn't ever hit this - we are only here because there is
                # a problem with this node, and we can't find it.
                raise RxCheckInternalLogicError("exhaustively checked "
                                                "problematic any time and "
                                                "found allowed option")
        # we tried all options and none were valid
        raise RxParseError("{} doesn't match allowed "
                           "values: {}".format(_f(c), ", ".join(errors)))

    else:
        print(s)


def schema_error_report(schema, config):
    try:
        _recursive_check(schema, config)
    except RxParseError as e:
        return str(e)
    return 'Schema is valid'


def schema_is_valid(schema, config):
    return schema.check(config)
