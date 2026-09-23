# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCompany(TransactionCase):
    def test_defaults(self):
        company = self.env["res.company"].create({"name": "DIN Test Company"})
        self.assertEqual(company.layout_din5008_margin_bottom, 25)
        self.assertEqual(company.layout_din5008_address_offset_top, 0)
        self.assertEqual(company.layout_din5008_address_height, 45)
        self.assertEqual(company.layout_din5008_info_left, 125)
        self.assertEqual(company.layout_din5008_info_width, 75)
        self.assertEqual(company.layout_din5008_remark_zone_height, 0)
        self.assertEqual(company.layout_din5008_logo_position, "left")
        self.assertTrue(company.layout_din5008_fold_marks)
        self.assertTrue(company.layout_din5008_sender_line)
        self.assertEqual(company.layout_din5008_informations_position, "beside")

    def test_constraints(self):
        company = self.env.company
        for field_name, low, high in [
            ("layout_din5008_margin_bottom", 5, 60),
            ("layout_din5008_address_offset_top", -10, 30),
            ("layout_din5008_address_height", 20, 80),
            ("layout_din5008_info_left", 105, 160),
            ("layout_din5008_info_width", 30, 90),
            ("layout_din5008_remark_zone_height", 0, 20),
        ]:
            company.write({field_name: low})
            company.write({field_name: high})
            with self.assertRaises(ValidationError):
                company.write({field_name: low - 1})
            with self.assertRaises(ValidationError):
                company.write({field_name: high + 1})
