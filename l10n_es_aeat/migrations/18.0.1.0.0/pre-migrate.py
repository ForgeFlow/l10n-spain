import base64
import json

from openupgradelib import openupgrade


def _save_certificates(env):
    cr = env.cr
    cr.execute("""
        SELECT id, company_id, name, state, date_start, date_end,
        public_key, private_key
        FROM l10n_es_aeat_certificate
    """)
    certificates = cr.fetchall()
    stored_data = {}
    for cert in certificates:
        (
            cert_id,
            company_id,
            name,
            state,
            date_start,
            date_end,
            public_key,
            private_key_path,
        ) = cert
        private_key_content = ""
        if private_key_path:
            try:
                with open(private_key_path, "rb") as f:
                    private_key_content = base64.b64encode(f.read()).decode()
            except FileNotFoundError:
                private_key_content = ""
        stored_data[str(cert_id)] = {
            "company_id": company_id,
            "name": name,
            "state": state,
            "date_start": str(date_start) if date_start else None,
            "date_end": str(date_end) if date_end else None,
            "public_key": public_key or "",
            "private_key": private_key_content,
        }
    env["ir.config_parameter"].set_param(
        "l10n_es_aeat_certificate_migration_data", json.dumps(stored_data)
    )


@openupgrade.migrate()
def migrate(env, version):
    _save_certificates(env)
