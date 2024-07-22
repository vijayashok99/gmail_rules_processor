import json
from typing import List, Dict, Any
from src.data.models import Email
from src.rules.predicates import get_predicate
from src.rules.actions import Action, apply_action

class RuleProcessor:
    def __init__(self, rules_file: str):
        self.rules = self.load_rules(rules_file)

    def load_rules(self, rules_file: str) -> List[Dict[str, Any]]:
        with open(rules_file, 'r') as f:
            rules_data = json.load(f)
        return rules_data['rules']

    def process_email(self, email: Email, gmail_service: Any) -> None:
        for rule in self.rules:
            # print("Rule - ", rule)
            if self.rule_matches(rule, email):
                self.apply_actions(rule, email, gmail_service)

    def rule_matches(self, rule: Dict[str, Any], email: Email) -> bool:
        conditions = rule['conditions']
        predicate = rule['predicate'].upper()
        
        results = [self.condition_matches(condition, email) for condition in conditions]
        
        # print(results)
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

    def apply_actions(self, rule: Dict[str, Any], email: Email, gmail_service: Any) -> None:
        for action in rule['actions']:
            try:
                action_enum = Action[action['type'].upper()]
                parameters = action.get('parameters', {})
                apply_action(action_enum, email, gmail_service, parameters)
            except KeyError:
                raise ValueError(f"Invalid action type: {action['type']}")
