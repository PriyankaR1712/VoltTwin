# VoltTwin Browser End-to-End Testing Report

**Date:** 2026-11-10
**Project:** `C:\\Users\\acer\\Desktop\\VoltTwin`
**Frontend command:** `npm.cmd run dev -- --host 127.0.0.1 --port 5173`
**Backend command:** `.venv\\Scripts\\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`

## Browser and framework

The test used a real installed **Google Chrome** executable at
`C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe`, automated with
**Playwright 1.65.0** from the newly added frontend development dependency. The
browser ran headless with a 1440x1100 viewport. This is browser execution, not a
source-only or API-only check.

The backend was already healthy on port 8000 from the project environment; an
additional start attempt correctly reported that the port was already in use.
The frontend was started with the actual Vite project command on port 5173.

## Result

**26 checks passed, 0 failed.** No page exceptions or critical (5xx) network
responses occurred.

The single-page dashboard was tested through its homepage and anchored sections;
there are no separate frontend route pages in the current application. The
Formula Explorer anchor and the VoltTwin brand link were both exercised.

## Checks executed

1. Loaded the homepage and verified the hero and Battery configuration section.
2. Clicked Formula Explorer navigation and verified the `#feature-explorer`
   anchor.
3. Verified the Formula Explorer provenance warning.
4. Verified all 67 feature rows are present and accessible.
5. Applied the CC, dV, CV, dI, and Charge category filters and verified 13,
   13, 13, 13, and 15 rows respectively.
6. Searched for `CC_energy` and verified one matching row.
7. Opened CC_energy details and verified candidate status.
8. Verified the unavailable original-formula warning.
9. Opened CC_entropy and verified the `Original formula unknown` status.
10. Verified the entropy diagnostic-proxy provenance warning.
11. Verified the batch/profile controls populate from the backend.
12. Ran a valid candidate calculation for batch 1, Sheet1, cycle 1.
13. Verified the candidate-only calculation warning.
14. Verified raw sample details and a rendered Recharts SVG plot.
15. Changed the batch to batch 2 and verified profiles repopulate.
16. Issued an invalid cycle request from the browser and observed HTTP 404.
17. Exercised the frontend invalid-calculation error state with a browser
    response carrying the same 404/detail shape.
18. Returned to the homepage through the VoltTwin brand link.
19. Verified the homepage remained usable after returning.

The script also recorded the catalog load, profile load, calculation, and error
requests while monitoring console, page-error, failed-request, and response
streams. The exact runnable test is [browser_e2e.mjs](../frontend/browser_e2e.mjs).

## Screenshots

The run generated these full-page screenshots under
`reports/browser_screenshots/`:

- [Homepage](browser_screenshots/01_homepage.png)
- [Formula Explorer catalog](browser_screenshots/02_formula_explorer_catalog.png)
- [Feature search and details](browser_screenshots/03_feature_search_and_details.png)
- [Valid calculation and raw plot](browser_screenshots/04_valid_calculation_and_raw_plot.png)
- [Batch/profile selection](browser_screenshots/05_batch_profile_selection.png)
- [Invalid calculation error](browser_screenshots/06_invalid_calculation_error.png)

The calculation screenshot visibly includes the candidate result, provenance
warning, raw signal chart, and numerical derivation panel.

## Console and network observations

- Page exceptions: **0**.
- Critical HTTP 5xx responses: **0**.
- Application requests needed for the successful flows returned successfully.
- Two aborted catalog requests were React development StrictMode superseded
  requests; the replacement requests completed and the controls populated.
- Two 404 responses were intentional invalid-calculation checks.
- Chrome reported one blocked Google Fonts request (`ERR_NETWORK_ACCESS_DENIED`)
  because this environment blocks external font downloads. The app continued to
  render with fallback fonts; this is recorded as an environment limitation,
  not an application-flow failure.

## Issues discovered and fixed

No reproducible application defect was found. The only two failures during test
development were incorrect test assumptions: native `<option>` elements are not
individually visible, and the UI status uses sentence-case `Original formula
unknown`. The browser test was corrected and rerun; no product code or formula
was changed.

## Remaining browser limitations

- The current app is a single-page dashboard, so “major page navigation” means
  anchored section navigation rather than separate routes.
- The UI disables an out-of-range cycle before sending it. Therefore the actual
  backend 404 was observed with a browser `fetch`, while the visible UI error
  rendering was tested with a browser-intercepted response using the same 404
  payload shape.
- External Google Fonts remain unavailable in this restricted environment; the
  fallback font path was visually rendered successfully.
- The test ran against the locally present XJTU reference data and a live local
  backend. A clean checkout without those ignored data files will show the
  backend’s documented data-unavailable states.
