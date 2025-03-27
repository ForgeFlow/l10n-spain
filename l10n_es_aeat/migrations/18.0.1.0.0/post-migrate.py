import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    query = """
        INSERT INTO certificate.key (name, content)
        SELECT
            'Key for AEAT Cert ' || id AS name,
            decode(private_key, 'base64') AS content
        FROM l10n_es_aeat_certificate
        WHERE private_key IS NOT NULL;

        INSERT INTO certificate.certificate (name, private_key_id, date_start, date_end, content)
        SELECT
            'AEAT Cert ' || id AS name,
            (SELECT id FROM certificate.key WHERE name = 'Key for AEAT Cert ' || cert.id) AS private_key_id,
            date_start,
            date_end,
            CASE
                WHEN public_key IS NOT NULL THEN encode(public_key, 'base64')
                ELSE ''
            END AS content
        FROM l10n_es_aeat_certificate cert;
        """
    cr.execute(query)
