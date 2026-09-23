# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

from ..models.layout_din5008_mixin import DIN5008_LAYOUT_KEYS, DIN5008_PAPERFORMATS

LAYOUT_DIN5008_FIELDS = [
    "layout_din5008_margin_bottom",
    "layout_din5008_address_offset_top",
    "layout_din5008_address_height",
    "layout_din5008_info_left",
    "layout_din5008_info_width",
    "layout_din5008_remark_zone_height",
    "layout_din5008_logo_position",
    "layout_din5008_fold_marks",
    "layout_din5008_sender_line",
    "layout_din5008_informations_position",
]


class BaseDocumentLayout(models.TransientModel):
    _name = "base.document.layout"
    _inherit = ["base.document.layout", "layout.din5008.mixin"]

    layout_din5008_margin_bottom = fields.Integer(
        related="company_id.layout_din5008_margin_bottom", readonly=False
    )
    layout_din5008_address_offset_top = fields.Integer(
        related="company_id.layout_din5008_address_offset_top", readonly=False
    )
    layout_din5008_address_height = fields.Integer(
        related="company_id.layout_din5008_address_height", readonly=False
    )
    layout_din5008_info_left = fields.Integer(
        related="company_id.layout_din5008_info_left", readonly=False
    )
    layout_din5008_info_width = fields.Integer(
        related="company_id.layout_din5008_info_width", readonly=False
    )
    layout_din5008_remark_zone_height = fields.Float(
        related="company_id.layout_din5008_remark_zone_height", readonly=False
    )
    layout_din5008_logo_position = fields.Selection(
        related="company_id.layout_din5008_logo_position", readonly=False
    )
    layout_din5008_fold_marks = fields.Boolean(
        related="company_id.layout_din5008_fold_marks", readonly=False
    )
    layout_din5008_sender_line = fields.Boolean(
        related="company_id.layout_din5008_sender_line", readonly=False
    )
    layout_din5008_informations_position = fields.Selection(
        related="company_id.layout_din5008_informations_position", readonly=False
    )
    layout_din5008_is_din = fields.Boolean(
        string="Is DIN 5008 Layout", compute="_compute_layout_din5008_is_din"
    )

    @api.depends("report_layout_id")
    def _compute_layout_din5008_is_din(self):
        for wizard in self:
            wizard.layout_din5008_is_din = (
                wizard.report_layout_id.view_id.key in DIN5008_LAYOUT_KEYS
            )

    @api.onchange("report_layout_id")
    def _onchange_report_layout_id(self):
        res = super()._onchange_report_layout_id()
        for wizard in self:
            form = DIN5008_LAYOUT_KEYS.get(wizard.report_layout_id.view_id.key)
            if not form:
                continue
            paperformat = self.env.ref(
                DIN5008_PAPERFORMATS[form], raise_if_not_found=False
            )
            if paperformat:
                wizard.paperformat_id = paperformat
        return res

    @api.depends(*LAYOUT_DIN5008_FIELDS)
    def _compute_preview(self):
        return super()._compute_preview()
