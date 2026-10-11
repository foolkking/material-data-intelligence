"""Account-bound adapter for legacy planner callers; never stores credentials."""
from types import SimpleNamespace
from mdi_api.user_models import validate_user_selection, resolve_user_selection


class AccountModelProvider:
    def __init__(self, user_id: str, *, provider: str, model: str, thinking_mode: str = "standard"):
        self._selection = validate_user_selection(user_id, {
            "provider": provider, "model": model, "thinking_mode": thinking_mode,
        })
        self.meta = SimpleNamespace(name=provider, model=model)

    def complete_json(self, *, messages, user_config=None, purpose=None):
        adapter, config = resolve_user_selection(self._selection)
        return adapter.complete_json(messages=messages, user_config=config, purpose=purpose)

    def generate_plan(self, request, *, tools, data_profile, user_config=None):
        from mdi_llm.planner_prompt import build_planner_prompt
        system, user = build_planner_prompt(request, tools=tools, data_profile=data_profile)
        return self.complete_json(messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
