import json
from typing import List, Dict, Any
from src.data.models import Email
from src.rules.predicates import get_predicate
from src.rules.actions import Action, apply_action

class RuleMatcher:
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = rules

    def match(self, email: Email) -> List[Dict[str, Any]]:
        return [rule for rule in self.rules if self.rule_matches(rule, email)]

    def rule_matches(self, rule: Dict[str, Any], email: Email) -> bool:
        conditions = rule['conditions']
        predicate = rule['predicate'].upper()
        
        results = [self.condition_matches(condition, email) for condition in conditions]
        
        if predicate == 'ALL':
            return all(results)
        elif predicate == 'ANY':
            return any(results)
        else:
            raise ValueError(f"Invalid rule predicate: {predicate}")

    def condition_matches(self, condition: Dict[str, str], email: Email) -> bool:
        field = condition['field']
        predicate = condition['predicate']
        value = condition['value']

        email_value = getattr(email, field)
        predicate_func = get_predicate(predicate)
        
        return predicate_func(email_value, value)




class RuleProcessor:
    def __init__(self, rule_matcher: RuleMatcher, gmail_service: Any):
        self.rule_matcher = rule_matcher
        self.gmail_service = gmail_service

    @classmethod
    def from_file(cls, rules_file: str, gmail_service: Any):
        with open(rules_file, 'r') as f:
            rules_data = json.load(f)
        rule_matcher = RuleMatcher(rules_data['rules'])
        return cls(rule_matcher, gmail_service)

    def process_email(self, email: Email) -> None:
        matching_rules = self.rule_matcher.match(email)
        for rule in matching_rules:
            self.apply_actions(rule, email)

    def apply_actions(self, rule: Dict[str, Any], email: Email) -> None:
        for action in rule['actions']:
            try:
                action_enum = Action[action['type'].upper()]
                parameters = action.get('parameters', {})
                apply_action(action_enum, email, self.gmail_service, parameters)
            except KeyError:
                raise ValueError(f"Invalid action type: {action['type']}")
