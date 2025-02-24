# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestKeysCertificates(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.subject = cls.issuer = x509.Name(
            [
                x509.NameAttribute(x509.oid.NameOID.COUNTRY_NAME, "BE"),
                x509.NameAttribute(
                    x509.oid.NameOID.STATE_OR_PROVINCE_NAME, "Brabant wallon"
                ),
                x509.NameAttribute(x509.oid.NameOID.LOCALITY_NAME, "Grand Rosière"),
                x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, "Odoo S.A."),
                x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, "odoo.com"),
            ]
        )

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.test_key_1 = cls.env["certificate.key"].create(
            {
                "name": "Test key",
                "content": base64.b64encode(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                ),
            }
        )

        cls.certificate_1 = (
            x509.CertificateBuilder()
            .subject_name(cls.subject)
            .issuer_name(cls.issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc) - timedelta(days=10))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=10))
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName("localhost")]),
                critical=False,
            )
            .sign(private_key, hashes.SHA256())
        )

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        certificate = cls.env["certificate.certificate"].create(
            {
                "name": "Test AEAT Certificate",
                "content": base64.b64encode(
                    cls.certificate_1.public_bytes(encoding=serialization.Encoding.PEM)
                ),
                "private_key_id": cls.test_key_1.id,
            }
        )
        cls.sii_cert = cls.env["l10n.es.aeat.certificate"].create(
            {
                "certificate_id": certificate.id,
                "state": "active",
            }
        )

    def test_get_certificates(self):
        pem_certificate, private_key = self.sii_cert.get_certificates()
        self.assertEqual(pem_certificate, self.sii_cert.certificate_id.pem_certificate)
        self.assertEqual(
            private_key, self.sii_cert.certificate_id.private_key_id.pem_key
        )

        # Test that an error is raised when no valid certificates exist
        self.sii_cert.state = "draft"
        with self.assertRaises(UserError):
            self.sii_cert.get_certificates()
