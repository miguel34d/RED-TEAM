# Guía para resolver los laboratorios de PortSwigger

Esta guía explica, paso a paso y en lenguaje sencillo, cómo crear la cuenta en PortSwigger y resolver los cuatro laboratorios pedidos.

---

## Paso 0: Crear la cuenta

1. Entra a https://portswigger.net/web-security
2. Haz clic en **"Sign up"** (arriba a la derecha) o en el botón que diga algo como "Access all labs free".
3. Completa el registro con tu correo y crea tu contraseña.
4. Confirma tu cuenta desde el correo que te llega.
5. Inicia sesión. Ya puedes entrar a cualquiera de los laboratorios.

Cada laboratorio tiene, arriba de todo, un botón que dice **"Access the lab"**. Al hacer clic ahí se abre una copia privada del sitio vulnerable, con una dirección única que termina en `.web-security-academy.net`. Ahí es donde se resuelve todo.

---

## Laboratorio 1: Unprotected admin functionality

**Qué hay que lograr:** entrar al panel de administración sin haber iniciado sesión, y borrar al usuario "carlos".

### Pasos

1. Abre el laboratorio 1: https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality → "Access the lab".
2. En la URL que se abrió, agrega al final `/robots.txt` y presiona Enter.
   - Ejemplo: `https://xxxxx.web-security-academy.net/robots.txt`
3. Ahí va a aparecer un texto corto. Busca la línea que empieza con `Disallow:` — esa es la ruta escondida del panel de administración (algo como `/administrator-panel`).
4. Copia esa ruta y ponla en la URL en lugar de `/robots.txt`.
   - Ejemplo: `https://xxxxx.web-security-academy.net/administrator-panel`
5. Vas a entrar directo, sin que te pida usuario ni contraseña. Ahí vas a ver una lista de usuarios.
6. Haz clic en **"Delete"** al lado del usuario **carlos**.
7. Arriba a la derecha, donde decía "Not solved", debería cambiar a **"Solved"**.

### Qué capturar como evidencia
- El contenido de `robots.txt` con la ruta revelada.
- El panel de administración abierto sin haber iniciado sesión.
- El mensaje de "Solved" al final.

### Por qué pasa esto (para la explicación del informe)
La aplicación no protege el panel con ninguna verificación real de sesión ni de permisos: simplemente confía en que nadie va a encontrar la dirección. Como la ruta queda expuesta en `robots.txt`, cualquiera puede entrar directamente.

---

## Laboratorio 2: Username enumeration via different responses

**Qué hay que lograr:** descubrir un nombre de usuario válido y su contraseña, comparando las respuestas del formulario de login, y luego iniciar sesión con esas credenciales.

Este laboratorio necesita **Burp Suite** (versión gratuita, Community Edition), instalada en tu computadora.

### Instalar Burp Suite (si no lo tienes)

- Descárgalo desde: https://portswigger.net/burp/communitydownload
- En Linux (por ejemplo Fedora), desde la terminal:
  ```bash
  wget -O burpsuite_community.sh "https://portswigger.net/burp/releases/download?product=community&type=Linux"
  chmod +x burpsuite_community.sh
  ./burpsuite_community.sh
  ```
- Sigue el instalador (Next, Next, hasta terminar).
- Ábrelo, elige **"Temporary project"** → Next → **"Use Burp defaults"** → **Start Burp**.

### Pasos del laboratorio

1. Abre el laboratorio 2: https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-different-responses → "Access the lab".
2. En Burp Suite, ve a la pestaña **Proxy → Intercept**, y haz clic en **"Open browser"**. Se abre una ventana de navegador conectada a Burp.
3. En esa ventana, entra al laboratorio y haz clic en **"My account"** para llegar al login.
4. Escribe cualquier usuario y contraseña de prueba (por ejemplo `test` / `test`) y dale **"Log in"**.
5. En Burp, con "Intercept on" activado, vas a ver la petición congelada, con algo como:
   `username=test&password=test`
6. Haz clic derecho sobre esa petición → **"Send to Intruder"**.
7. Ve a la pestaña **Intruder**. Selecciona solo la palabra del nombre de usuario (por ejemplo `test`) y haz clic en **"Add §"**, para que quede así: `username=§test§&password=test`.
8. En el panel de "Payloads" (a la derecha), carga la lista de nombres de usuario. En la página del laboratorio hay un enlace que dice algo como **"candidate usernames"** — descárgalo y cárgalo con el botón **"Load..."**.
9. Haz clic en **"Start attack"**.
10. En la tabla de resultados, ordena por la columna **"Length"**. Casi todas las filas van a tener el mismo número, salvo una o dos que se destacan — ese es el usuario real.
11. Repite el mismo proceso, pero esta vez deja fijo el usuario encontrado y marca la contraseña con `§ §`. Carga la lista de **"candidate passwords"** del laboratorio.
12. Lanza el ataque de nuevo. Busca la fila cuyo **"Status code"** sea distinto a las demás (normalmente 302 en vez de 200) — esa es la contraseña correcta.
13. Ve al navegador, inicia sesión con el usuario y la contraseña encontrados.
14. Debería aparecer **"Solved"**.

### Qué capturar como evidencia
- La petición de login interceptada.
- La posición marcada con `§ §` para el usuario.
- Los resultados del ataque, con la fila del usuario válido resaltada.
- Lo mismo para la contraseña (la fila con el código 302).
- El login exitoso y el "Solved".

### Por qué pasa esto
El sistema responde de forma distinta según si el usuario existe o no (cambia el tamaño o el contenido del mensaje de error). Eso permite, desde afuera, deducir qué usuarios son reales sin necesidad de adivinar la contraseña primero.

---

## Laboratorio 3: OS command injection, simple case

**Qué hay que lograr:** aprovechar un campo vulnerable para ejecutar un comando del sistema operativo en el servidor.

### Pasos

1. Abre el laboratorio 3: https://portswigger.net/web-security/os-command-injection/lab-simple → "Access the lab".
2. Entra a cualquier producto de la tienda (haz clic en él).
3. Con Burp Suite interceptando (Proxy → Intercept, "Intercept on"), haz clic en el botón **"Check stock"**.
4. Va a aparecer una petición interceptada con dos datos, algo como:
   `productId=1&storeId=1`
5. Modifica el valor de `storeId` agregando al final `|whoami`, sin espacios, quedando así:
   `productId=1&storeId=1|whoami`
6. Haz clic en **"Forward"** para enviar la petición modificada.
7. Ve a la pestaña **"HTTP history"**, busca la última petición a `/product/stock` y ábrela.
8. Revisa la pestaña **"Response"**: ahí debería aparecer el nombre de un usuario del sistema (resultado del comando `whoami`) en vez del número de inventario normal.
9. Vuelve al navegador y revisa si el laboratorio ya quedó marcado como **"Solved"**.

### Qué capturar como evidencia
- La página del producto usado.
- La petición interceptada con `storeId` modificado.
- La respuesta del servidor mostrando el resultado del comando.
- El mensaje de "Solved".

### Por qué pasa esto
La aplicación toma el valor que se le manda en `storeId` y lo pega directamente dentro de un comando del sistema operativo, sin revisar qué caracteres trae. Al incluir el símbolo `|`, se le puede agregar un segundo comando que también se ejecuta.

---

## Laboratorio 4: Reflected XSS

**Qué hay que lograr:** lograr que el navegador ejecute un código JavaScript a través de la barra de búsqueda del sitio.

### Pasos

1. Abre el laboratorio 4: https://portswigger.net/web-security/cross-site-scripting/reflected → busca el recuadro verde de "LAB" y haz clic ahí para entrar al laboratorio real (no te quedes en la página de teoría).
2. En la página del blog que se abre, busca la barra de búsqueda.
3. Escribe exactamente esto:
   ```
   <script>alert(1)</script>
   ```
4. Presiona buscar o Enter.
5. Debería aparecer una ventana emergente con el número **1**.
6. El laboratorio se marca automáticamente como **"Solved"**.

### Qué capturar como evidencia
- El texto ingresado en la barra de búsqueda.
- La ventana emergente ejecutándose.
- El mensaje de "Solved".

### Por qué pasa esto
La página toma el texto que se escribe en la búsqueda y lo repite tal cual dentro del código HTML de la respuesta, sin convertir los caracteres especiales (`<`, `>`). Por eso el navegador interpreta ese texto como código real y lo ejecuta.

---

## Resumen para el informe final

Para cada laboratorio, el informe debe incluir:

1. **Capturas de pantalla** de cada paso importante y del resultado final ("Solved").
2. **Explicación breve** de la vulnerabilidad (ya está resumida al final de cada sección de esta guía, en "Por qué pasa esto").
3. **Payload o técnica usada**:
   - Lab 1: acceso directo a `/administrator-panel` descubierto vía `robots.txt`.
   - Lab 2: `username=§candidato§&password=...` y luego `username=apollo&password=§candidato§` con Intruder.
   - Lab 3: `storeId=1|whoami`.
   - Lab 4: `<script>alert(1)</script>`.
4. **Evidencia de resolución**: la captura de "Solved" de cada laboratorio.

El informe se puede entregar en Word o convertido a PDF, según lo que pida la consigna.
