def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError

    uploaded = value.name
    uploaded_lower = uploaded.lower()

    # convert
    if uploaded_lower.endswith("xls"):
        pass
    elif uploaded_lower.endswith("xlsx"):
        pass
    elif uploaded_lower.endswith("csv"):
        pass
    else:
        raise ValidationError(u'Unsupported file extension: {0} (expect xls, csv, xlsx)'.format(value.name))
