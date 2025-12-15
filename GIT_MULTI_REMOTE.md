# Configuración Git Multi-Remote - GitHub y UCASAL

Este documento describe la configuración para hacer push simultáneo a dos repositorios remotos:
- **GitHub**: `https://github.com/Proyect/invoice-data-simple-AI.git`
- **UCASAL**: `http://git.ucasal.edu.ar/amdiaz/ocr.git`

## Configuración Inicial (Ya Completada)

### Credenciales Globales
Las credenciales de Git están configuradas globalmente:
```bash
git config --global user.name "ARIEL MARCELO DIAZ"
git config --global user.email "amdiaz@ucasal.edu.ar"
```

### Remotes Configurados
- **origin**: Apunta a GitHub (fetch y push)
- **ucasal**: Apunta al repositorio de UCASAL (fetch y push)
- **origin** tiene múltiples URLs de push configuradas para envío automático a ambos repositorios

## Verificar Configuración Actual

Para verificar la configuración de remotes:
```bash
git remote -v
```

Deberías ver:
```
origin	https://github.com/Proyect/invoice-data-simple-AI.git (fetch)
origin	https://github.com/Proyect/invoice-data-simple-AI.git (push)
origin	http://git.ucasal.edu.ar/amdiaz/ocr.git (push)
ucasal	http://git.ucasal.edu.ar/amdiaz/ocr.git (fetch)
ucasal	http://git.ucasal.edu.ar/amdiaz/ocr.git (push)
```

Para verificar credenciales globales:
```bash
git config --global user.name
git config --global user.email
```

## Métodos de Push

### Opción 1: Push Automático a Ambos (Recomendado)

Con la configuración actual, al ejecutar:
```bash
git push origin main
```

Se enviará automáticamente a **ambos** repositorios (GitHub y UCASAL) simultáneamente.

**Nota**: Si hay un error en uno de los repositorios, el push puede fallar. En ese caso, usa la Opción 2.

### Opción 2: Push Manual Separado

Si prefieres controlar cada push individualmente:

```bash
# Push solo a GitHub
git push origin main

# Push solo a UCASAL
git push ucasal main

# O hacer push a ambos manualmente
git push origin main && git push ucasal main
```

### Opción 3: Usar Scripts Helper

Se han creado scripts para facilitar el push simultáneo:

**Windows (PowerShell/Batch):**
```bash
.\push-all.bat main
```

**Linux/Mac:**
```bash
./push-all.sh main
```

## Comandos Útiles

### Ver información de un remote específico
```bash
git remote show origin
git remote show ucasal
```

### Cambiar la rama para push
```bash
# Para rama 'develop'
git push origin develop
git push ucasal develop
```

### Fetch desde ambos remotes
```bash
git fetch origin
git fetch ucasal
```

### Ver diferencias entre remotes
```bash
git log origin/main..ucasal/main
git diff origin/main ucasal/main
```

## Troubleshooting

### Error: "remote origin already exists"
Si intentas agregar un remote que ya existe, primero elimínalo:
```bash
git remote remove ucasal
git remote add ucasal http://git.ucasal.edu.ar/amdiaz/ocr.git
```

### Error de autenticación
Si tienes problemas de autenticación:

1. **Para GitHub**: Puede requerir token de acceso personal
   - Ve a GitHub Settings > Developer settings > Personal access tokens
   - Crea un token con permisos de repositorio
   - Usa el token como contraseña al hacer push

2. **Para UCASAL**: Verifica tus credenciales de la universidad
   - Puede requerir autenticación HTTP básica
   - Git te pedirá usuario y contraseña en el primer push

### Verificar conectividad
```bash
# Probar conexión a GitHub
git ls-remote origin

# Probar conexión a UCASAL
git ls-remote ucasal
```

### Resetear configuración de push múltiple
Si necesitas resetear la configuración de push múltiple en origin:
```bash
# Ver configuración actual
git remote get-url --push origin --all

# Resetear a una sola URL
git remote set-url origin https://github.com/Proyect/invoice-data-simple-AI.git
git remote set-url --add --push origin https://github.com/Proyect/invoice-data-simple-AI.git
git remote set-url --add --push origin http://git.ucasal.edu.ar/amdiaz/ocr.git
```

## Notas Importantes

1. **Credenciales Globales**: Las credenciales configuradas son globales y afectarán todos los repositorios Git en tu sistema.

2. **Repositorio UCASAL**: Asegúrate de que el repositorio en UCASAL exista y tengas permisos de escritura antes de hacer push.

3. **Ramas**: Asegúrate de que ambos repositorios tengan la misma rama (por ejemplo, `main` o `master`). Si las ramas tienen nombres diferentes, especifica la rama remota:
   ```bash
   git push origin main:main
   git push ucasal main:main
   ```

4. **Sincronización**: Si un repositorio se desincroniza, puedes forzar la sincronización (usar con precaución):
   ```bash
   git push origin main --force
   git push ucasal main --force
   ```

5. **Primera vez**: En el primer push a UCASAL, Git puede pedirte credenciales. Guárdalas usando:
   ```bash
   git config --global credential.helper store
   ```

## Estructura de Archivos

- `GIT_MULTI_REMOTE.md` - Esta documentación
- `push-all.sh` - Script para Linux/Mac
- `push-all.bat` - Script para Windows
- `.git/config` - Configuración de Git (no editar manualmente)

## Soporte

Para más información sobre Git remotes múltiples:
- [Git Documentation - Remotes](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes)
- [Git Documentation - Multiple Push URLs](https://git-scm.com/docs/git-remote#Documentation/git-remote.txt-remotenamepushurl)

