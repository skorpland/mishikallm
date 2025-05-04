from mishikallm.mishikallm_core_utils.duration_parser import get_next_standardized_reset_time

from datetime import datetime, timezone
def get_budget_reset_timezone():
    """
    Get the budget reset timezone from general_settings.
    Falls back to UTC if not specified.
    """
    # Import at function level to avoid circular imports
    from mishikallm.proxy.proxy_server import general_settings
    if general_settings:
        mishikallm_settings = general_settings.get("mishikallm_settings", {})
        if mishikallm_settings and "timezone" in mishikallm_settings:
            return mishikallm_settings["timezone"]
    
    return "UTC"


def get_budget_reset_time(budget_duration: str):
    """
    Get the budget reset time from general_settings.
    Falls back to UTC if not specified.
    """
    reset_at = get_next_standardized_reset_time(
        duration=budget_duration, 
        current_time=datetime.now(timezone.utc),
        timezone_str=get_budget_reset_timezone()
    )
    return reset_at