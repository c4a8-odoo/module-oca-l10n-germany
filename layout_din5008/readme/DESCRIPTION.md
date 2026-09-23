This module provides a **DIN 5008** business letter layout for all PDF reports
that use the standard Odoo document layout (invoices, quotations, purchase
orders, delivery slips, ...).

Unlike the Odoo module `l10n_din5008`, which renders its own report structure
and needs a companion module for every report, this layout extends the
standard layout `web.external_layout_standard`. Every report that works with
the standard layout works with this one, including extensions other modules
add to the standard layout or to the address block.

Both DIN 5008 forms are available in the document layout configurator:

- **Form A**: letterhead of 27 mm, address window starting at 27 mm.
- **Form B**: letterhead of 45 mm, address window starting at 45 mm.

The layout places the sender line, the address window (20 mm from the left
edge, 85 mm x 45 mm), the information block (125 mm from the left edge, 75 mm
wide), the document title (two lines below the address window), the fold
marks (87/192 mm for Form A, 105/210 mm for Form B) and the hole mark
(148.5 mm) according to DIN 5008. All blocks stay in the document flow: long
addresses or a long information block push the following content down
instead of overlapping it.
