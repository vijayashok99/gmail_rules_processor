from datetime import datetime, timedelta, timezone

def contains(field_value: str, condition_value: str) -> bool:
    return condition_value.lower() in field_value.lower()

def does_not_contain(field_value: str, condition_value: str) -> bool:
    return not contains(field_value, condition_value)

def equals(field_value: str, condition_value: str) -> bool:
    return field_value.lower() == condition_value.lower()

def does_not_equal(field_value: str, condition_value: str) -> bool:
    return not equals(field_value, condition_value)

def ensure_offset_aware(dt):
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def parse_time_value(value: str) -> timedelta:
    number, unit = value.split()
    number = int(number)
    if unit.lower() in ['day', 'days']:
        return timedelta(days=number)
    elif unit.lower() in ['hour', 'hours']:
        return timedelta(hours=number)
    elif unit.lower() in ['minute', 'minutes']:
        return timedelta(minutes=number)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

def greater_than(field_value: datetime, condition_value: str) -> bool:
    time_delta = parse_time_value(condition_value)
    now = datetime.now(timezone.utc)
    field_value = ensure_offset_aware(field_value)
    return (now - field_value) > time_delta

def less_than(field_value: datetime, condition_value: str) -> bool:
    time_delta = parse_time_value(condition_value)
    now = datetime.now(timezone.utc)
    field_value = ensure_offset_aware(field_value)
    return (now - field_value) < time_delta

PREDICATES = {
    'contains': contains,
    'does_not_contain': does_not_contain,
    'equals': equals,
    'does_not_equal': does_not_equal,
    'greater_than': greater_than,
    'less_than': less_than,
}

def get_predicate(predicate_name: str):
    predicate = PREDICATES.get(predicate_name)
    if not predicate:
        raise ValueError(f"Invalid predicate: {predicate_name}")
    return predicate