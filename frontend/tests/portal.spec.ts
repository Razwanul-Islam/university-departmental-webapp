import { test, expect, type Page } from "@playwright/test";

async function login(page: Page, role: string) {
  await page.goto("./");
  await page.getByLabel("Email address").fill(role + "@demo.edu");
  await page.getByLabel("Password", { exact: true }).fill("CampusDemo!2026");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Overview", exact: true }),
  ).toBeVisible();
}
async function open(page: Page, route: string) {
  await page.locator('nav a[href="#' + route + '"]').click();
}
test("head manages a subject; teacher records a result; student reads it", async ({
  page,
}) => {
  const suffix = Date.now();
  const title = "Browser subject " + suffix;
  await login(page, "head");
  await open(page, "subjects");
  await page.getByRole("button", { name: "New subject", exact: true }).click();
  await page.getByLabel("Subject name", { exact: true }).fill(title);
  await page.getByLabel("Subject code").fill("UI" + String(suffix).slice(-8));
  await page
    .getByLabel("Teacher", { exact: true })
    .selectOption({ label: "Farhana Rahman" });
  await page.getByRole("button", { name: "Save subject" }).click();
  await expect(
    page.getByRole("cell", { name: title, exact: true }),
  ).toBeVisible();
  await open(page, "classes");
  await page
    .getByRole("button", { name: "Edit class", exact: false })
    .first()
    .click();
  const select = page.getByLabel("Subjects", { exact: true });
  await expect(select).toBeVisible();
  const selected = await select
    .locator("option:checked")
    .evaluateAll((options) =>
      options.map((o) => (o as HTMLOptionElement).value),
    );
  const course = await select
    .locator("option")
    .filter({ hasText: title })
    .getAttribute("value");
  await select.selectOption([...selected, course!]);
  await page.getByRole("button", { name: "Save class" }).click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await open(page, "exams");
  await page.getByRole("button", { name: "New exam", exact: true }).click();
  await page
    .getByLabel("Exam name", { exact: true })
    .fill("Browser assessment " + suffix);
  await page
    .getByLabel("Subject", { exact: true })
    .selectOption({ label: title });
  await page.getByLabel("Exam date").fill("2026-12-15");
  await page.getByRole("button", { name: "Save exam" }).click();
  await expect(
    page.getByRole("cell", {
      name: "Browser assessment " + suffix,
      exact: true,
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "teacher");
  await open(page, "results");
  await page.getByRole("button", { name: "New result", exact: true }).click();
  await page
    .getByLabel("Subject", { exact: true })
    .selectOption({ label: title });
  await page
    .getByLabel("Exam", { exact: true })
    .selectOption({ label: "Browser assessment " + suffix });
  await page
    .getByLabel("Student", { exact: true })
    .selectOption({ label: "Ayesha Karim" });
  await page.getByLabel("Marks out of 100").fill("91");
  await page.getByRole("button", { name: "Save result" }).click();
  await expect(page.getByRole("row").filter({ hasText: title })).toContainText(
    "A+",
  );
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "student");
  await open(page, "results");
  await expect(page.getByRole("row").filter({ hasText: title })).toContainText(
    "91",
  );
  await expect(
    page.getByRole("button", { name: "New result", exact: true }),
  ).toHaveCount(0);
  await page.screenshot({
    path: "test-results/student-results.png",
    fullPage: true,
  });
});

test("student reads notices, joins a club, and edits their profile", async ({
  page,
}) => {
  await login(page, "student");
  await page.screenshot({
    path: "test-results/dashboard-desktop.png",
    fullPage: true,
  });
  await open(page, "notices");
  await page.getByRole("button", { name: "Read", exact: true }).first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await open(page, "clubs");
  const card = page
    .locator(".club-card")
    .filter({ hasText: "Programming Club" });
  if (await card.getByRole("button", { name: "Leave club" }).count())
    await card.getByRole("button", { name: "Leave club" }).click();
  await card.getByRole("button", { name: "Join club" }).click();
  await expect(card.getByText("Joined", { exact: true })).toBeVisible();
  await card.getByRole("button", { name: "Leave club" }).click();
  await expect(card.getByRole("button", { name: "Join club" })).toBeVisible();
  await page.getByRole("button", { name: "Open profile" }).click();
  await page.getByLabel("Full name").fill("Ayesha Karim");
  await page.getByRole("button", { name: "Save profile" }).click();
  await expect(page.getByRole("status")).toHaveText(
    "Your profile has been updated.",
  );
});

test("mobile navigation works without horizontal page overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page, "student");
  await page.screenshot({
    path: "test-results/dashboard-mobile.png",
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.getByRole("button", { name: "Open navigation" }).click();
  await open(page, "subjects");
  await expect(
    page.getByRole("heading", { name: "Subjects", exact: true }).first(),
  ).toBeVisible();
  await expect(page.locator(".sidebar")).not.toHaveClass(/open/);
});

test("registration creates a student with a useful empty dashboard", async ({
  page,
}) => {
  await page.goto("./");
  await page.getByRole("button", { name: "Create an account" }).click();
  await page.getByLabel("Full name").fill("New Campus Student");
  await page
    .getByLabel("Email address")
    .fill("browser" + Date.now() + "@example.edu");
  await page.getByLabel("Password", { exact: true }).fill("NewCampus!6428");
  await page.getByLabel("Confirm password").fill("NewCampus!6428");
  await page
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Overview", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "You're all caught up" }),
  ).toHaveCount(0);
  await expect(page.locator('nav a[href="#users"]')).toHaveCount(0);
  await open(page, "subjects");
  await expect(
    page.getByRole("heading", { name: "Nothing here yet" }),
  ).toBeVisible();
});

test("expired access refreshes automatically and sign-out survives an immediate reload", async ({
  page,
}) => {
  await login(page, "student");
  await page.evaluate(() => {
    const tokens = JSON.parse(sessionStorage.getItem("tokens")!);
    sessionStorage.setItem(
      "tokens",
      JSON.stringify({ ...tokens, access: "expired" }),
    );
  });
  const renewed = page.waitForResponse((r) =>
    r.url().endsWith("/api/user/refresh/"),
  );
  await page.reload();
  expect((await renewed).status()).toBe(200);
  await expect(
    page.getByRole("heading", { name: "Overview", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Welcome back", exact: true }),
  ).toBeVisible();
});
