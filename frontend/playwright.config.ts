import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 90000,
  expect: { timeout: 10000 },
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:5173/static/",
    headless: true,
    actionTimeout: 15000,
    viewport: { width: 1440, height: 1000 },
  },
  webServer: [
    {
      command:
        process.platform === "win32"
          ? "..\\.venv\\Scripts\\python.exe tests/run_backend.py"
          : "../.venv/bin/python tests/run_backend.py",
      url: "http://127.0.0.1:8000/api/health/",
      reuseExistingServer: false,
      timeout: 120000,
    },
    {
      command: "npm run dev -- --port 5173 --strictPort",
      url: "http://127.0.0.1:5173/static/",
      reuseExistingServer: false,
    },
  ],
});
