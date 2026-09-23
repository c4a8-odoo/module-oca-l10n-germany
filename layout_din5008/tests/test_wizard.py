# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase, tagged

from .common import LayoutDin5008Common


@tagged("post_install", "-at_install")
class TestWizard(LayoutDin5008Common, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_din5008()
        cls.report_layout_a = cls.env.ref("layout_din5008.report_layout_din5008_a")
        cls.report_layout_b = cls.env.ref("layout_din5008.report_layout_din5008_b")
        cls.report_layout_standard = cls.env.ref("web.report_layout_standard")
        cls.paperformat_euro = cls.env.ref("base.paperformat_euro")

    def test_layout_selection_sets_paperformat(self):
        self.company.write(
            {
                "external_report_layout_id": self.env.ref(
                    "web.external_layout_standard"
                ).id,
                "paperformat_id": self.paperformat_euro.id,
            }
        )
        with Form(self.env["base.document.layout"]) as wizard:
            self.assertFalse(wizard.layout_din5008_is_din)
            wizard.report_layout_id = self.report_layout_a
            self.assertTrue(wizard.layout_din5008_is_din)
            self.assertEqual(wizard.paperformat_id, self.paperformat_a)
            wizard.report_layout_id = self.report_layout_b
            self.assertEqual(wizard.paperformat_id, self.paperformat_b)
            wizard.report_layout_id = self.report_layout_standard
            self.assertFalse(wizard.layout_din5008_is_din)
            # the paper format of another layout is not touched
            self.assertEqual(wizard.paperformat_id, self.paperformat_b)

    def test_save_writes_company_fields(self):
        with Form(self.env["base.document.layout"]) as wizard:
            wizard.report_layout_id = self.report_layout_b
            wizard.layout_din5008_fold_marks = False
            wizard.layout_din5008_margin_bottom = 40
            wizard.layout_din5008_remark_zone_height = 12.7
            wizard.layout_din5008_logo_position = "right"
            wizard.layout_din5008_informations_position = "below"
        self.assertEqual(self.company.external_report_layout_id, self.layout_b)
        self.assertEqual(self.company.paperformat_id, self.paperformat_b)
        self.assertFalse(self.company.layout_din5008_fold_marks)
        self.assertEqual(self.company.layout_din5008_margin_bottom, 40)
        self.assertEqual(self.company.layout_din5008_remark_zone_height, 12.7)
        self.assertEqual(self.company.layout_din5008_logo_position, "right")
        self.assertEqual(self.company.layout_din5008_informations_position, "below")

    def test_invalid_margin_rejected(self):
        with self.assertRaises(ValidationError):
            with Form(self.env["base.document.layout"]) as wizard:
                wizard.report_layout_id = self.report_layout_a
                wizard.layout_din5008_margin_bottom = 70

    def test_preview(self):
        with Form(self.env["base.document.layout"]) as wizard:
            self.assertEqual(wizard.report_layout_id, self.report_layout_a)
            preview = wizard.preview
            self.assertIn("din5008_sender_line", preview)
            self.assertIn("Acme GmbH · Musterstraße 1 · 12345 Berlin", preview)
            self.assertIn("o_layout_din5008", preview)
            self.assertIn('style="height: 27mm;"', preview)
            # "beside" is the default: the information block is relocated
            self.assertIn('class="din5008_informations"', preview)
            self.assertLess(
                preview.index('class="din5008_informations"'),
                preview.index('id="informations"'),
            )

            wizard.layout_din5008_informations_position = "below"
            self.assertNotIn('class="din5008_informations"', wizard.preview)

            wizard.layout_din5008_sender_line = False
            self.assertNotIn('class="din5008_sender_line"', wizard.preview)

            wizard.report_layout_id = self.report_layout_b
            self.assertIn('style="height: 45mm;"', wizard.preview)

            wizard.layout_din5008_logo_position = "right"
            self.assertIn('data-din5008-logo="right"', wizard.preview)
