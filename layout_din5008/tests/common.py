# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import lxml.html

LOGO_PNG = (
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/AAX+Av4N70a4"
    b"AAAAAElFTkSuQmCC"
)

COMPANY_DETAILS = "<p>Acme GmbH<br/>Musterstraße 1<br/>12345 Berlin</p>"
REPORT_FOOTER = "<p>Tel. +49 30 123456 · info@acme.example · Amtsgericht Berlin</p>"

# Self-contained report using the conventions of the standard reports:
# address, information_block, layout_document_title and #informations.
TEST_REPORT_ARCH = """
<t t-name="layout_din5008.test_report">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <t t-set="o" t-value="o" />
                <t t-set="address">
                    <address class="mb-0">
                        Max Mustermann<br/>Musterweg 5<br/>10115 Berlin
                    </address>
                </t>
                <t t-if="not no_information_block" t-set="information_block">
                    <strong>Shipping Address</strong>
                    <div>Lager Nord<br/>Hafenstraße 9<br/>20457 Hamburg</div>
                </t>
                <div class="page">
                    <t t-set="layout_document_title">
                        <span>Rechnung RE-2026-001</span>
                    </t>
                    <div id="informations" class="row mb-4">
                        <div class="col" name="invoice_date">
                            <strong>Rechnungsdatum</strong>
                            <div>23.09.2026</div>
                        </div>
                        <div class="col" name="due_date">
                            <strong>Zahlbar bis</strong>
                            <div>07.10.2026</div>
                        </div>
                        <div class="col" name="customer_ref">
                            <strong>Kundennummer</strong>
                            <div>K-4711</div>
                        </div>
                    </div>
                    <table class="table o_main_table table-borderless">
                        <thead>
                            <tr>
                                <th>Beschreibung</th>
                                <th class="text-end">Betrag</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr t-foreach="range(n_rows or 3)" t-as="i">
                                <td>Position <t t-out="i + 1" /></td>
                                <td class="text-end">10,00 EUR</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </t>
        </t>
    </t>
</t>
"""


class LayoutDin5008Common:
    """Mixin preparing a company using the DIN 5008 layout and a test report."""

    @classmethod
    def _setup_din5008(cls):
        cls.company = cls.env.company
        cls.layout_a = cls.env.ref("layout_din5008.external_layout_din5008_a")
        cls.layout_b = cls.env.ref("layout_din5008.external_layout_din5008_b")
        cls.paperformat_a = cls.env.ref("layout_din5008.paperformat_din5008_a")
        cls.paperformat_b = cls.env.ref("layout_din5008.paperformat_din5008_b")
        cls.company.write(
            {
                "external_report_layout_id": cls.layout_a.id,
                "paperformat_id": cls.paperformat_a.id,
                "company_details": COMPANY_DETAILS,
                "report_footer": REPORT_FOOTER,
                "logo": LOGO_PNG,
                "layout_din5008_margin_bottom": 25,
                "layout_din5008_address_offset_top": 0,
                "layout_din5008_address_height": 45,
                "layout_din5008_info_left": 125,
                "layout_din5008_info_width": 75,
                "layout_din5008_remark_zone_height": 0,
                "layout_din5008_logo_position": "left",
                "layout_din5008_fold_marks": True,
                "layout_din5008_sender_line": True,
                "layout_din5008_informations_position": "beside",
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Max Mustermann"})
        cls.env["ir.ui.view"].create(
            {
                "type": "qweb",
                "name": "layout_din5008.test_report",
                "key": "layout_din5008.test_report",
                "arch": TEST_REPORT_ARCH,
            }
        )
        cls.report = cls.env["ir.actions.report"].create(
            {
                "name": "DIN 5008 test report",
                "report_name": "layout_din5008.test_report",
                "model": "res.partner",
                "report_type": "qweb-pdf",
            }
        )

    def _set_form(self, form):
        layout = self.layout_a if form == "A" else self.layout_b
        paperformat = self.paperformat_a if form == "A" else self.paperformat_b
        self.company.write(
            {"external_report_layout_id": layout.id, "paperformat_id": paperformat.id}
        )

    def _render_html(self, data=None):
        html = self.env["ir.actions.report"]._render_qweb_html(
            self.report, self.partner.ids, data=data
        )[0]
        if isinstance(html, bytes):
            html = html.decode("utf-8")
        return str(html)

    def _render_tree(self, data=None):
        return lxml.html.fromstring(self._render_html(data=data))
