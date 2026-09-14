import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests', testMatch: 'workspace*.spec.ts', fullyParallel: false,
  timeout: 30000, expect: { timeout: 8000 }, workers: 1,
  use: { baseURL: 'http://127.0.0.1:4322', channel: 'chrome', headless: true, viewport: {width:1280,height:800}, screenshot: 'only-on-failure' },
  webServer: { command: 'npm run dev -- --host 127.0.0.1 --port 4322', url: 'http://127.0.0.1:4322', reuseExistingServer: true },
});
