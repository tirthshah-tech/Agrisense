"""UI package for AgriSense."""
from ui.dashboard import render_dashboard
from ui.farms import render_farms_page
from ui.crops import render_crops_page
from ui.soil import render_soil_page
from ui.resources import render_resources_page
from ui.fertilizer import render_fertilizer_page
from ui.weather import render_weather_page
from ui.yield_view import render_yield_page
from ui.resource_efficiency import render_resource_efficiency_page
from ui.alerts import render_alerts_page
from ui.data_quality import render_data_quality_page
from ui.system_status import render_system_status_page  # Backward compatibility alias

__all__ = [
    "render_dashboard",
    "render_farms_page",
    "render_crops_page",
    "render_soil_page",
    "render_resources_page",
    "render_fertilizer_page",
    "render_weather_page",
    "render_yield_page",
    "render_resource_efficiency_page",
    "render_alerts_page",
    "render_data_quality_page",
    "render_system_status_page",
]
