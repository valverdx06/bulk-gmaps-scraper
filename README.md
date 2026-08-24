# 🚀 Google Maps Lead Generator & Web Intelligence Scraper

Modular, high-performance Python script for automated lead extraction from Google Maps (worldwide support for USA, UK, Canada, Spain, Argentina, Brazil, etc.), enriched with web crawling for corporate **email addresses** and **social media profiles** (Facebook, Instagram, LinkedIn, Twitter/X), with direct exports to **Excel (`.xlsx`)** and **CSV (`.csv`)**.

---

## 📌 Core Features

- 🌍 **Worldwide Multi-Country & Multi-Language Support:** Operates seamlessly across any city or category in English, Spanish, Portuguese, French, etc.
- ⚡ **Dynamic Container Feed Scroll (`div[role="feed"]`):** Precise internal scroll handling inside Google Maps result feed.
- 🛡️ **Anti-Detection (Stealth Mode):** Powered by `playwright-stealth` and evasive Chromium flags to bypass bot checks and rate limits.
- ✉️ **Web Intelligence Enrichment (`web_enricher.py`):** Asynchronous crawling of business websites for emails and social media profile handles (`Facebook`, `Instagram`, `LinkedIn`, `Twitter / X`).
- 🔄 **Real-Time Lead Deduplication:** Filters duplicates by Google Place ID (`/maps/place/...`) to prevent repeated records.
- 📊 **Enriched 19-Column Output:** Styled Excel spreadsheets with navy blue headers, bold text, auto-adjusted column widths, and UTF-8 BOM CSV files.

---

## 🛠️ Prerequisites & Installation

### 1. Navigate to Project Directory
```bash
cd "/home/valverdx/Projects/Experimento 1"
```

### 2. Create & Activate Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

*(Note: On Debian/Ubuntu PEP 668 environments without virtualenv, add `--break-system-packages` if needed)*

### 4. Install Playwright Chromium Browser
```bash
playwright install chromium
```

---

## 🚀 Execution Modes

### Mode 1: Interactive Prompts (Recommended)
Simply run the script with no arguments, and it will prompt you step-by-step:
```bash
python main.py
```

### Mode 2: Command Line Interface (CLI Flags)

#### Multi-Country Examples:

**1. United States (USA):**
```bash
python main.py --category "Dental Clinics" --city "Miami" --country "USA" --max-results 20
```

**2. United Kingdom (UK):**
```bash
python main.py --category "Law Firms" --city "London" --country "UK" --max-results 15
```

**3. Spain:**
```bash
python main.py --category "Gyms" --city "Madrid" --country "Spain" --max-results 20
```

**4. Brazil:**
```bash
python main.py --category "Academias" --city "São Paulo" --country "Brazil" --max-results 20
```

**5. Direct Custom Query:**
```bash
python main.py --query "Boutique Hotels in Paris, France" --max-results 30
```

---

## ⚙️ CLI Options (`--help`)

| Option | Description |
| :--- | :--- |
| `-c`, `--category` | Business category or industry type (*e.g. Gyms, Dental Clinics, Lawyers*) |
| `-l`, `--city` | City or municipality (*e.g. London, Miami, Madrid*) |
| `-C`, `--country` | Country (*Optional, e.g. USA, UK, Spain*) |
| `-q`, `--query` | Direct full search query string |
| `-m`, `--max-results` | Maximum number of qualified leads to extract (Default: 20) |
| `--no-web-enrichment` | Disables website crawling for emails and social profiles |
| `--headful` | Runs Chromium with visible GUI browser window |

---

## 📂 Enriched 19-Column Output Schema

All generated lead reports are automatically saved to the `output/` directory:

```text
experimento_1/
└── output/
    ├── Gyms_in_Miami_USA.xlsx
    └── Gyms_in_Miami_USA.csv
```

### Extracted Data Fields:
1. **Business Name:** Official business title.
2. **Category:** Google Maps business classification (e.g. *Gym, Dentist, Law Firm*).
3. **Rating:** Star rating average (e.g. *4.8*).
4. **Reviews Count:** Total number of Google reviews.
5. **Phone Number:** International phone number.
6. **Email Address:** Contact email discovered on official website or contact subpages.
7. **Website URL:** Official business website link.
8. **Street Address:** Full street address.
9. **City:** Parsed city or municipality.
10. **Postal Code:** Parsed postal/zip code.
11. **Country:** Parsed country.
12. **Latitude:** Exact geographical latitude coordinate.
13. **Longitude:** Exact geographical longitude coordinate.
14. **Facebook Profile:** Official Facebook page link.
15. **Instagram Profile:** Official Instagram profile link.
16. **LinkedIn Profile:** Official LinkedIn company/personal page link.
17. **Twitter Profile:** Official Twitter / X profile link.
18. **Place ID:** Google Maps unique place identifier.
19. **Google Maps Link:** Direct URL to business listing on Google Maps.

---

## 📡 Ejecución Remota por SSH con Conda (Bulk US Perfume Scraper)

Para correr el scraper a gran escala (`bulk_us_perfume_scraper.py`) en un servidor o laptop remota vía SSH usando Conda:

### 1. Conexión SSH al Servidor
```bash
ssh <USUARIO>@<IP_SERVIDOR> -p <PUERTO>
```

### 2. Cargar entorno y navegar al directorio de proyectos
```bash
source ~/.bashrc
cd /opt/proyects
```

### 3. Clonar el repositorio
```bash
git clone <URL_DE_TU_REPOSITORIO>
cd Experimento-1   # O el nombre de la carpeta clonada
```

### 4. Configurar el entorno Conda automáticamente
```bash
bash setup_remote.sh
```
*O manualmente:*
```bash
conda env create -f environment.yml
conda activate gmaps-scraper
playwright install chromium
```

### 5. Ejecutar el Bulk Scraper

#### Opción A: Ejecución en segundo plano (Recomendada para SSH con `nohup`)
Permite cerrar la sesión SSH sin interrumpir el proceso de scraping:
```bash
bash run_bulk_scraper.sh 30000 32
```
- Monitorear progreso en tiempo real: `tail -f scraper.log`
- Filtrar leads capturados: `grep "✅" scraper.log`

#### Opción B: Ejecución con `tmux` (Sesión interactiva persistente)
```bash
tmux new -s scraper
conda activate gmaps-scraper
python bulk_us_perfume_scraper.py 30000 32
```
*(Para salir sin detener el proceso: presiona `Ctrl + B` y luego `D`. Para volver a entrar: `tmux attach -t scraper`)*

### 6. Descargar los resultados generados (.xlsx / .csv)
Desde tu máquina local:
```bash
scp -P <PUERTO> "<USUARIO>@<IP_SERVIDOR>:/opt/proyects/<NOMBRE_CARPETA>/output/*.xlsx" ./output/
```
