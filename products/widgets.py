from django.forms.widgets import ClearableFileInput
# Using 'as _' below means we can now call gettext_lazy using _()
from django.utils.translation import gettext_lazy as _


class CustomClearableFileInput(ClearableFileInput):
    clear_checkbox_label = _('Remove')
    initial_text = _('Current image')
    input_text = _('')
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'