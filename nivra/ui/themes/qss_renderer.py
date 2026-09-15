

def build_stylesheet(theme: dict) -> str:
    colors = theme["colors"]
    shape = theme["shape"]
    spacing = theme["spacing"]

    return f"""
        QMainWindow {{
            background-color: {colors["app_background"]};
        }}

        QWidget {{
            color: {colors["text_primary"]};
        }}

        QTreeView,
        QPlainTextEdit,
        QLineEdit {{
            background-color: {colors["surface"]};
            color: {colors["text_primary"]};

            border: 1px solid {colors["glass_border"]};
            border-radius: {shape["radius_medium"]}px;

            padding: {spacing["sm"]}px;
        }}

        QPushButton {{
            background-color: {colors["surface_alt"]};
            color: {colors["text_primary"]};

            border: 1px solid {colors["glass_border"]};
            border-radius: {shape["radius_small"]}px;

            padding: {spacing["sm"]}px {spacing["md"]}px;
        }}

        QPushButton:hover {{
            background-color: {colors["surface_hover"]};
            border-color: {colors["accent"]};
        }}

        QLineEdit:focus,
        QPlainTextEdit:focus,
        QTreeView:focus {{
            border: 1px solid {colors["accent"]};
        }}
        """