from typing import Literal

from rendercv.themes.options import ThemeOptions, theme_options_theme_field_info

theme_options_theme_field_info.default = "classic"


class EngineeringenhancedThemeOptions(ThemeOptions):
    theme: Literal["engineeringenhanced"] = theme_options_theme_field_info
