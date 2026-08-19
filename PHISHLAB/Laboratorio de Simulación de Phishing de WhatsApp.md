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

# 📘 Laboratorio: Simulación de Phishing de WhatsApp

> **⚠️ Uso exclusivamente académico y controlado**
>
> Este laboratorio tiene como objetivo demostrar, en un entorno autorizado, cómo funciona una campaña de ingeniería social basada en phishing y cómo identificar sus indicadores de riesgo.
>
> **No se deben utilizar credenciales, códigos OTP, números telefónicos reales ni cuentas de terceros.**

---

## 📌 Información del laboratorio

| Campo | Información |
|---|---|
| 👨‍🎓 Estudiante | Miguel Ramirez Meli |
| 🆔 Matrícula | 2025-1367 |
| 📚 Materia | Hacker Ético 1 |
| 👨‍🏫 Profesor | Nelson Mieses |
| 🏫 Institución | ITLA |
| 🎯 Técnica | Phishing / Ingeniería Social |
| 🧪 Entorno | Kali Linux |
| 🛠️ Herramientas | SET Toolkit, ngrok |
| 🔐 Tipo | Simulación controlada |

---

# 🎯 Objetivo

El objetivo de esta práctica es demostrar de manera controlada cómo una campaña de phishing puede utilizar:

- Ingeniería social.
- Mensajes de urgencia.
- Suplantación visual de servicios conocidos.
- Páginas web falsas.
- Enlaces externos.
- Solicitudes de información aparentemente legítimas.

La práctica también busca enseñar al usuario a reconocer señales de phishing y proteger sus cuentas frente a intentos de ingeniería social.

---

# 🧠 Conceptos utilizados

## Phishing

El phishing es una técnica de ingeniería social mediante la cual un atacante intenta engañar a una persona para que visite un sitio falso o proporcione información sensible.

## Ingeniería social

Consiste en manipular psicológicamente al usuario para conseguir que realice una acción que normalmente no realizaría.

Algunas técnicas utilizadas son:

- 🚨 Sensación de urgencia.
- ⚠️ Amenazas o consecuencias negativas.
- 🔐 Solicitudes de verificación.
- 🎭 Suplantación de identidad.
- 🔗 Enlaces aparentemente legítimos.

---

# 🖥️ FASE 1 — Preparación de Kali Linux

Actualizar los repositorios:

```bash
sudo apt update
sudo apt upgrade -y
```

Instalar SET Toolkit:

```bash
sudo apt install set -y
```

Instalar ngrok siguiendo la documentación oficial correspondiente a la versión utilizada en el laboratorio.

> **Nota:** El token de autenticación de ngrok nunca debe publicarse en GitHub.

---

# 📁 FASE 2 — Preparación del laboratorio

Crear el directorio de trabajo:

```bash
mkdir -p ~/whatsapp_phishing
cd ~/whatsapp_phishing
```

Crear la página de simulación:

```bash
nano index.html
```

La página debe utilizar **datos ficticios** y mostrar claramente que se trata de una simulación cuando finalice el ejercicio.

Ejemplo de estructura:

```text
whatsapp_phishing/
├── index.html
├── README.md
├── evidencias/
│   ├── captura-01.png
│   ├── captura-02.png
│   └── captura-03.png
└── informe/
    └── informe.pdf
```

---

# 🔧 FASE 3 — SET Toolkit

Para la demostración académica se puede utilizar SET Toolkit para estudiar el flujo de una campaña de ingeniería social.

```bash
sudo setoolkit
```

Menú utilizado durante la demostración:

```text
1 → Social-Engineering Attacks
2 → Website Attack Vectors
3 → Credential Harvester Attack Method
```

> ⚠️ En este laboratorio no deben recolectarse credenciales reales ni códigos de autenticación de terceros.

---

# 🔗 FASE 4 — Túnel HTTPS

Para una demostración controlada puede utilizarse un túnel HTTPS temporal.

Ejemplo:

```bash
ngrok http 80
```

La herramienta proporcionará una dirección temporal.

### 🔐 Importante

La URL generada:

- No debe utilizarse para engañar a personas no autorizadas.
- No debe distribuirse públicamente.
- Debe utilizarse únicamente dentro del alcance autorizado de la práctica.
- Debe desactivarse al finalizar el laboratorio.

---

# 📨 FASE 5 — Simulación del correo

El correo utilizado en la práctica debe formar parte de un escenario académico previamente autorizado.

Ejemplo conceptual:

> **Asunto:** Simulación académica de seguridad — WhatsApp
>
> Hola [Participante],
>
> Como parte de una práctica de seguridad informática, recibirás una simulación de un mensaje de phishing.
>
> El objetivo es evaluar si puedes identificar señales de ingeniería social antes de interactuar con el enlace.
>
> Recuerda verificar siempre:
>
> - El dominio del sitio.
> - El remitente.
> - El contexto del mensaje.
> - Las solicitudes de códigos de autenticación.
> - La existencia de amenazas o mensajes de urgencia.

---

# 🧪 FASE 6 — Ejecución de la simulación

Durante la práctica se evalúan principalmente los siguientes indicadores:

| Indicador | Riesgo |
|---|---|
| 🚨 Mensaje urgente | Alto |
| ⚠️ Amenaza de pérdida de cuenta | Alto |
| 🔗 URL desconocida | Alto |
| 🎭 Suplantación de marca | Alto |
| 🔐 Solicitud de código OTP | Crítico |
| 📱 Solicitud de número telefónico | Medio/Alto |
| 🌐 Dominio diferente al oficial | Alto |

### Datos utilizados

Todos los datos deben ser ficticios:

```text
Número de prueba:
+1 809 000 0000

Código de prueba:
000000
```

**Nunca utilizar códigos reales enviados por WhatsApp, bancos, correo electrónico u otros servicios.**

---

# 🗣️ FASE 7 — Revelación de la simulación

Una vez terminada la actividad, se debe explicar inmediatamente al participante que se trataba de una práctica académica.

Ejemplo:

> Hola. Soy estudiante del Tecnólogo en Seguridad del ITLA y esta actividad forma parte de una práctica de Hacker Ético con el profesor Nelson Mieses.
>
> El mensaje que recibiste era una simulación de phishing diseñada para demostrar cómo funciona la ingeniería social.
>
> El objetivo no era obtener información real, sino demostrar lo fácil que puede ser para un usuario confiar en un mensaje aparentemente legítimo.
>
> Algunas señales que debías identificar eran la urgencia, la amenaza de filtración, el enlace externo y la solicitud de información de autenticación.
>
> Para proteger tus cuentas:
>
> - Nunca compartas códigos de verificación.
> - Activa la autenticación en dos pasos.
> - Comprueba cuidadosamente las URL.
> - No confíes en mensajes que generen miedo o urgencia.
> - Accede a los servicios desde sus aplicaciones o sitios oficiales.

---

# 📸 FASE 8 — Evidencias

Las evidencias recomendadas son:

### Evidencia 01 — Página de simulación

Captura de la interfaz utilizada durante el laboratorio.

```text
evidencias/captura-01-pagina.png
```

### Evidencia 02 — Mensaje de simulación

Captura del correo o mensaje utilizado dentro del entorno autorizado.

```text
evidencias/captura-02-mensaje.png
```

### Evidencia 03 — Terminal

Captura del funcionamiento de las herramientas durante la práctica.

```text
evidencias/captura-03-terminal.png
```

> No incluir números telefónicos reales, códigos OTP, contraseñas, tokens, cookies ni información personal en las capturas.

---

# 📊 Resultado

La evaluación puede documentarse mediante una tabla como la siguiente:

| Aspecto | Resultado |
|---|---|
| El participante abrió el mensaje | Sí / No |
| Identificó la URL sospechosa | Sí / No |
| Detectó la suplantación | Sí / No |
| Identificó la solicitud de código | Sí / No |
| Reportó el intento | Sí / No |
| Reconoció la técnica de phishing | Sí / No |

### Análisis

El resultado permite determinar qué elementos visuales y psicológicos pueden influir en la toma de decisiones de los usuarios.

La práctica demuestra que la seguridad no depende únicamente de controles técnicos. La capacitación y concientización de los usuarios también son componentes fundamentales de la seguridad informática.

---

# 🛡️ Concientización

Los códigos de verificación son información sensible y no deben compartirse con terceros.

Un atacante puede intentar obtenerlos mediante:

- Phishing.
- Ingeniería social.
- Suplantación de soporte técnico.
- Mensajes falsos de seguridad.
- Sitios web fraudulentos.

Ante una solicitud inesperada de un código:

> **Detente → verifica → no compartas el código.**

También es recomendable utilizar mecanismos adicionales de seguridad, mantener las aplicaciones actualizadas y acceder a los servicios desde sus aplicaciones o dominios oficiales.

---

# 🔐 Buenas prácticas

- ✅ Verificar siempre el dominio.
- ✅ No introducir información sensible en enlaces sospechosos.
- ✅ No compartir códigos OTP.
- ✅ Activar la verificación en dos pasos.
- ✅ Desconfiar de mensajes con amenazas.
- ✅ Evitar hacer clic en enlaces inesperados.
- ✅ Reportar mensajes sospechosos.
- ✅ Utilizar contraseñas únicas.
- ✅ Mantener actualizado el sistema operativo.
- ✅ Realizar prácticas de phishing únicamente con autorización.

---

# 📂 Estructura final del proyecto

```text
.
├── README.md
├── index.html
├── evidencias/
│   ├── captura-01-pagina.png
│   ├── captura-02-mensaje.png
│   └── captura-03-terminal.png
│
└── informe/
    └── informe.pdf
```

---

# 📄 Informe PDF

El informe final debe contener:

1. **Portada**
   - Nombre.
   - Matrícula.
   - Materia.
   - Profesor.
   - Institución.

2. **Objetivo**
   - Objetivos establecidos en el enunciado.

3. **Metodología**
   - Kali Linux.
   - SET Toolkit.
   - Página de simulación.
   - HTTPS.
   - ngrok.
   - Ingeniería social.

4. **Evidencias**
   - Capturas del laboratorio.
   - Página de simulación.
   - Mensaje utilizado.
   - Terminal.

5. **Resultados**
   - Comportamiento observado.
   - Indicadores identificados.
   - Análisis de la actividad.

6. **Concientización**
   - Riesgos del phishing.
   - Protección de códigos de verificación.
   - Recomendaciones de seguridad.

7. **Anexos**
   - Enlace al video de la práctica.
   - Evidencias adicionales.

---

# ⚠️ Consideraciones de seguridad

Este proyecto es exclusivamente educativo.

No utilizar esta metodología para:

- ❌ Robar cuentas.
- ❌ Obtener códigos OTP reales.
- ❌ Capturar contraseñas reales.
- ❌ Suplantar servicios frente a usuarios no autorizados.
- ❌ Distribuir enlaces maliciosos.
- ❌ Acceder a cuentas de terceros.
- ❌ Almacenar información personal de participantes.

Toda prueba debe realizarse con **autorización previa y dentro de un entorno controlado**.

---

# 🎓 Conclusión

La práctica permitió estudiar el funcionamiento de una campaña de phishing desde la perspectiva de un laboratorio de seguridad ofensiva.

El principal aprendizaje es que un usuario puede convertirse en un objetivo vulnerable cuando un atacante combina una apariencia legítima con elementos psicológicos como urgencia, miedo y confianza.

Por esta razón, la educación del usuario, la autenticación multifactor y la verificación de enlaces constituyen medidas importantes para reducir el riesgo de ataques de ingeniería social.

---

## 👨‍💻 Autor

**Miguel Ramirez Meli**

**Matrícula:** `2025-1367`

**ITLA — Hacker Ético 1**

**Profesor:** Nelson Mieses

---

<div align="center">

### 🛡️ Ethical Hacking • Cybersecurity • Social Engineering

<img src="https://img.shields.io/badge/Kali%20Linux-557C94?style=flat-square&logo=kalilinux&logoColor=white" />
<img src="https://img.shields.io/badge/SET%20Toolkit-red?style=flat-square&logo=linux&logoColor=white" />
<img src="https://img.shields.io/badge/ngrok-1F1E37?style=flat-square&logo=ngrok&logoColor=white" />
<img src="https://img.shields.io/badge/Phishing%20Simulation-orange?style=flat-square&logo=security&logoColor=white" />

</div>