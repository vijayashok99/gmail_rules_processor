from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict

class Predicate:
    @staticmethod
    def contains(field_value: str, condition_value: str) -> bool:
        return condition_value.lower() in field_value.lower()

    @staticmethod
    def does_not_contain(field_value: str, condition_value: str) -> bool:
        return not Predicate.contains(field_value, condition_value)

    @staticmethod
    def equals(field_value: str, condition_value: str) -> bool:
        return field_value.lower() == condition_value.lower()

    @staticmethod
    def does_not_equal(field_value: str, condition_value: str) -> bool:
        return not Predicate.equals(field_value, condition_value)

    @staticmethod
    def greater_than(field_value: datetime, condition_value: str) -> bool:
        time_delta = Predicate.parse_time_value(condition_value)
        now = datetime.now(timezone.utc)
        field_value = Predicate.ensure_offset_aware(field_value)
        return (now - field_value) > time_delta

    @staticmethod
    def less_than(field_value: datetime, condition_value: str) -> bool:
        time_delta = Predicate.parse_time_value(condition_value)
        now = datetime.now(timezone.utc)
        field_value = Predicate.ensure_offset_aware(field_value)
        return (now - field_value) < time_delta

    @staticmethod
    def ensure_offset_aware(dt: datetime) -> datetime:
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @staticmethod
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

PREDICATES: Dict[str, Callable] = {
    'contains': Predicate.contains,
    'does_not_contain': Predicate.does_not_contain,
    'equals': Predicate.equals,
    'does_not_equal': Predicate.does_not_equal,
    'greater_than': Predicate.greater_than,
    'less_than': Predicate.less_than,
}

def get_predicate(predicate_name: str) -> Callable:
    predicate = PREDICATES.get(predicate_name)
    if not predicate:
        raise ValueError(f"Invalid predicate: {predicate_name}")
    return predicate