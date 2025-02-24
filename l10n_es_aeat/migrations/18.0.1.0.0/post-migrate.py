import base64
import binascii
import json
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Restores AEAT certificate data into the new schema."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    migration_data = env["ir.config_parameter"].get_param(
        "l10n_es_aeat_certificate_migration_data"
    )
    if not migration_data:
        raise ValueError("No AEAT certificate migration data found")

    migration_data = json.loads(migration_data)

    for cert_id, cert_data in migration_data.items():
        private_key_data = cert_data.get("private_key", "")
        date_start = cert_data.get("date_start")
        date_end = cert_data.get("date_end")
        public_key_path = cert_data.get("public_key", "")
        try:
            private_key_bytes = private_key_data.encode() if private_key_data else None
        except binascii.Error:
            private_key_bytes = None
        if public_key_path:
            try:
                with open(public_key_path, "rb") as f:
                    public_key_content = f.read()
            except FileNotFoundError:
                _logger.info("Public key file not found")
        key_id = (
            env["certificate.key"].create(
                {
                    "name": f"Key for AEAT Cert {cert_id}",
                    "content": private_key_bytes or b"",
                }
            )
            if private_key_bytes
            else None
        )
        cert_id_new = env["certificate.certificate"].create(
            {
                "name": f"AEAT Cert {cert_id}",
                "private_key_id": key_id.id if key_id else False,
                "date_start": date_start,
                "date_end": date_end,
                "content": base64.b64encode(public_key_content).decode()
                if public_key_content
                else "",
            }
        )
        env["l10n.es.aeat.certificate"].browse(int(cert_id)).write(
            {"certificate_id": cert_id_new.id}
        )
        # Clean up stored migration data
        env["ir.config_parameter"].sudo().set_param(
            "l10n_es_aeat_certificate_migration_data", ""
        )
