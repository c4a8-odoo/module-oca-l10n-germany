# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase, tagged

from .common import LayoutDin5008Common

HEADER = "//div[contains(concat(' ', normalize-space(@class), ' '), ' header ')]"
ARTICLE = "//div[contains(concat(' ', normalize-space(@class), ' '), ' article ')]"
FOOTER = "//div[contains(concat(' ', normalize-space(@class), ' '), ' footer ')]"
ADDRESS_ROW = "//div[contains(concat(' ', normalize-space(@class), ' '), ' address ')]"


@tagged("post_install", "-at_install")
class TestHtmlLayout(LayoutDin5008Common, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_din5008()

    def _one(self, tree, xpath):
        nodes = tree.xpath(xpath)
        self.assertEqual(len(nodes), 1, f"expected one node for {xpath}")
        return nodes[0]

    def test_structure_below(self):
        self.company.layout_din5008_informations_position = "below"
        tree = self._render_tree()
        header = self._one(tree, HEADER)
        article = self._one(tree, ARTICLE)
        footer = self._one(tree, FOOTER)
        company_class = f"o_company_{self.company.id}_layout"
        for node in (header, article, footer):
            self.assertIn("o_layout_din5008", node.get("class"))
            self.assertIn(company_class, node.get("class"))
        self.assertIn("o_report_layout_standard", article.get("class"))
        self.assertEqual(header.get("style"), "height: 27mm;")
        self.assertEqual(header.get("data-din5008-form"), "A")
        self.assertEqual(header.get("data-din5008-logo"), "left")
        self.assertEqual(article.get("data-din5008-informations"), "below")
        self.assertIsNone(article.get("data-din5008-margin-bottom"))

        # company address block is moved from the header into the footer
        self.assertFalse(header.xpath(".//div[@name='company_address']"))
        company_address = self._one(footer, ".//div[@name='company_address']")
        self.assertIn("Acme GmbH", company_address.text_content())
        self.assertIn("Tel. +49 30 123456", footer.text_content())

        # fold marks: two fold marks and one hole mark in the header
        marks = header.xpath(".//div[contains(@class, 'din5008_fold_mark')]")
        self.assertEqual([m.get("style") for m in marks], ["top: 87mm;", "top: 192mm;"])
        hole = self._one(header, ".//div[contains(@class, 'din5008_hole_mark')]")
        self.assertEqual(hole.get("style"), "top: 148.5mm;")

        # sender line above the address window
        sender = self._one(article, ".//div[@class='din5008_sender_line']")
        self.assertEqual(sender.text, "Acme GmbH · Musterstraße 1 · 12345 Berlin")
        self.assertEqual(sender.get("style"), "top: 0mm;")

        # standard address row with the information block after the address
        row = self._one(article, ADDRESS_ROW)
        children = [child.get("name") for child in row if child.get("name")]
        self.assertEqual(children, ["address", "information_block"])
        self.assertIn("Max Mustermann", row.text_content())
        self.assertIn("Lager Nord", row.text_content())

        # document information stays inside the page
        informations = self._one(article, ".//div[@id='informations']")
        self.assertTrue(informations.xpath("ancestor::div[@class='page']"))
        self.assertFalse(article.xpath(".//div[@name='din5008_informations']"))
        title = self._one(article, "./h2")
        self.assertEqual(title.text_content().strip(), "Rechnung RE-2026-001")
        # company specific css is scoped to the article
        style = self._one(article, "./style")
        self.assertIn(self.company._layout_din5008_scope_class(), style.text)
        self.assertIn(self.company._layout_din5008_scope_class(), article.get("class"))
        self.assertIn("min-height: 45mm", style.text)

    def test_structure_beside(self):
        # "beside" is the default
        tree = self._render_tree()
        article = self._one(tree, ARTICLE)
        self.assertEqual(article.get("data-din5008-informations"), "beside")
        row = self._one(article, ADDRESS_ROW)
        children = [child.get("name") for child in row if child.get("name")]
        self.assertEqual(
            children, ["address", "information_block", "din5008_informations"]
        )
        informations = self._one(article, ".//div[@id='informations']")
        self.assertTrue(
            informations.xpath("ancestor::div[@name='din5008_informations']")
        )
        self.assertFalse(informations.xpath("ancestor::div[@class='page']"))
        self.assertIn("Rechnungsdatum", row.text_content())
        page = self._one(article, ".//div[@class='page']")
        self.assertIn("Position 1", page.text_content())
        self.assertNotIn("Rechnungsdatum", page.text_content())
        # the title still follows the address row
        title = self._one(article, "./h2")
        self.assertEqual(title.text_content().strip(), "Rechnung RE-2026-001")
        self.assertIs(row.getnext(), title)

    def test_beside_without_information_block(self):
        tree = self._render_tree(data={"no_information_block": True})
        row = self._one(tree, ADDRESS_ROW)
        children = [child.get("name") for child in row if child.get("name")]
        self.assertEqual(children, ["address", "din5008_informations"])

    def test_form_b(self):
        self._set_form("B")
        tree = self._render_tree()
        header = self._one(tree, HEADER)
        self.assertEqual(header.get("style"), "height: 45mm;")
        self.assertEqual(header.get("data-din5008-form"), "B")
        marks = header.xpath(".//div[contains(@class, 'din5008_fold_mark')]")
        self.assertEqual(
            [m.get("style") for m in marks], ["top: 105mm;", "top: 210mm;"]
        )

    def test_logo_position(self):
        self.company.layout_din5008_logo_position = "right"
        tree = self._render_tree()
        header = self._one(tree, HEADER)
        self.assertEqual(header.get("data-din5008-logo"), "right")
        self.assertTrue(header.xpath(".//img[@class='o_company_logo_small']"))

    def test_options_disabled(self):
        self.company.write(
            {"layout_din5008_sender_line": False, "layout_din5008_fold_marks": False}
        )
        tree = self._render_tree()
        self.assertFalse(tree.xpath("//div[@class='din5008_sender_line']"))
        self.assertFalse(tree.xpath("//div[contains(@class, 'din5008_mark')]"))

    def test_custom_geometry(self):
        self.company.write(
            {
                "layout_din5008_address_offset_top": 3,
                "layout_din5008_address_height": 50,
                "layout_din5008_info_left": 120,
                "layout_din5008_info_width": 80,
                "layout_din5008_remark_zone_height": 8,
            }
        )
        tree = self._render_tree()
        article = self._one(tree, ARTICLE)
        style = self._one(article, "./style").text
        self.assertIn("margin-top: 3mm; min-height: 50mm", style)
        self.assertIn("padding-top: 13mm", style)
        self.assertIn("margin-left: 100mm; width: 80mm", style)
        sender = self._one(article, ".//div[@class='din5008_sender_line']")
        self.assertEqual(sender.get("style"), "top: 3mm;")

    def test_extension_of_standard_layout_applies(self):
        """Extensions of web.external_layout_standard apply to the DIN layout."""
        self.env["ir.ui.view"].create(
            {
                "name": "layout_din5008.test_extension",
                "type": "qweb",
                "inherit_id": self.env.ref("web.external_layout_standard").id,
                "mode": "extension",
                "arch": """
                    <xpath expr="//ul[@name='company_address_list']" position="inside">
                        <li class="din5008_test_extension">EXTENSION</li>
                    </xpath>
                """,
            }
        )
        tree = self._render_tree()
        footer = self._one(tree, FOOTER)
        extension = self._one(footer, ".//li[@class='din5008_test_extension']")
        self.assertEqual(extension.text, "EXTENSION")

    def test_prepare_html_margin_bottom(self):
        html = self._render_html(data={"report_type": "pdf"})
        self.assertIn('data-din5008-margin-bottom="25"', html)
        args = self.report._prepare_html(html, report_model="res.partner")[4]
        self.assertEqual(args.get("data-report-margin-bottom"), "25")

        self.company.layout_din5008_margin_bottom = 40
        html = self._render_html(data={"report_type": "pdf"})
        args = self.report._prepare_html(html, report_model="res.partner")[4]
        self.assertEqual(args.get("data-report-margin-bottom"), "40")

        # an explicit value on the root tag keeps precedence
        html = html.replace("<html", '<html data-report-margin-bottom="12"', 1)
        args = self.report._prepare_html(html, report_model="res.partner")[4]
        self.assertEqual(args.get("data-report-margin-bottom"), "12")

        # html rendering does not carry the attribute
        html = self._render_html()
        self.assertNotIn("data-din5008-margin-bottom", html)
