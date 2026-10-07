This glue module connects the DIN 5008 layout shipped with Odoo
(`l10n_din5008`) to the shared report footer of `l10n_de_report_footer`:

- the footer text, the company address block and the tagline are printed
  with the company placeholders rendered;
- the shared footer lines (for example the company representatives of
  `l10n_de_report_footer_representative`) are printed in the legal section of
  the footer, before the VAT number;
- the bottom margin configured in the document layout applies to the DIN 5008
  reports (previously the module `l10n_din5008_report_margin_bottom`).

It is installed automatically when both modules are installed.
