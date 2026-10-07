Go to *Settings > Companies > Configure Document Layout* and choose
**DIN 5008 Form A** or **DIN 5008 Form B**. The matching paper format
(*DIN 5008 Form A* / *DIN 5008 Form B*) is selected automatically.

The following settings appear once a DIN 5008 layout is selected:

- **Document Information**: where the document information of the standard
  reports (dates, references, salesperson, ...) is printed. *Below the title*
  keeps the standard position. *Beside the address* (default) moves the block
  into the DIN 5008 information block next to the address window. The block is moved
  after rendering, so extensions adding rows to it keep working; only styles
  that rely on its original position do not apply.
- **Logo Position**: print the company logo on the left or on the right of
  the letterhead; the tagline is printed on the opposite side.
- **Sender Line**: print the *Address* text of the document layout as a
  single line above the recipient address (Rücksendeangabe); its lines are
  joined with the *Separator* (`|`, `•` or `·`) and *Font scale* scales the
  7 pt line. The address may contain placeholders; the placeholder *DIN 5008
  Sender Line Text* provides the company name and address formatted with the
  separator and the *Country* option (country code before the postal code,
  `DE-12345 Berlin`, or the country name at the end). Without address text the
  formatted company address is printed.
- **Fold Marks** and **Hole Mark**: print the fold marks and the hole mark
  on every page.
- **Address Window**: vertical offset (mm) of the address row relative to the
  DIN 5008 position, its minimum height (mm) and the height of the remark
  zone (Zusatz- und Vermerkzone) between the sender line and the recipient
  address. DIN 5008 reserves 12.7 mm for remarks such as "Einschreiben"; the
  default of 0 mm prints the recipient address directly below the sender line.
- **Information Block**: distance from the left edge (mm) and width (mm) of
  the column next to the address window.

While one of these fields is focused, the affected area is outlined in the
preview.
The footer text with company placeholders, the shared footer lines and the
bottom margin of the PDF reports are configured in the same wizard and come
from the module `l10n_de_report_footer`.

The paper formats keep 0 mm side margins and disable smart shrinking so that
the CSS millimetres of the layout equal the printed millimetres. When you use
your own paper format with a DIN 5008 layout, keep these settings and set the
top margin equal to the header spacing (27 mm for Form A, 45 mm for Form B).
