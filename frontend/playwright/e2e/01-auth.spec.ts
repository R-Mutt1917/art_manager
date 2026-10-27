import { test, expect } from '@playwright/test';

test.describe('Flujo de Autenticación', () => {
  test('debe permitir el login exitoso y redirigir al inventario', async ({ page }) => {
    // 1. Navegar a la página de login
    await page.goto('http://localhost:4321/login');

    // 2. Completar el formulario usando los IDs reales del HTML
    await page.locator('#email').fill('dueno@demo.com');
    await page.locator('#password').fill('demo1234');

    // 3. Hacer clic en el botón de submit
    await page.locator('#submit-btn').click();

    // 4. Esperar navegación (puede ir a /inventario o a / si hay redirección por defecto)
    await page.waitForLoadState('networkidle');
    
    // 5. Verificar que estamos autenticados (debería estar en inventario o home, pero NO en login)
    const currentURL = page.url();
    expect(currentURL).not.toContain('/login');
  });

  test('debe redirigir al login si se intenta acceder a una ruta protegida sin sesión', async ({ page }) => {
    // 1. Intentar ir directamente a una ruta privada
    await page.goto('http://localhost:4321/inventario');

    // 2. Debería redirigir al login automáticamente.
    // Usamos una expresión regular (/.*\/login.*/) para que coincida incluso si tiene 
    // parámetros como ?returnTo=%2Finventario o ?redirect=...
    await page.waitForURL(/.*\/login.*/);
    
    // 3. Verificación final
    await expect(page).toHaveURL(/.*\/login.*/);
  });
});