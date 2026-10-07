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

# Allowed values of the numeric settings (mm, the font scale is a factor)
LAYOUT_DIN5008_RANGES = {
    "layout_din5008_address_offset_top": (-10, 30),
    "layout_din5008_address_height": (20, 80),
    "layout_din5008_info_left": (105, 160),
    "layout_din5008_info_width": (30, 90),
    "layout_din5008_remark_zone_height": (0, 20),
    "layout_din5008_sender_font_factor": (0.5, 2.0),
}


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "layout.din5008.mixin"]

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
        string="DIN 5008 Fold Marks",
        default=True,
        help="Print the fold marks on the left edge of every page.",
    )
    layout_din5008_hole_mark = fields.Boolean(
        string="DIN 5008 Hole Mark",
        default=True,
        help="Print the hole mark on the left edge of every page.",
    )
    layout_din5008_sender_line = fields.Boolean(
        string="DIN 5008 Sender Line",
        default=True,
        help="Print the company address as a single line above the recipient "
        "address (Rücksendeangabe), visible in the envelope window.",
    )
    layout_din5008_sender_line_text = fields.Char(
        string="DIN 5008 Sender Line Text",
        compute="_compute_layout_din5008_sender_line_text",
        store=True,
        help="Name and address of the company formatted as a single line with "
        "the configured separator and country indicator. Available as "
        "placeholder in the address, tagline and footer texts of the document "
        "layout; insert it into the address to print it as sender line.",
    )
    layout_din5008_sender_separator = fields.Selection(
        selection=[
            ("pipe", "Pipe (|)"),
            ("bullet", "Bullet (•)"),
            ("middot", "Middle dot (·)"),
        ],
        string="DIN 5008 Sender Line Separator",
        default="pipe",
        required=True,
        help="Character between the lines of the address printed as sender line "
        "above the recipient. The company name and address formatted this way "
        "are available as the placeholder 'DIN 5008 Sender Line Text' in the "
        "address, tagline and footer texts of the document layout.",
    )
    layout_din5008_sender_country = fields.Selection(
        selection=[
            ("none", "No country"),
            ("code", "Country code before the postal code"),
            ("name", "Country name"),
        ],
        string="DIN 5008 Sender Line Country",
        default="none",
        required=True,
        help="How the country of the company is printed in the placeholder "
        "'DIN 5008 Sender Line Text' (insert it into the address of the "
        "document layout to print it as sender line).",
    )
    layout_din5008_sender_font_factor = fields.Float(
        string="DIN 5008 Sender Line Font Scale",
        default=1.0,
        digits=(3, 2),
        help="Scale factor of the sender line font size (1.0 = 7 pt).",
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
                            "%(field)s must be between %(low)s and %(high)s.",
                            field=company._fields[field_name]._description_string(
                                self.env
                            ),
                            low=low,
                            high=high,
                        )
                    )

    @api.model
    def mail_allowed_qweb_expressions(self):
        return super().mail_allowed_qweb_expressions() + (
            "object.layout_din5008_sender_line_text",
        )

    @api.depends(
        "name",
        "partner_id.street",
        "partner_id.street2",
        "partner_id.zip",
        "partner_id.city",
        "partner_id.country_id",
        "layout_din5008_sender_separator",
        "layout_din5008_sender_country",
    )
    def _compute_layout_din5008_sender_line_text(self):
        for company in self:
            company.layout_din5008_sender_line_text = (
                company._layout_din5008_format_sender_line()
            )
