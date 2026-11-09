# Figure editions and denominators

The count, sector and recorded-date maps use the November reviewed working
inventory: 1,329 raw rows. They count records rather than verified currently
operative restrictions. State totals include the two aggregate meta-rows; the
separate cleaned LaTeX inventory/sector tables omit those two rows and declare
their own denominator. None is a nationwide current-law census.

- `map-moratorium-counts`: all raw rows grouped by state, including pending,
  historical, rejected and unknown recorded stages.
- `map-sector-composition`: normalized `sectors` arrays. A multi-sector row
  contributes once to each recorded sector; the most frequent sector determines
  the state fill, with tied maxima shown as Mixed. `general` is Other. Empty
  values are Unknown and never silently become data centers. These are declared
  sector classifications, not independent project-applicability findings.
- `map-timeline-heatmap`: normalized recorded dates with a usable month. Dates
  may be unverified or scheduled; a date does not independently prove adoption
  or legal force. Rows without usable months are counted separately in the title.

The legal-authority, home-rule, preemption and maximum-statutory-duration maps
retain the companion historical paper's classifications. They have not received
a new November state-law survey and must not be presented as verified current
law. They are re-rendered only to put the historical edition notice directly on each image; classification inputs are unchanged. Rendering those classifications does not update their evidence.
The linked April manuscript and its embedded figures remain a historical edition.

PNG, SVG and PDF variants of each refreshed data map are generated together.
The data-map refresh and all seven table generators do not rebuild the historical
paper PDF or the older clause-extraction cohort. The latter remains a separate
348-record analytical cohort with its own source and confidence rules.
