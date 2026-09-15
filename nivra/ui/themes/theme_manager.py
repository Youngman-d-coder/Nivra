import json
from pathlib import Path


class ThemeManager:
    def __init__(self) -> None:
        self._builtin_dir = Path(__file__).parent / "builtin"

    def load_builtin_theme(self, theme_id: str) -> dict:
        theme_path = self._builtin_dir / f"{theme_id}.json"

        if not theme_path.exists():
            raise FileNotFoundError(f"Theme file not found: {theme_path}")
        
        validate_theme_data = json.loads(
            theme_path.read_text(encoding="utf-8")
        )

        self._validate_theme(validate_theme_data)
        return validate_theme_data

    def _validate_theme(self, theme_data: dict) -> None:
        section_keys = {
            "colors",
            "shape",
            "spacing",
            "motion"
        }

        required_keys = {
            "id",
            "name",
            "version",
            "colors",
            "shape",
            "spacing",
            "motion"
        }

        required_color_keys = {
            "app_background",
            "surface",
            "surface_alt",
            "surface_hover",
            "glass_border",
            "glass_highlight",
            "glass_shadow",
            "text_primary",
            "text_secondary",
            "text_muted",
            "accent",
            "accent_hover",
            "accent_soft",
            "success",
            "warning",
            "error",
        }

        required_shape_keys = {
            "radius_small",
            "radius_medium",
            "radius_large",
        }

        required_spacing_keys = {
            "xs",
            "sm",
            "md",
            "lg",
            "xl",
        }

        required_motion_keys = {
            "fast",
            "normal",
            "slow",
        }

        if not isinstance(theme_data, dict):
            raise ValueError("Theme data must be a JSON object.")

        missing_keys = required_keys - theme_data.keys()
        if missing_keys:
            raise ValueError(
                f"Theme is missing required keys: {missing_keys}"
            )

        for section in section_keys:
            if not isinstance(theme_data[section], dict):
                raise ValueError(
                    f"Theme section '{section}' must be a JSON object."
                )

        missing_colors = required_color_keys - theme_data["colors"].keys()
        if missing_colors:
            raise ValueError(
                f"Theme colors are missing required keys: {missing_colors}"
            )

        missing_shape = required_shape_keys - theme_data["shape"].keys()
        if missing_shape:
            raise ValueError(
                f"Theme shape is missing required keys: {missing_shape}"
            )

        missing_spacing = required_spacing_keys - theme_data["spacing"].keys()
        if missing_spacing:
            raise ValueError(
                f"Theme spacing is missing required keys: {missing_spacing}"
            )

        missing_motion = required_motion_keys - theme_data["motion"].keys()
        if missing_motion:
            raise ValueError(
                f"Theme motion is missing required keys: {missing_motion}"
            )


if __name__ == "__main__":
    manager = ThemeManager()
    theme = manager.load_builtin_theme("nivra_glass")
    import copy

    bad_theme = copy.deepcopy(theme)
    bad_theme["shape"].pop("radius_medium")
    manager._validate_theme(bad_theme)

    print(theme["name"])
    print(theme["colors"]["accent"])
    print(theme["spacing"]["sm"])