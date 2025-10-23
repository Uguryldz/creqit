@creqit.whitelist()
def sync_contact_removal(email, phone=None, from_doctype=None):
    target_doctypes = ["Leads", "Opportunity"]
    if from_doctype in target_doctypes:
        target_doctypes.remove(from_doctype)  # Diğerinden sil

    for doctype in target_doctypes:
        docs = creqit.get_all(doctype, fields=["name"])
        for doc in docs:
            doc_instance = creqit.get_doc(doctype, doc.name)
            new_rows = []
            changed = False
            for row in doc_instance.table_orgl:
                if row.email == email and (not phone or row.phone == phone):
                    changed = True
                    continue
                new_rows.append(row)
            if changed:
                doc_instance.table_orgl = new_rows
                doc_instance.save()
