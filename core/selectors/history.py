from django.apps import apps

ALLOWED_ORDER_FIELDS = {"-history_date", "history_date"}


def resolve_history_model(app_label, model_name):
    """Returns the model class if it exists and has change history enabled, else None."""
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return None
    if not hasattr(model, "history"):
        return None
    return model


def list_history_for_object(obj, order_by="-history_date"):
    """Historical records for the given AuditModel instance."""
    if order_by not in ALLOWED_ORDER_FIELDS:
        order_by = "-history_date"
    return obj.history.select_related("history_user").order_by(order_by)


def attach_diffs(records):
    """Annotates each historical record with has_previous_record/computed_changes
    (its field-level diff against the immediately preceding version). Read-only —
    only sets in-memory attributes on already-fetched records, no persistence."""
    for record in records:
        previous = record.prev_record
        record.has_previous_record = previous is not None
        record.computed_changes = (
            record.diff_against(previous).changes if previous else []
        )
    return records
