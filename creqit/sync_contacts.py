import creqit

# Her doctype için şirket alanını eşleyen sözlük
COMPANY_FIELD_MAP = {
    "Leads": "company",
    "Opportunity": "account_name"
}

@creqit.whitelist()
def sync_table_orgl(doc, method):
    this_doctype = doc.doctype
    other_doctype = "Opportunity" if this_doctype == "Leads" else "Leads"

    this_company_field = COMPANY_FIELD_MAP[this_doctype]
    other_company_field = COMPANY_FIELD_MAP[other_doctype]

    company_value = getattr(doc, this_company_field, None)
    if not company_value:
        return

    current_contacts = {(row.email, row.phone) for row in doc.table_orgl}

    # Diğer doctype içinde aynı şirkete sahip kayıtları bul
    other_docs = creqit.get_all(
        other_doctype,
        filters={other_company_field: company_value},
        fields=["name"]
    )

    for d in other_docs:
        other_doc = creqit.get_doc(other_doctype, d.name)
        updated = False

        # Diğer doc'taki her satırı kontrol et
        for row in list(other_doc.table_orgl):
            if (row.email, row.phone) not in current_contacts:
                other_doc.remove(row)
                updated = True

        if updated:
            other_doc.save(ignore_permissions=True)
            creqit.db.commit()
