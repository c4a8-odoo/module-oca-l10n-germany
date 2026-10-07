# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDin5008Footer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write(
            {
                "phone": "+49 30 123456",
                "vat": "DE123456789",
                "external_report_layout_id": cls.env.ref(
                    "l10n_din5008.external_layout_din5008"
                ).id,
                "report_footer": '<p>Tel. <t t-out="object.phone">-</t></p>',
                "report_header": '<p>Call <t t-out="object.phone"/></p>',
                "company_details": '<p>Phone <t t-out="object.phone"/></p>',
            }
        )
        cls.env["ir.ui.view"].create(
            {
                "name": "l10n_din5008_footer.test_lines",
                "type": "qweb",
                "inherit_id": cls.env.ref("l10n_de_report_footer.footer_lines").id,
                "mode": "extension",
                "arch": """
                    <xpath expr="//t[@name='l10n_de_report_footer_lines']"
                           position="inside">
                        <li class="test_footer_line">Amtsgericht Berlin HRB 1</li>
                    </xpath>
                """,
            }
        )

    def test_preview_footer(self):
        with Form(self.env["base.document.layout"]) as wizard:
            self.assertEqual(
                wizard.report_layout_id,
                self.env.ref("l10n_din5008.report_layout_din5008"),
            )
            preview = wizard.preview
        self.assertIn("din_page footer", preview)
        self.assertIn("Tel. +49 30 123456", preview)
        self.assertIn("Call +49 30 123456", preview)
        self.assertIn("Phone +49 30 123456", preview)
        self.assertNotIn("t-out=", preview)
        # the footer lines are printed before the VAT number
        self.assertLess(
            preview.index("Amtsgericht Berlin HRB 1"), preview.index("DE123456789")
        )
