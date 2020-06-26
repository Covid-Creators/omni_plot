from widgets.animations.supported_animations import SUPPORTED_ANIMATIONS

from plugins.abstract_content_editor import AbstractContentEditor
from plugins.abstract_content_widget import AbstractContentWidget

# Add new content types here
SUPPORTED_CONTENT_EDITORS = [
]

for plugin in SUPPORTED_CONTENT_EDITORS:
    assert issubclass(plugin, AbstractContentEditor) or issubclass(plugin, AbstractContentWidget)

SUPPORTED_CONTENT_EDITORS = {
    content.json_key: (content.human_readable_type, content) for content in SUPPORTED_CONTENT_EDITORS}

SUPPORTED_CONTENT_WIDGETS = {**SUPPORTED_CONTENT_EDITORS, **SUPPORTED_ANIMATIONS}
