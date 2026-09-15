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

        QWidget#workspaceHeader,
        QWidget#outputPanel,
        QWidget#pulsePanel {{
            background-color: {colors["surface"]};
            border: 1px solid {colors["glass_border"]};
            border-radius: {shape["radius_large"]}px;
        }}

        QLabel#workspaceTitle,
        QLabel#panelTitle {{
            color: {colors["text_primary"]};
            font-weight: 600;
        }}

        QLabel#statusText {{
            color: {colors["text_muted"]};
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

        QHeaderView::section {{
            background-color: {colors["surface_alt"]};
            color: {colors["text_secondary"]};
            border: none;
            border-bottom: 1px solid {colors["glass_border"]};
            padding: {spacing["sm"]}px;
        }}

        QSplitter::handle {{
            background-color: {colors["glass_border"]};
        }}

        QSplitter::handle:horizontal {{
            width: 2px;
        }}

        QSplitter::handle:vertical {{
            height: 2px;
        }}

        QSplitter::handle:hover {{
            background-color: {colors["accent"]};
        }}

        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background: {colors["surface_hover"]};
            border-radius: 5px;
            min-height: 28px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {colors["accent_soft"]};
        }}

        QScrollBar::handle:vertical:pressed {{
            background: {colors["accent"]};
        }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{
            background: transparent;
        }}

        QScrollBar:horizontal {{
            background: transparent;
            height: 10px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background: {colors["surface_hover"]};
            border-radius: 5px;
            min-width: 28px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {colors["accent_soft"]};
        }}

        QScrollBar::handle:horizontal:pressed {{
            background: {colors["accent"]};
        }}

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal {{
            background: transparent;
        }}

        QTreeView::item {{
            padding: {spacing["xs"]}px {spacing["sm"]}px;
            border-radius: {shape["radius_small"]}px;
        }}

        QTreeView::item:hover {{
            background-color: {colors["surface_hover"]};
        }}

        QTreeView::item:selected {{
            background-color: {colors["accent_soft"]};
            color: {colors["text_primary"]};
        }}

        QTreeView::item:selected:active {{
            background-color: {colors["accent_soft"]};
            color: {colors["text_primary"]};
        }}
    """
