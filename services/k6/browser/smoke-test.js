import { browser } from "k6/experimental/browser";
import { check } from "k6";
import { uuidv4 } from "https://jslib.k6.io/k6-utils/1.1.0/index.js";
export const options = {
  scenarios: {
    ui: {
      executor: "shared-iterations",
      options: {
        browser: {
          type: "chromium",
        },
      },
    },
  },
  thresholds: {
    checks: ["rate==1.0"],
  },
};

export default async function () {
  const page = browser.newPage();

  try {
    await page.goto("http://localhost:3000/create");

    page.locator('input[name="username"]').type(`user_${uuidv4()}`);
    page.locator('input[name="password"]').type("adminadminadmin");

    // Use text content to locate the submit button
    const submitButton = page.locator(
      "#__next > div > main > div > div > div > div > div > form > div.mt-6 > button"
    );

    // // Wait for the submit button to be available and click it
    // await submitButton.waitFor({ state: "visible" });
    await Promise.all([
      submitButton.click(), // Click the submit button
    ]);

    check(page, {
      header: (p) =>
        p
          .locator(
            "#__next > div > main > div > div > div > div > div > form > div.text-center.font-medium"
          )
          .textContent() == "User Account created successfully!",
    });
  } finally {
    page.close();
  }
}
