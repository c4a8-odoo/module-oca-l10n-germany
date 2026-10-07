Print any report using a document layout. The footer text is printed with
the placeholders replaced by the data of the company that issues the
document, followed by the footer lines added by other modules.

Developers: call `<t t-call="l10n_de_report_footer.footer_lines"/>` inside a
`<ul>` of a custom layout and add `<li>` elements to the hook
`//t[@name='l10n_de_report_footer_lines']` of that template to print
additional lines in every layout. Give a form field the class
`o_report_preview_highlight_<key>` and style
`html[data-report-preview-highlight="<key>"] <selector>` in the report assets
to outline an area of the layout preview while the field is focused.
