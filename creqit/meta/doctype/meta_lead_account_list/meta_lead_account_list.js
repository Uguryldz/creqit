// Copyright (c) 2025, creqit Technologies and contributors
// License: MIT. See LICENSE

creqit.ui.form.on('Meta Lead Account List', {
    refresh(frm) {
        frm.add_custom_button(__('Sync Accounts'), function() {
            creqit.call({
                method: 'creqit.meta.doctype.meta_lead_account_list.meta_lead_account_list.sync_accounts',
                callback: function(r) {
                    if (r.message) {
                        creqit.show_alert({
                            message: __('Processed: {0}, Failures: {1}', [r.message.total_processed, r.message.failures]),
                            indicator: r.message.failures ? 'orange' : 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        });

        // Render accounts table from JSON
        render_accounts_table(frm);
    }
});

function render_accounts_table(frm) {
    const container = frm.get_field('accounts_html').$wrapper.get(0);
    const raw = frm.doc.accounts_json || '[]';
    let rows = [];
    try {
        rows = JSON.parse(raw);
    } catch (e) {
        container.innerHTML = `<div class="text-muted">Invalid accounts JSON</div>`;
        return;
    }

    if (!rows.length) {
        container.innerHTML = `<div class="text-muted">Henüz hesap yok. Sync Accounts ile getiriniz.</div>`;
        return;
    }

    const header = ['Page Name', 'Category', 'Business', 'City', 'Country', 'Tasks'];
    const thead = `<thead><tr>${header.map(h => `<th>${h}</th>`).join('')}</tr></thead>`;
    const tbody = `<tbody>${rows.map(r => `
        <tr>
            <td>${escape_html(r.page_name || '')}</td>
            <td>${escape_html(r.category || '')}</td>
            <td>${escape_html(r.business_name || '')}</td>
            <td>${escape_html(r.city || '')}</td>
            <td>${escape_html(r.country || '')}</td>
            <td>${Array.isArray(r.tasks) ? r.tasks.join(', ') : (r.tasks || '')}</td>
        </tr>
    `).join('')}</tbody>`;

    container.innerHTML = `<div class="table-responsive"><table class="table table-bordered" style="margin-top:8px;">${thead}${tbody}</table></div>`;
}

function escape_html(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}


