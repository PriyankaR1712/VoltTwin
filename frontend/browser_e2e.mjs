import { chromium } from 'playwright'
import fs from 'node:fs'

const baseUrl = 'http://127.0.0.1:5173/'
const chromePath = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
const screenshotDir = 'C:/Users/acer/Desktop/VoltTwin/reports/browser_screenshots'
fs.mkdirSync(screenshotDir, { recursive: true })

const failures = []
const consoleErrors = []
const pageErrors = []
const criticalResponses = []
const expectedClientErrors = []
const passed = []

function check(condition, message) {
  if (!condition) throw new Error(message)
  passed.push(message)
}

async function waitForOptions(locator, timeoutMs = 60000) {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    if (await locator.locator('option').count() > 0) return
    await new Promise((resolve) => setTimeout(resolve, 250))
  }
  throw new Error('Timed out waiting for a populated select control')
}

async function main() {
  const browser = await chromium.launch({ headless: true, executablePath: chromePath })
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 })
  const page = await context.newPage()

  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text())
  })
  page.on('pageerror', (error) => pageErrors.push(String(error)))
  page.on('requestfailed', (request) => {
    failures.push(`${request.method()} ${request.url()} :: ${request.failure()?.errorText ?? 'unknown'}`)
  })
  page.on('response', (response) => {
    if (response.status() >= 500) criticalResponses.push(`${response.status()} ${response.url()}`)
    if (response.status() >= 400 && response.status() < 500) {
      expectedClientErrors.push(`${response.status()} ${response.url()}`)
    }
  })

  const screenshot = async (name) => {
    await page.screenshot({ path: `${screenshotDir}/${name}.png`, fullPage: true })
  }

  await page.goto(baseUrl, { waitUntil: 'domcontentloaded' })
  await page.getByRole('heading', { name: /Understand your battery's/i }).waitFor()
  check(await page.getByText('Battery configuration', { exact: true }).isVisible(), 'homepage loads battery configuration')
  await screenshot('01_homepage')

  await page.getByRole('link', { name: 'Formula Explorer' }).click()
  await page.locator('#feature-explorer').scrollIntoViewIfNeeded()
  await page.getByRole('heading', { name: 'Formula Explorer', exact: true }).waitFor()
  check(page.url().endsWith('/#feature-explorer'), 'navigation to Formula Explorer works')
  check(await page.getByRole('note').filter({ hasText: 'Original XJTU workbook formulas have not been verified' }).isVisible(), 'provenance warning is visible')
  await page.locator('.formula-feature-row').first().waitFor()
  check(await page.locator('.formula-feature-row').count() === 67, 'all 67 candidate features are accessible')
  await screenshot('02_formula_explorer_catalog')

  const groupButtons = page.locator('[aria-label="Feature category"] button')
  for (const [group, expectedCount] of [['CC', 13], ['dV', 13], ['CV', 13], ['dI', 13], ['Charge', 15]]) {
    await groupButtons.getByText(group, { exact: true }).click()
    check(await page.locator('.formula-feature-row').count() === expectedCount, `${group} category filter shows ${expectedCount} features`)
  }
  await groupButtons.getByText('CC', { exact: true }).click()

  const search = page.getByRole('searchbox', { name: 'Search all 67 features' })
  await search.fill('CC_energy')
  check(await page.locator('.formula-feature-row').count() === 1, 'feature search narrows to CC_energy')
  await page.locator('.formula-feature-row').first().click()
  check(await page.getByRole('heading', { name: 'CC_energy', exact: true }).isVisible(), 'feature details open for CC_energy')
  check(await page.getByText('Candidate / Unverified', { exact: true }).first().isVisible(), 'candidate formula status is shown')
  check(await page.getByText('Unavailable — original formula not verified.', { exact: true }).isVisible(), 'original formula unavailable warning is shown')
  await screenshot('03_feature_search_and_details')

  await groupButtons.getByText('All', { exact: true }).click()
  await search.fill('CC_entropy')
  await page.locator('.formula-feature-row').first().click()
  check(await page.getByText('Original formula unknown', { exact: true }).first().isVisible(), 'unknown original entropy status is shown')
  check(await page.getByText(/Original formula not verified\. The expression below describes the existing candidate implementation only\./).isVisible(), 'unknown formula provenance note is shown')
  check(await page.getByText(/Original formula unknown\. The displayed histogram expression is a diagnostic proxy/).isVisible(), 'entropy diagnostic proxy warning is shown')

  await search.fill('')
  await page.getByRole('button', { name: 'CC_energy' }).click()
  const batchSelect = page.locator('label').filter({ hasText: 'Batch' }).locator('select')
  const profileSelect = page.locator('label').filter({ hasText: 'Battery profile' }).locator('select')
  await waitForOptions(profileSelect)
  check(await profileSelect.locator('option').count() > 0, 'initial profile selection is populated')
  await page.getByRole('button', { name: 'Calculate candidate' }).click()
  await page.locator('.formula-calculation-result').waitFor({ timeout: 30000 })
  check(await page.locator('.formula-chart svg').count() > 0, 'raw signal plot renders after valid calculation')
  check(await page.getByText('Candidate calculation only. It may differ from the original benchmark workbook implementation.', { exact: true }).isVisible(), 'candidate-only calculation warning is visible')
  check(await page.getByText(/Raw samples:/).isVisible(), 'raw sampling details render')
  await screenshot('04_valid_calculation_and_raw_plot')

  await batchSelect.selectOption('2')
  await waitForOptions(profileSelect)
  check(await batchSelect.inputValue() === '2', 'batch selection changes to batch 2')
  check((await profileSelect.locator('option').count()) > 0, 'profile selection remains populated after batch change')
  await screenshot('05_batch_profile_selection')

  const invalidResponse = await page.evaluate(async () => {
    const response = await fetch('/api/formula-explorer/calculate?batch=1&profile=Sheet1&cycle=99999&feature_name=CC_energy')
    return { status: response.status, body: await response.json() }
  })
  check(invalidResponse.status === 404, 'invalid cycle returns a browser-observed 404')

  await page.route('**/api/formula-explorer/calculate?*', async (route) => {
    await route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: 'Cycle 99999 is not available in Sheet1 of batch 1.' }) })
  })
  await batchSelect.selectOption('1')
  await waitForOptions(profileSelect)
  await page.getByRole('button', { name: 'Calculate candidate' }).click()
  await page.getByRole('alert').filter({ hasText: 'Cycle 99999' }).waitFor({ timeout: 10000 })
  check(await page.getByRole('alert').filter({ hasText: 'Cycle 99999' }).isVisible(), 'invalid calculation displays an actionable UI error')
  await screenshot('06_invalid_calculation_error')
  await page.unroute('**/api/formula-explorer/calculate?*')

  await page.getByRole('link', { name: 'VoltTwin home' }).click()
  await page.getByRole('heading', { name: /Understand your battery's/i }).waitFor()
  check(page.url().endsWith('/#'), 'brand navigation returns to homepage')
  check(await page.getByText('Battery configuration', { exact: true }).isVisible(), 'homepage remains usable after navigation')

  const result = {
    browser: 'Google Chrome',
    framework: 'Playwright',
    executable: chromePath,
    passed: passed.length,
    passed_checks: passed,
    console_errors: consoleErrors,
    page_errors: pageErrors,
    failed_requests: failures,
    critical_responses: criticalResponses,
    client_error_responses: expectedClientErrors,
    screenshots: fs.readdirSync(screenshotDir).filter((name) => name.endsWith('.png')).sort(),
  }
  await browser.close()
  console.log(JSON.stringify(result, null, 2))
}

main().catch((error) => {
  console.error(error.stack || error)
  process.exitCode = 1
})
