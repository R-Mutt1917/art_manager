import { test, expect } from '@playwright/test';

test.describe('Flujo completo: crear, ver y editar obra', () => {
  test('debe permitir crear una obra, verla en detalle y editarla', async ({ page }) => {
    // 1. Login como admin
    await page.goto('/login');
    await page.fill('input[type="email"]', 'dueno@demo.com');
    await page.fill('input[type="password"]', 'demo1234');
    await page.click('button[type="submit"]');
    await page.waitForURL('/inventario');

    // 2. Crear nueva obra
    await page.goto('/crear');
    await page.fill('input#titulo', 'Obra E2E Test');
    await page.fill('input#anio', '2024');
    await page.fill('input#dimensiones', '50x50 cm');
    await page.fill('input#precio', '1000');
    await page.fill('textarea#notas', 'Obra creada por test E2E');
    
    // Seleccionar técnica (autocomplete)
    await page.fill('input#tecnica', 'Óleo sobre lienzo');
    await page.waitForTimeout(500); // Esperar sugerencias
    await page.keyboard.press('Enter');
    
    // Guardar
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000); // Esperar redirección
    
    // 3. Verificar que se creó (debería estar en /obras/X)
    const currentUrl = page.url();
    expect(currentUrl).toMatch(/\/obras\/\d+/);
    
    // 4. Verificar datos en la página de detalle
    await expect(page.locator('h1')).toContainText('Obra E2E Test');
    await expect(page.locator('body')).toContainText('2024');
    await expect(page.locator('body')).toContainText('50x50 cm');
    
    // 5. Click en "Editar"
    await page.click('a[href*="/editar"]');
    await page.waitForURL(/\/obras\/\d+\/editar/);
    
    // 6. Modificar título
    await page.fill('input#titulo', 'Obra E2E Test - Editada');
    await page.click('button[type="submit"]');
    
    // 7. Verificar cambio
    await expect(page.locator('h1')).toContainText('Obra E2E Test - Editada');
  });
});