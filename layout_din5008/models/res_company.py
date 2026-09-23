# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .layout_din5008_mixin import (
    DIN5008_ADDRESS_HEIGHT,
    DIN5008_INFO_LEFT,
    DIN5008_INFO_WIDTH,
    DIN5008_REMARK_ZONE_HEIGHT,
)

LAYOUT_DIN5008_RANGES = {
    "layout_din5008_margin_bottom": (5, 60),
    "layout_din5008_address_offset_top": (-10, 30),
    "layout_din5008_address_height": (20, 80),
    "layout_din5008_info_left": (105, 160),
    "layout_din5008_info_width": (30, 90),
    "layout_din5008_remark_zone_height": (0, 20),
}


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "layout.din5008.mixin"]

    layout_din5008_margin_bottom = fields.Integer(
        string="DIN 5008 Bottom Margin (mm)",
        default=25,
        help="Bottom page margin reserved for the footer of DIN 5008 reports.",
    )
    layout_din5008_address_offset_top = fields.Integer(
        string="DIN 5008 Address Window Offset (mm)",
        default=0,
        help="Vertical shift of the address window relative to the DIN 5008 "
        "position directly below the letterhead. Negative values move it up.",
    )
    layout_din5008_address_height = fields.Integer(
        string="DIN 5008 Address Window Height (mm)",
        default=DIN5008_ADDRESS_HEIGHT,
        help="Minimum height of the address window row. The document title "
        "starts below this row.",
    )
    layout_din5008_remark_zone_height = fields.Float(
        string="DIN 5008 Remark Zone Height (mm)",
        default=0,
        digits=(3, 1),
        help="Height of the remark zone (Zusatz- und Vermerkzone) between the "
        "sender line and the recipient address. DIN 5008 reserves "
        f"{DIN5008_REMARK_ZONE_HEIGHT} mm; 0 places the recipient address "
        "directly below the sender line.",
    )
    layout_din5008_info_left = fields.Integer(
        string="DIN 5008 Information Block Left (mm)",
        default=DIN5008_INFO_LEFT,
        help="Distance of the information block from the left edge of the page.",
    )
    layout_din5008_info_width = fields.Integer(
        string="DIN 5008 Information Block Width (mm)",
        default=DIN5008_INFO_WIDTH,
    )
    layout_din5008_logo_position = fields.Selection(
        selection=[("left", "Left"), ("right", "Right")],
        string="DIN 5008 Logo Position",
        default="left",
        required=True,
        help="Horizontal position of the company logo in the letterhead. The "
        "tagline is printed on the opposite side.",
    )
    layout_din5008_fold_marks = fields.Boolean(
        string="DIN 5008 Fold and Hole Marks",
        default=True,
        help="Print fold marks and the hole mark on the left edge of every page.",
    )
    layout_din5008_sender_line = fields.Boolean(
        string="DIN 5008 Sender Line",
        default=True,
        help="Print the company address as a single line above the recipient "
        "address (Rücksendeangabe), visible in the envelope window.",
    )
    layout_din5008_informations_position = fields.Selection(
        selection=[
            ("below", "Below the title (standard position)"),
            ("beside", "Beside the address (DIN 5008 information block)"),
        ],
        string="DIN 5008 Document Information",
        default="beside",
        required=True,
        help="Where the document information (dates, references, ...) of the "
        "standard reports is printed. 'Beside the address' moves the block "
        "next to the address window after rendering.",
    )

    @api.constrains(*LAYOUT_DIN5008_RANGES)
    def _check_layout_din5008_values(self):
        for company in self:
            for field_name, (low, high) in LAYOUT_DIN5008_RANGES.items():
                value = company[field_name]
                if not low <= value <= high:
                    raise ValidationError(
                        self.env._(
                            "%(field)s must be between %(low)s and %(high)s mm.",
                            field=company._fields[field_name]._description_string(
                                self.env
                            ),
                            low=low,
                            high=high,
                        )
                    )
