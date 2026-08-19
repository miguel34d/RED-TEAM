<div align="center">
  <img src="https://img.shields.io/badge/Estudiante-Miguel%20Ramirez%20Meli-blue?style=flat-square&logo=github&logoColor=white" />
  <img src="https://img.shields.io/badge/Matrícula-2025--1367-blue?style=flat-square&logo=id-card&logoColor=white" />
  <img src="https://img.shields.io/badge/Materia-Hacker%20%C3%89tico%201-orange?style=flat-square&logo=book&logoColor=white" />
  <img src="https://img.shields.io/badge/Profesor-Nelson%20Mieses-orange?style=flat-square&logo=chalkboard-teacher&logoColor=white" />
  <img src="https://img.shields.io/badge/Institución-ITLA-grey?style=flat-square&logo=school&logoColor=white" />
  <br>
  <img src="https://img.shields.io/badge/Estado-Resuelto-brightgreen?style=flat-square&logo=check&logoColor=white" />
  <img src="https://img.shields.io/badge/Ataque-Phishing-orange?style=flat-square&logo=shield&logoColor=white" />
</div>

<br>

# 📘 Laboratorio de Phishing Simulado de WhatsApp

> **⚠️ Aviso académico:** Este proyecto fue realizado con fines educativos dentro de un laboratorio controlado de Hacker Ético. La demostración debe utilizar únicamente participantes autorizados y datos ficticios. No se deben recopilar contraseñas, códigos SMS, códigos 2FA ni información personal real.

---

## 👨‍🎓 Información del estudiante

| Campo | Información |
|---|---|
| **Estudiante** | Miguel Ramirez Meli |
| **Matrícula** | 2025-1367 |
| **Materia** | Hacker Ético 1 |
| **Profesor** | Nelson Mieses |
| **Institución** | ITLA |
| **Tipo de práctica** | Simulación de Phishing |
| **Estado** | Resuelto |

---

# 🎯 Objetivo

Demostrar, dentro de un entorno controlado, cómo funciona una campaña de ingeniería social basada en phishing y cómo una página falsa puede utilizar elementos visuales y mensajes de urgencia para intentar engañar a un usuario.

La práctica busca:

1. Identificar las características de un ataque de phishing.
2. Crear una simulación visual de una página de inicio de sesión.
3. Analizar el comportamiento del usuario frente a mensajes de urgencia.
4. Identificar indicadores que permitan detectar páginas fraudulentas.
5. Concientizar sobre la protección de códigos de verificación y datos personales.

---

# 🛠️ Tecnologías utilizadas

- 🐉 Kali Linux
- 🧰 Social-Engineer Toolkit (SET)
- 🌐 Servidor web local
- 🔗 ngrok
- 📄 HTML
- 🎨 CSS
- ⚙️ JavaScript
- 📧 Correo electrónico
- 🔐 Ingeniería social
- 🛡️ Concientización de seguridad

---

# 🖥️ FASE 1 — Preparar Kali Linux

## 1. Actualizar el sistema

```bash
sudo apt update && sudo apt upgrade -y
```

## 2. Instalar SET Toolkit

```bash
sudo apt install set -y
```

## 3. Instalar ngrok

```bash
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null

echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" | sudo tee /etc/apt/sources.list.d/ngrok.list

sudo apt update

sudo apt install ngrok -y
```

## 4. Configurar ngrok

Después de crear una cuenta en ngrok, configurar el token correspondiente:

```bash
ngrok config add-authtoken "AQUI_VA_TU_AUTHTOKEN"
```

> 🔐 **Importante:** nunca publiques tu authtoken en GitHub ni dentro de capturas de pantalla.

---

# 📝 FASE 2 — Crear la página de simulación

Crear el directorio del laboratorio:

```bash
mkdir -p ~/whatsapp_phishing
cd ~/whatsapp_phishing
```

Crear el archivo:

```bash
nano index.html
```

### 📌 Página HTML

El código HTML de la simulación se encuentra en el archivo correspondiente del repositorio.

Después de abrir `index.html`, copia el contenido del HTML disponible en el proyecto:

```text
COPIAR EL HTML DEL ARCHIVO DEL REPOSITORIO
```

Guardar:

```text
Ctrl + O
Enter
Ctrl + X
```

### ⚠️ Alcance de la simulación

La página debe utilizar:

- Datos ficticios.
- Números de prueba.
- Códigos ficticios.
- Ningún almacenamiento de credenciales reales.
- Ningún código 2FA real.
- Ninguna contraseña real.
- Ninguna información personal de terceros.

El objetivo es demostrar **el engaño visual y la ingeniería social**, no obtener acceso a cuentas reales.

---

# 🔧 FASE 3 — Levantar el entorno de laboratorio

Desde la terminal:

```bash
cd ~/whatsapp_phishing
```

Para iniciar el entorno de demostración:

```bash
sudo setoolkit
```

Dentro del laboratorio se puede utilizar la estructura de:

```text
1 → Social-Engineering Attacks
2 → Website Attack Vectors
3 → Credential Harvester Attack Method
```

> ⚠️ Para una práctica segura, la demostración debe utilizar exclusivamente información ficticia y participantes que hayan autorizado expresamente la prueba.

---

# 🔗 FASE 4 — Túnel HTTPS con ngrok

Abrir una segunda terminal.

Ejecutar:

```bash
ngrok http 80
```

El servicio mostrará una dirección pública temporal similar a:

```text
https://ejemplo.ngrok-free.dev
```

Esta dirección únicamente debe compartirse con participantes autorizados dentro del laboratorio.

### 🔐 Recomendaciones

- No publicar la URL en redes sociales.
- No enviar la URL a personas que no participan en la práctica.
- No utilizarla para suplantar servicios reales fuera del laboratorio.
- Detener el túnel cuando termine la demostración.

---

# 📨 FASE 5 — Simulación del correo de phishing

## Asunto utilizado

```text
⚠️ SIMULACIÓN ACADÉMICA: Verificación de seguridad de WhatsApp
```

## Ejemplo de mensaje

```text
Hola [Nombre]:

Este mensaje forma parte de una simulación académica de
ingeniería social.

Se está realizando una prueba controlada para demostrar
cómo los mensajes de urgencia pueden llevar a un usuario
a visitar una página falsa.

🔗 Enlace de laboratorio:
[URL DEL LABORATORIO]

Esta actividad forma parte de una práctica de Hacker Ético.

- Laboratorio de Seguridad
```

> ⚠️ No utilizar mensajes que amenacen con publicar conversaciones reales ni hacerse pasar por el equipo oficial de WhatsApp fuera de un entorno autorizado.

---

# 🎯 FASE 6 — Demostración

Durante la demostración se observa:

- Si el participante identifica el correo sospechoso.
- Si revisa el dominio.
- Si verifica el remitente.
- Si detecta el mensaje de urgencia.
- Si reconoce elementos visuales falsificados.
- Si intenta introducir información.

### Datos de prueba

Para la demostración utilizar únicamente información ficticia:

```text
Número de prueba:
809 000 0000

Código de prueba:
000000
```

### Resultado esperado

El laboratorio debe demostrar que una página visualmente similar a un servicio conocido puede generar confianza en el usuario.

**No se deben capturar códigos reales de WhatsApp.**

---

# 🗣️ FASE 7 — Discurso de revelación

> Hola [Nombre].
>
> Soy estudiante del tecnólogo en Seguridad del ITLA y estoy cursando la materia Hacker Ético 1 con el profesor Nelson Mieses.
>
> La actividad que acabas de realizar forma parte de una simulación académica de phishing.
>
> El objetivo era demostrar cómo un atacante puede utilizar una situación de emergencia, una página visualmente similar a un servicio conocido y un enlace externo para intentar generar confianza.
>
> Esta demostración utiliza únicamente datos ficticios y no permite acceder a ninguna cuenta real.
>
> Para protegerte:
>
> - Nunca compartas códigos de verificación.
> - No introduzcas códigos 2FA en páginas a las que llegaste desde enlaces sospechosos.
> - Revisa siempre el dominio.
> - Desconfía de mensajes que generen miedo o urgencia.
> - Verifica las solicitudes directamente desde la aplicación oficial.
> - Activa las medidas de seguridad disponibles en tus cuentas.
>
> El objetivo de la práctica es aprender a reconocer este tipo de ataques antes de que puedan causar daños reales.

---

# 📸 FASE 8 — Evidencias

El informe debe incluir capturas de:

### 1. Entorno de Kali Linux

```text
Captura de la terminal mostrando la preparación
del laboratorio.
```

### 2. Página de simulación

```text
Captura de la página utilizada durante la demostración.
```

### 3. Correo de prueba

```text
Captura del correo utilizado para la simulación.
```

### 4. Túnel HTTPS

```text
Captura de ngrok mostrando el túnel activo.
```

### 5. Resultado

```text
Captura donde se demuestre el resultado de la simulación.
```

> 🔒 Antes de subir las evidencias a GitHub, ocultar números telefónicos, correos electrónicos, tokens, direcciones privadas y cualquier otro dato personal.

---

# 📊 FASE 9 — Resultado

## ¿La víctima ingresó los datos?

```text
Respuesta:
[COMPLETAR CON EL RESULTADO DE LA SIMULACIÓN]
```

## ¿La víctima sospechó del mensaje?

```text
Respuesta:
[COMPLETAR]
```

## ¿Qué indicadores de phishing fueron identificados?

```text
- Mensaje alarmista.
- Sensación de urgencia.
- Solicitud de verificación.
- Enlace externo.
- Dominio diferente al servicio legítimo.
- Uso de elementos visuales similares.
```

---

# 🛡️ FASE 10 — Concientización

El phishing aprovecha principalmente el comportamiento humano y no únicamente vulnerabilidades técnicas.

Los atacantes pueden utilizar:

- Miedo.
- Urgencia.
- Curiosidad.
- Autoridad.
- Confianza.
- Falsas alertas de seguridad.

Un usuario debe comprobar siempre la dirección del sitio web antes de introducir información sensible.

### 🔐 Regla principal

> **Un código de verificación es confidencial. Nunca debe compartirse con otra persona ni introducirse en una página sospechosa.**

---

# 🔍 Indicadores de una página sospechosa

| Indicador | Riesgo |
|---|---|
| Dominio desconocido | 🔴 Alto |
| Mensaje alarmista | 🟠 Medio/Alto |
| Solicitud de código 2FA | 🔴 Alto |
| Enlace recibido por correo | 🟠 Medio |
| Errores ortográficos | 🟠 Medio |
| Solicitud de información personal | 🔴 Alto |
| URL diferente al servicio oficial | 🔴 Alto |
| Presión para actuar inmediatamente | 🔴 Alto |

---

# 🧪 Arquitectura del laboratorio

```text
                    ┌─────────────────────┐
                    │     PARTICIPANTE    │
                    │     autorizado      │
                    └──────────┬──────────┘
                               │
                               │ HTTPS
                               ▼
                    ┌─────────────────────┐
                    │        ngrok        │
                    │  Túnel del lab      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Kali Linux      │
                    │                     │
                    │  Servidor web       │
                    │  Página simulada    │
                    └─────────────────────┘
```

---

# 📁 Estructura del proyecto

```text
whatsapp_phishing/
│
├── index.html
│
├── README.md
│
├── evidencias/
│   ├── 01-kali.png
│   ├── 02-pagina.png
│   ├── 03-correo.png
│   ├── 04-ngrok.png
│   └── 05-resultado.png
│
└── informe/
    └── informe-final.pdf
```

---

# 📄 FASE 11 — Informe escrito

El PDF debe contener:

## Portada

- Nombre: Miguel Ramirez Meli
- Matrícula: 2025-1367
- Profesor: Nelson Mieses
- Materia: Hacker Ético 1
- Institución: ITLA
- Nombre de la práctica

## Objetivo

Incluir los objetivos establecidos en el enunciado de la práctica.

## Metodología

Explicar:

```text
1. Preparación de Kali Linux.
2. Configuración del entorno de laboratorio.
3. Creación de la página de simulación.
4. Configuración del acceso HTTPS.
5. Realización de la simulación.
6. Observación del comportamiento.
7. Revelación de la actividad.
8. Concientización del participante.
```

## Evidencias

Agregar las capturas correspondientes.

## Resultado

Explicar:

- Qué ocurrió.
- Si el participante detectó el phishing.
- Qué elementos generaron sospecha.
- Qué elementos generaron confianza.

## Concientización

Explicar la importancia de:

- Proteger códigos de verificación.
- Revisar URLs.
- Evitar enlaces sospechosos.
- No actuar bajo presión.
- Utilizar aplicaciones oficiales.

## Anexos

Agregar:

```text
Enlace al video de la práctica:
[PEGAR ENLACE AQUÍ]
```

---

# ✅ Resumen de comandos

## Preparar directorio

```bash
mkdir -p ~/whatsapp_phishing
cd ~/whatsapp_phishing
```

## Crear HTML

```bash
nano index.html
```

> Copiar el HTML de simulación disponible en el repositorio.

## Iniciar SET

```bash
sudo setoolkit
```

## Iniciar ngrok

En otra terminal:

```bash
ngrok http 80
```

## Finalizar laboratorio

Cuando termine la demostración:

```text
Ctrl + C
```

para detener los servicios correspondientes.

---

# ⚠️ Consideraciones de seguridad

Este repositorio tiene finalidad **educativa y académica**.

No utilizar este proyecto para:

- Robar cuentas.
- Capturar credenciales reales.
- Capturar códigos SMS.
- Capturar códigos 2FA.
- Suplantar personas.
- Distribuir malware.
- Engañar usuarios sin autorización.
- Obtener acceso no autorizado.
- Publicar información personal.

Todas las pruebas deben realizarse:

```text
✅ Con autorización
✅ En un entorno controlado
✅ Con datos ficticios
✅ Con participantes informados según las reglas de la práctica
✅ Con finalidad educativa
```

---

# 🎓 Conclusión

La práctica demuestra que el phishing puede combinar ingeniería social, diseño visual y mensajes de urgencia para intentar convencer a un usuario de realizar una acción insegura.

La principal defensa continúa siendo la combinación de:

**Educación + Concientización + Verificación + Medidas de seguridad.**

Un usuario que reconoce una URL sospechosa, desconfía de mensajes alarmistas y protege sus códigos de verificación puede reducir considerablemente el riesgo de comprometer su cuenta.

---

<div align="center">

### 🛡️ Hacker Ético 1 — ITLA

**Miguel Ramirez Meli**  
**Matrícula: 2025-1367**

<br>

<img src="https://img.shields.io/badge/Educational-Laboratory-blue?style=flat-square&logo=academia&logoColor=white" />
<img src="https://img.shields.io/badge/Security-Awareness-green?style=flat-square&logo=shield&logoColor=white" />
<img src="https://img.shields.io/badge/Phishing-Simulation-orange?style=flat-square&logo=hackthebox&logoColor=white" />

</div>
