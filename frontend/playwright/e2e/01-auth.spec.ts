import { test, expect } from '@playwright/test';

test.describe('Autenticación', () => {
  test('debe permitir login con usuario demo y redirigir al inventario', async ({ page }) => {
    // 1. Navegar a /login
    await page.goto('/login');
    
    // 2. Completar el formulario
    await page.fill('input[type="email"]', 'dueno@demo.com');
    await page.fill('input[type="password"]', 'demo1234');
    
    // 3. Click en "Iniciar Sesión"
    await page.click('button[type="submit"]');
    
    // 4. Esperar navegación y verificar URL
    await page.waitForURL('/inventario');
    await expect(page).toHaveURL('/inventario');
    
    // 5. Verificar que ve el título del inventario
    await expect(page.locator('h1, h2')).toContainText(/inventario|catálogo/i);
  });

  test('debe redirigir a /login si intento acceder a /inventario sin auth', async ({ page }) => {
    // 1. Ir directo a ruta protegida
    await page.goto('/inventario');
    
    // 2. Debería redirigir a /login
    await page.waitForURL('/login');
    await expect(page).toHaveURL('/login');
  });
});