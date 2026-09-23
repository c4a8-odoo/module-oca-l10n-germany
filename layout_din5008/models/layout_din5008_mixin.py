# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re

import lxml.html
from markupsafe import Markup

from odoo import models
from odoo.tools import html2plaintext

# Letterhead height (= paper format margin top) and fold mark positions,
# all in mm from the top edge of the page.
DIN5008_FORMS = {
    "A": {"header_height": 27, "fold_marks": (87, 192)},
    "B": {"header_height": 45, "fold_marks": (105, 210)},
}
DIN5008_HOLE_MARK = 148.5
# Address window: 20 mm from the left edge, 85 mm wide, 45 mm high.
DIN5008_ADDRESS_LEFT = 20
DIN5008_ADDRESS_WIDTH = 85
DIN5008_ADDRESS_HEIGHT = 45
# Zones inside the address window: sender line (Rücksendeangabe) and
# remark zone (Zusatz- und Vermerkzone) above the recipient address.
DIN5008_SENDER_ZONE_HEIGHT = 5
DIN5008_REMARK_ZONE_HEIGHT = 12.7
# Information block: 125 mm from the left edge, 75 mm wide.
DIN5008_INFO_LEFT = 125
DIN5008_INFO_WIDTH = 75

DIN5008_LAYOUT_KEYS = {
    "layout_din5008.external_layout_din5008_a": "A",
    "layout_din5008.external_layout_din5008_b": "B",
}
DIN5008_PAPERFORMATS = {
    "A": "layout_din5008.paperformat_din5008_a",
    "B": "layout_din5008.paperformat_din5008_b",
}

_ADDRESS_ROW_XPATH = (
    './/div[contains(concat(" ", normalize-space(@class), " "), " address ")]'
)
_INFORMATIONS_XPATH = './/div[@id="informations"]'


def _serialize_fragment(root):
    """Serialize the children of a wrapper element created by lxml."""
    return (root.text or "") + "".join(
        lxml.html.tostring(child, encoding="unicode") for child in root
    )


class LayoutDin5008Mixin(models.AbstractModel):
    """Helpers used by the DIN 5008 report templates.

    The layout templates receive ``company`` either as a ``res.company`` record
    or, in the document layout wizard preview, as the ``base.document.layout``
    record itself. Both models inherit this mixin.
    """

    _name = "layout.din5008.mixin"
    _description = "DIN 5008 Layout Helpers"

    def _layout_din5008_sender_line(self):
        """Return the sender line (Rücksendeangabe) printed above the recipient."""
        self.ensure_one()
        lines = []
        if self.company_details:
            lines = html2plaintext(self.company_details).splitlines()
        lines = [line.strip() for line in lines if line.strip()]
        if not lines and self.partner_id:
            address = self.partner_id._display_address(without_company=True) or ""
            lines = [self.name or "", *address.splitlines()]
            lines = [line.strip() for line in lines if line.strip()]
        return " · ".join(lines)

    def _layout_din5008_scope_class(self):
        """CSS class scoping the company specific rules of one rendered article."""
        self.ensure_one()
        return "din5008_scope_" + re.sub(r"\W", "_", str(self.id))

    def _layout_din5008_geometry(self, form):
        """Return inline styles and CSS for the given DIN 5008 form ('A' or 'B')."""
        self.ensure_one()
        spec = DIN5008_FORMS.get(form) or DIN5008_FORMS["A"]
        offset_top = self.layout_din5008_address_offset_top or 0
        address_height = self.layout_din5008_address_height or DIN5008_ADDRESS_HEIGHT
        info_left = self.layout_din5008_info_left or DIN5008_INFO_LEFT
        info_width = self.layout_din5008_info_width or DIN5008_INFO_WIDTH
        remark_height = self.layout_din5008_remark_zone_height or 0
        recipient_top = DIN5008_SENDER_ZONE_HEIGHT + remark_height
        scope = f".o_layout_din5008.{self._layout_din5008_scope_class()}"
        company_css = (
            f"{scope} .address.row {{ margin-top: {offset_top}mm; "
            f"min-height: {address_height}mm; }}\n"
            f"{scope} .address.row > div[name='address'] "
            f"{{ padding-top: {recipient_top:g}mm; }}\n"
            f"{scope} .address.row > div[name='information_block'], "
            f"{scope} .address.row > .din5008_informations "
            f"{{ margin-left: {info_left - DIN5008_ADDRESS_LEFT}mm; "
            f"width: {info_width}mm; }}\n"
        )
        return {
            "form": form,
            "header_height": spec["header_height"],
            "header": f"height: {spec['header_height']}mm;",
            "sender_line": f"top: {offset_top}mm;",
            "fold_marks": [f"top: {top}mm;" for top in spec["fold_marks"]],
            "hole_mark": f"top: {DIN5008_HOLE_MARK}mm;",
            "company_css": Markup(company_css),
        }

    def _layout_din5008_relocate_informations(self, address_html, body):
        """Move the ``#informations`` block of the report body into the address row.

        Standard reports render the document information (dates, references,
        ...) as ``<div id="informations">`` below the title. In the "beside"
        mode this block is moved into the DIN 5008 information block next to
        the address window. Both arguments are already rendered HTML; only
        these fragments are parsed, the surrounding document is untouched.

        :return: tuple ``(address_html, body_html)`` as Markup
        """
        address_html = str(address_html or "")
        body_html = str(body or "")
        if 'id="informations"' not in body_html or not address_html.strip():
            return Markup(address_html), Markup(body_html)
        body_root = lxml.html.fragment_fromstring(body_html, create_parent="div")
        address_root = lxml.html.fragment_fromstring(address_html, create_parent="div")
        informations = body_root.xpath(_INFORMATIONS_XPATH)
        rows = address_root.xpath(_ADDRESS_ROW_XPATH)
        if not informations or not rows:
            return Markup(address_html), Markup(body_html)
        node = informations[0]
        node.drop_tree()
        node.tail = None
        container = lxml.html.Element(
            "div", {"class": "din5008_informations", "name": "din5008_informations"}
        )
        container.append(node)
        rows[0].append(container)
        return (
            Markup(_serialize_fragment(address_root)),
            Markup(_serialize_fragment(body_root)),
        )
