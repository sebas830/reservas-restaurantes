# Despliegue de MkDocs a GitHub Pages

## 📋 Pasos para habilitar GitHub Pages en tu repositorio

### ✅ Estado: El workflow ya está configurado

El workflow de despliegue automático **ya existe** en `.github/workflows/mkdocs-pages.yml` y se ejecutará automáticamente cuando hagas push a `main`.

### 1. Configurar GitHub Pages en tu repositorio

1. Ve a tu repositorio en GitHub: https://github.com/sebas830/reservas-restaurantes
2. Haz clic en **Settings** (Configuración) en la barra superior
3. En la barra lateral izquierda, selecciona **Pages** (bajo "Code and automation")
4. En la sección **Build and deployment**:
   - **Source**: Selecciona **Deploy from a branch**
   - **Branch**: Selecciona **gh-pages** y **/ (root)**
5. Haz clic en **Save**

**⏱️ Espera 1-2 minutos** para que GitHub procese la configuración.

### 2. Hacer el primer push con documentación

```bash
# Desde tu terminal local
git add .
git commit -m "docs: configurar GitHub Pages para MkDocs"
git push origin main
```

### 3. Monitorear el despliegue

1. Ve a tu repositorio en GitHub
2. Haz clic en la pestaña **Actions** (arriba)
3. Busca el workflow: **"Desplegar documentación MkDocs a GitHub Pages"** (o similar)
4. Verifica que está **"in progress"** o **"completed"** (generalmente tarda 1-2 minutos)
5. Una vez completado (✅), tu documentación estará en:
   ```
   https://sebas830.github.io/reservas-restaurantes/
   ```

**💡 Tip**: Los workflow se ejecutan automáticamente cada vez que:
- Haces push a `main` con cambios en `docs/` o `mkdocs.yml`
- Ejecutas manualmente desde GitHub Actions

```bash
# Localmente, puedes construir y servir la documentación:
python3 -m venv .venv-docs
source .venv-docs/bin/activate
pip install -r requirements-docs.txt
mkdocs serve
```

Accede a: `http://127.0.0.1:8000`

## 🔧 Configuración adicional (opcional)

### Agregar dominio personalizado

Si tienes un dominio personalizado, crea un archivo `docs/CNAME` con:
```
tu-dominio.com
```

### Cambiar la rama de despliegue

Si prefieres desplegar desde una rama diferente, edita `.github/workflows/deploy-docs.yml`:
```yaml
on:
  push:
    branches:
      - main  # Cambia a la rama deseada
```

### Proteger la rama `gh-pages`

1. Ve a **Settings → Branches**
2. Haz clic en **Add rule**
3. Pattern: `gh-pages`
4. Marca **Dismiss stale pull request approvals when new commits are pushed**

## 📚 Estructura de documentación

La documentación se genera desde:
- Archivos en `docs/` (Markdown)
- Configuración en `mkdocs.yml`
- Dependencias en `requirements-docs.txt`

Para agregar nuevas páginas:
1. Crea un archivo `.md` en `docs/`
2. Actualiza la navegación en `mkdocs.yml`
3. Haz push a `main` y el workflow se ejecutará automáticamente

## ✅ Checklist

- [ ] He accedido a Settings → Pages
- [ ] He seleccionado `gh-pages` como rama de despliegue
- [ ] He hecho push de los cambios a `main`
- [ ] He visto que el workflow **"Deploy MkDocs to GitHub Pages"** se ejecutó correctamente
- [ ] He visitado `https://sebas830.github.io/reservas-restaurantes/` y confirmé que la documentación es visible

## 🆘 Solución de problemas

### El workflow falla al instalar dependencias
```bash
# Verifica que requirements-docs.txt existe y tiene las dependencias correctas
cat requirements-docs.txt
```

### La documentación no aparece
- Espera 2-3 minutos después del despliegue
- Recarga la página con `Ctrl+Shift+R` (caché)
- Verifica en **Settings → Pages** que está usando la rama `gh-pages`

### Cambios en `main` no se reflejan
- Verifica que el workflow se ejecutó en **Actions**
- Revisa los logs si hay errores
- Confirma que el archivo `mkdocs.yml` es válido (sin errores de YAML)

## 📖 Referencias

- [MkDocs Documentation](https://www.mkdocs.org/)
- [GitHub Pages with MkDocs](https://squidfunk.github.io/mkdocs-material/publishing-your-site/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
