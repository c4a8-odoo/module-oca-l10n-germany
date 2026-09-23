# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re

from odoo import models

_MARGIN_BOTTOM_RE = re.compile(r'data-din5008-margin-bottom="(\d+)"')


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _prepare_html(self, html, report_model=False):
        """Forward the DIN 5008 bottom margin of the rendered company to wkhtmltopdf.

        The DIN 5008 article carries ``data-din5008-margin-bottom``. It is
        turned into the ``data-report-margin-bottom`` argument that
        ``_build_wkhtmltopdf_args`` already understands. An explicit value on
        the root ``<html>`` tag keeps precedence.
        """
        res = super()._prepare_html(html, report_model=report_model)
        if not res:
            return res
        bodies, res_ids, header, footer, specific_paperformat_args = res
        text = html.decode("utf-8") if isinstance(html, bytes) else str(html)
        match = _MARGIN_BOTTOM_RE.search(text)
        if match:
            specific_paperformat_args.setdefault(
                "data-report-margin-bottom", match.group(1)
            )
        return bodies, res_ids, header, footer, specific_paperformat_args
