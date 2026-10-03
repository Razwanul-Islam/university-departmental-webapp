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

test("record names open details on the dashboard and every resource screen", async ({
  page,
}) => {
  await login(page, "head");
  const carousel = page.getByRole("region", { name: "Workspace highlights" });
  await carousel.getByRole("button", { name: "Next highlight" }).click();
  await expect(carousel).toContainText("A clear plan. A confident next step.");
  await carousel.focus();
  await page.keyboard.press("ArrowLeft");
  await expect(carousel).toContainText("Your next chapter. All in one place.");
  await carousel.getByRole("button", { name: /Show highlight 3/ }).click();
  await carousel.getByRole("button", { name: "Discover your community" }).click();
  await expect(page.getByRole("heading", { name: "Clubs", exact: true }).first()).toBeVisible();
  await open(page, "dashboard");
  await expect(page.locator(".announcement .record-link").first()).toBeVisible();
  await page.screenshot({ path: "test-results/premium-dashboard.png", fullPage: true, animations: "disabled" });
  await page.locator(".announcement .record-link").first().click();
  await expect(
    page.getByRole("dialog").locator(".notice-content"),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await page.locator(".exam-preview .record-link").first().click();
  await expect(page.getByRole("dialog")).toContainText("Exam");
  await page.keyboard.press("Escape");

  for (const route of [
    "subjects",
    "classes",
    "enrollments",
    "exams",
    "results",
    "notices",
    "clubs",
    "users",
  ]) {
    await open(page, route);
    const name = page.locator("main .record-link").first();
    await expect(name).toBeVisible();
    await name.focus();
    await page.keyboard.press("Enter");
    await expect(
      page.getByRole("dialog").locator(".record-details"),
    ).toBeVisible();
    if (route === "classes")
      await expect(page.getByRole("dialog")).toContainText(
        "Data Structures & Algorithms",
      );
    if (route === "notices" || route === "clubs")
      await expect(
        page.getByRole("dialog").locator(".notice-content"),
      ).toBeVisible();
    if (route === "users")
      await expect(page.getByRole("dialog")).toContainText("Email");
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog")).not.toBeVisible();
    await expect(name).toBeFocused();
    if (route === "notices") {
      await page
        .getByRole("button", { name: "Read", exact: true })
        .first()
        .click();
      await expect(
        page.getByRole("dialog").locator(".notice-content"),
      ).toBeVisible();
      await page.keyboard.press("Escape");
    }
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Open navigation" }).click();
  await open(page, "dashboard");
  await expect(page.getByRole("heading", { name: "Overview", exact: true })).toBeVisible();
  await expect(page.getByRole("region", { name: "Workspace highlights" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: "test-results/premium-mobile.png", fullPage: true, animations: "disabled" });
  await page.emulateMedia({ reducedMotion: "reduce" });
  expect(await page.locator(".hero-floating").evaluate((element) => getComputedStyle(element).animationName)).toBe("none");

});
