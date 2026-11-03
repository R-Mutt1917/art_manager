import { test, expect } from '@playwright/test';

const USERS = {
  admin: { email: 'dueno@demo.com', password: 'demo1234', rol: 'ADMIN' },
  curador: { email: 'curador@demo.com', password: 'demo1234', rol: 'CURADOR' },
  asesor: { email: 'asesor@demo.com', password: 'demo1234', rol: 'ASESOR' },
  viewer: { email: 'viewer@demo.com', password: 'demo1234', rol: 'VIEWER' },
};

test.describe('Matriz de Permisos por Rol', () => {
  for (const [nombreRol, usuario] of Object.entries(USERS)) {
    test.describe(`Rol: ${nombreRol}`, () => {
      
      test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:4321/login');
        await page.locator('#email').fill(usuario.email);
        await page.locator('#password').fill(usuario.password);
        await page.locator('button[type="submit"]').click();
        await expect(page).not.toHaveURL(/.*\/login.*/);
      });

      // Inventario: ADMIN, CURADOR, ASESOR pueden entrar; VIEWER es redirigido
      test(`acceso a /inventario (${nombreRol})`, async ({ page }) => {
        await page.goto('http://localhost:4321/inventario');
        if (nombreRol === 'admin' || nombreRol === 'curador' || nombreRol === 'asesor') {
          await expect(page).toHaveURL(/\/inventario/);
        } else {
          await expect(page).toHaveURL(/\/catalogo/);
        }
      });

      // Crear: solo ADMIN y CURADOR pueden entrar
      test(`acceso a /crear (${nombreRol})`, async ({ page }) => {
        await page.goto('http://localhost:4321/crear');
        if (nombreRol === 'admin' || nombreRol === 'curador') {
          await expect(page).toHaveURL(/\/crear/);
          await expect(page.locator('h1, h2')).toContainText(/crear|nueva/i);
        } else {
          // Asesor y Viewer son redirigidos al catálogo por el middleware
          await expect(page).toHaveURL(/\/catalogo/);
        }
      });

      // Dashboard: ADMIN, CURADOR, ASESOR pueden entrar; VIEWER es redirigido
      test(`acceso a /dashboard (${nombreRol})`, async ({ page }) => {
        await page.goto('http://localhost:4321/dashboard');
        if (nombreRol === 'admin' || nombreRol === 'curador' || nombreRol === 'asesor') {
          await expect(page).toHaveURL(/\/dashboard/);
          await expect(page.locator('h1, h2')).toContainText(/dashboard|métricas|estadísticas/i);
        } else {
          await expect(page).toHaveURL(/\/catalogo/);
        }
      });

      // Técnicas: solo ADMIN y CURADOR pueden entrar
      test(`acceso a /tecnicas (${nombreRol})`, async ({ page }) => {
        await page.goto('http://localhost:4321/tecnicas');
        if (nombreRol === 'admin' || nombreRol === 'curador') {
          await expect(page).toHaveURL(/\/tecnicas/);
          await expect(page.locator('h1, h2')).toContainText(/técnicas/i);
        } else {
          await expect(page).toHaveURL(/\/catalogo/);
        }
      });
    });
  }
});