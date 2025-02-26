import csv
from odoo.tools import file_open

def import_fiscal_position_tax(env):
    concerned_company_ids = [
        company.id
        for company in env.companies
        if company.chart_template and company.chart_template.startswith('es_')
    ]
    if not concerned_company_ids:
        return
    fiscal_positions = env['account.fiscal.position'].search(env['account.fiscal.position']._check_company_domain(concerned_company_ids))
    taxes = env['account.tax'].search(env['account.tax']._check_company_domain(concerned_company_ids))

    xmlid2fp = {
        xml_id.split('.')[1].split('_', maxsplit=1)[1]: env['account.fiscal.position'].browse(record)
        for record, xml_id in fiscal_positions.get_external_id().items() if xml_id.startswith('account.')
    }

    xmlid2tax = {
        xml_id.split('.')[1].split('_', maxsplit=1)[1]: env['account.tax'].browse(record)
        for record, xml_id in taxes.get_external_id().items() if xml_id.startswith('account.')
    }

    csv_path = 'l10n_es_dua/data/template/account.fiscal.position.tax-es_common.csv'
    with file_open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            position = xmlid2fp.get(row['position_id'].split('.')[-1:][0])
            tax_src = xmlid2tax.get(row['tax_src_id'].split('.')[-1:][0])
            tax_dest = xmlid2tax.get(row['tax_dest_id'].split('.')[-1:][0])

            if not position or not tax_src or not tax_dest:
                continue

            env['account.fiscal.position.tax'].create({
                'position_id': position.id,
                'tax_src_id': tax_src.id,
                'tax_dest_id': tax_dest.id,
            })

def _l10n_es_dua_post_init(env):
    import_fiscal_position_tax(env)
