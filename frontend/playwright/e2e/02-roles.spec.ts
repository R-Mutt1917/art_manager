import { test, expect } from '@playwright/test';

// Datos de los usuarios demo
const USERS = {
  admin: { email: 'dueno@demo.com', password: 'demo1234', role: 'ADMIN' },
  curador: { email: 'curador@demo.com', password: 'demo1234', role: 'CURADOR' },
  asesor: { email: 'asesor@demo.com', password: 'demo1234', role: 'ASESOR' },
  viewer: { email: 'viewer@demo.com', password: 'demo1234', role: 'VIEWER' },
};

test.describe('Matriz de permisos por rol', () => {
  for (const [roleName, user] of Object.entries(USERS)) {
    test.describe(`Rol: ${roleName}`, () => {
      test.beforeEach(async ({ page }) => {
        // Login antes de cada test
        await page.goto('/login');
        await page.fill('input[type="email"]', user.email);
        await page.fill('input[type="password"]', user.password);
        await page.click('button[type="submit"]');
        await page.waitForURL('/inventario');
      });

      test(`debe poder ver el inventario`, async ({ page }) => {
        await expect(page.locator('body')).toContainText(/inventario|catálogo/i);
      });

      if (roleName === 'admin' || roleName === 'curador') {
        test(`debe poder crear una obra (${roleName})`, async ({ page }) => {
          await page.goto('/crear');
          await expect(page.locator('h1, h2')).toContainText(/crear|nueva/i);
          // Acá podrías completar el formulario y guardar
        });
      } else {
        test(`NO debe poder acceder a /crear (${roleName})`, async ({ page }) => {
          await page.goto('/crear');
          // Debería ver 403 o ser redirigido
          const url = page.url();
          expect(url).toMatch(/\/(login|inventario)/);
        });
      }

      if (roleName === 'admin' || roleName === 'asesor') {
        test(`debe poder ver el dashboard (${roleName})`, async ({ page }) => {
          await page.goto('/dashboard');
          await expect(page).toHaveURL('/dashboard');
        });
      } else {
        test(`NO debe poder ver dashboard (${roleName})`, async ({ page }) => {
          await page.goto('/dashboard');
          const url = page.url();
          expect(url).toMatch(/\/(login|inventario)/);
        });
      }
    });
  }
});