const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:5173';
const USERNAME = 'test_clinic';
const PASSWORD = 'zaq12wsx8262';

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();

  console.log('🚀 Navigating to login page...');
  await page.goto(TARGET_URL, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(1000);

  // Take screenshot of login page to debug
  await page.screenshot({ path: '/tmp/login-page.png', fullPage: true });
  console.log('📸 Login page screenshot saved');

  // Debug: List all input fields
  const inputs = await page.locator('input').all();
  console.log(`🔍 Found ${inputs.length} input fields`);
  for (let i = 0; i < inputs.length; i++) {
    const type = await inputs[i].getAttribute('type');
    const name = await inputs[i].getAttribute('name');
    const placeholder = await inputs[i].getAttribute('placeholder');
    console.log(`   Input ${i}: type="${type}", name="${name}", placeholder="${placeholder}"`);
  }

  // Login - try different selectors
  console.log('🔐 Logging in...');

  // Find username field (could be email or username)
  const usernameField = page.locator('input').first();
  const passwordField = page.locator('input[type="password"]');

  await usernameField.fill(USERNAME);
  await page.waitForTimeout(200);
  await passwordField.fill(PASSWORD);
  await page.waitForTimeout(200);

  // Screenshot before submit
  await page.screenshot({ path: '/tmp/before-submit.png', fullPage: true });

  // Find and click submit button
  const submitBtn = page.locator('button[type="submit"], button:has-text("Sign"), button:has-text("Log")');
  await submitBtn.click();
  console.log('👆 Clicked submit button');

  // Wait for navigation - either URL change or network idle
  try {
    await page.waitForURL('**/app/**', { timeout: 10000 });
    console.log('✅ Navigated to app');
  } catch (e) {
    console.log('⚠️ URL did not change to /app/**, checking current state...');
    await page.waitForTimeout(2000);
  }

  // Take screenshot after login attempt
  await page.screenshot({ path: '/tmp/after-login.png', fullPage: true });
  console.log('📸 After login screenshot saved');
  console.log('📍 Current URL:', page.url());

  // If still on login page, there might be an error
  if (page.url().includes('login') || page.url() === TARGET_URL + '/') {
    console.log('⚠️ Still on login page, checking for errors...');
    const errorMsg = await page.locator('[class*="error"], [class*="alert"], .text-red').textContent().catch(() => null);
    if (errorMsg) {
      console.log('❌ Login error:', errorMsg);
    }
  }

  // Navigate to calendar-v2
  console.log('📅 Navigating to calendar-v2...');
  await page.goto(`${TARGET_URL}/app/appointment/calendar-v2`, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(3000);

  // Take screenshot
  await page.screenshot({ path: '/tmp/calendar-v2-initial.png', fullPage: true });
  console.log('📸 Calendar page screenshot saved');
  console.log('📍 Current URL:', page.url());
  console.log('📄 Page title:', await page.title());

  // Check if we got redirected back to login
  if (page.url().includes('login')) {
    console.log('❌ Got redirected to login page. Authentication may have failed.');
    await browser.close();
    return;
  }

  // Wait for calendar to load
  await page.waitForTimeout(2000);

  // Look for slot cards (appointment cards) on the calendar
  const slotCards = await page.locator('.slot-card').all();
  console.log(`📅 Found ${slotCards.length} slot cards on the calendar`);

  if (slotCards.length < 2) {
    console.log('⚠️ Need at least 2 slot cards to test hover overlap.');

    // Try to find any cards that might have hover behavior
    const anyCards = await page.locator('[class*="slot"], [class*="card"], [class*="event"]').all();
    console.log(`🔍 Found ${anyCards.length} potential card elements`);

    await page.screenshot({ path: '/tmp/calendar-v2-cards.png', fullPage: true });

    if (slotCards.length === 0) {
      console.log('ℹ️ No appointment cards found. The calendar may be empty for today.');
    }
  }

  if (slotCards.length >= 2) {
    // Test 1: Hover over first card
    console.log('\n🧪 Test 1: Single card hover');
    const firstCard = slotCards[0];
    await firstCard.hover();
    await page.waitForTimeout(200);

    const hoverCards1 = await page.locator('.hover-card-popup, .fixed.z-\\[9999\\]').all();
    console.log(`📦 Hover cards visible: ${hoverCards1.length}`);

    await page.screenshot({ path: '/tmp/calendar-v2-hover-single.png', fullPage: true });

    // Test 2: Rapid hover between cards
    console.log('\n🧪 Test 2: Rapid hover between cards (overlap test)');
    const secondCard = slotCards[1];

    await firstCard.hover();
    await page.waitForTimeout(150);
    await page.screenshot({ path: '/tmp/calendar-v2-hover-first.png', fullPage: true });

    await secondCard.hover({ force: true });
    await page.waitForTimeout(30);

    const hoverCardsDuringTransition = await page.locator('.hover-card-popup, .fixed.z-\\[9999\\]').all();
    console.log(`📦 Hover cards during rapid transition: ${hoverCardsDuringTransition.length}`);

    if (hoverCardsDuringTransition.length > 1) {
      console.log('⚠️ OVERLAP DETECTED: Multiple hover cards visible simultaneously!');
    }

    await page.screenshot({ path: '/tmp/calendar-v2-overlap-test.png', fullPage: true });

    // Test 3: Stress test
    console.log('\n🧪 Test 3: Stress test');
    for (let i = 0; i < Math.min(slotCards.length, 5); i++) {
      await slotCards[i].hover({ force: true });
      await page.waitForTimeout(50);

      const currentHoverCards = await page.locator('.hover-card-popup, .fixed.z-\\[9999\\]').all();
      if (currentHoverCards.length > 1) {
        console.log(`⚠️ Overlap at card ${i + 1}: ${currentHoverCards.length} hover cards`);
        await page.screenshot({ path: `/tmp/calendar-v2-stress-overlap-${i}.png`, fullPage: true });
      }
    }

    await page.screenshot({ path: '/tmp/calendar-v2-stress-test-final.png', fullPage: true });
  }

  console.log('\n📊 Test Summary:');
  console.log('- Screenshots saved to /tmp/calendar-v2-*.png');

  await page.waitForTimeout(2000);
  await browser.close();
  console.log('\n✅ Test completed');
})();
