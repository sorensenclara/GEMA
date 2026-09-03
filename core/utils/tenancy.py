def resolve_company(obj):
    """Recorre la relación del objeto hasta encontrar su Company, sin atarse
    a una ruta exacta de FK (funciona tanto si `company` está directo en el
    objeto como si solo está en su `cliente`/`matafuegos` asociado)."""
    company = getattr(obj, "company", None)
    if company:
        return company
    cliente = getattr(obj, "cliente", None)
    if cliente is not None:
        company = getattr(cliente, "company", None)
        if company:
            return company
    matafuegos = getattr(obj, "matafuegos", None)
    if matafuegos is not None:
        return resolve_company(matafuegos)
    return None
