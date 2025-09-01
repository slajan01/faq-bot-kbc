# KBC FAQ Bot - Propojení Copilot Studia a Azure Functions

Tento projekt demonstruje kompletní propojení konverzačního agenta vytvořeného v **Microsoft Copilot Studiu** s vlastní backendovou logikou hostovanou v **Azure Function** (Python). Komunikace je orchestrována pomocí **Power Automate** a standardizována přes **Vlastní konektor (Custom Connector)**.

---
## Architektura a Průběh Konverzace

Celé řešení je postaveno na čtyřech klíčových komponentách, které spolu komunikují a provádějí uživatele celým procesem dotazu a odpovědi.

### Architektura
Tok dat probíhá v následujícím pořadí:

```
Uživatel
   |
   v
[1. Copilot Studio Téma] ---------------------> (Spouští tok s dotazem uživatele)
   |
   v
[2. Power Automate Tok] ----------------------> (Volá akci v konektoru)
   |
   v
[3. Vlastní Konektor (Custom Connector)] -----> (Volá Azure Function API)
   |
   v
[4. Azure Function (Python)] -----------------> (Zpracuje dotaz a vrací JSON)
   |
   `----<----<----<----<----<----<----<----<---- (Odpověď se vrací stejnou cestou zpět)
```
### Příklad Konverzace s Vysvětlením

Zde je ukázka, jak tato architektura funguje v praxi a co jednotlivé kroky znamenají:

**Vy:** `mám dotaz`
> **Vysvětlení:** Uživatel použije spouštěcí frázi. Tím dává botovi signál, že chce aktivovat speciální schopnost hledání v externí databázi, nikoliv vést běžnou konverzaci.

**Bot:** `Dobře, na co přesně se chcete zeptat?`
> **Vysvětlení:** Copilot spustil správné Téma. Nyní pokládá upřesňující otázku, aby získal konkrétní dotaz, který následně pošle ke zpracování.

**Vy:** `Jaké jsou poplatky za vedení účtu?`
> **Vysvětlení:** Uživatel poskytuje finální dotaz. Tato hodnota se uloží do proměnné a bezpečně se předá přes Power Automate a konektor až do Azure funkce.

**Bot:** `Testovací odpověď z Azure Function pro dotaz: 'Jaké jsou poplatky za vedení účtu?'`
> **Vysvětlení:** Toto je finální odpověď, kterou bot obdržel přímo z našeho interního systému (Azure funkce). Dokazuje to, že celý řetězec propojení od začátku do konce úspěšně funguje.

1.  **Copilot Studio (Frontend):** Stará se o vedení konverzace s uživatelem, rozpoznání záměru (pomocí frází nebo popisu) a volání Power Automate toku.
2.  **Power Automate (Orchestrátor):** Slouží jako "lepidlo". Přijímá data z Copilota, volá konektor, zpracovává odpověď (pomocí klíčového kroku **Parsovat JSON**) a vrací výsledek zpět.
3.  **Vlastní konektor (Adaptér):** Standardizovaný "obal" kolem Azure funkce, který umožňuje Power Platformě snadno komunikovat s API pomocí OpenAPI specifikace.
4.  **Azure Function (Backend):** "Mozek" operace. V tomto projektu jsou dvě funkce:
    * `faq`: Hlavní funkce, která přijímá dotaz a vrací odpověď.
    * `swagger_get`: Pomocná funkce, která servíruje ručně vytvořený `swagger.json` soubor.

---
## Použité Technologie
* Microsoft Copilot Studio
* Microsoft Power Automate
* Microsoft Power Platform (pro Vlastní konektory)
* Microsoft Azure Functions (Python 3.9+)
* OpenAPI (Swagger)

---
## Struktura Projektu
```
/
|-- faq/
|   |-- __init__.py      # Hlavní logika pro odpovědi
|   `-- function.json
|-- swagger_get/
|   |-- __init__.py      # Funkce pro servírování swagger.json
|   `-- function.json
|-- .gitignore
|-- host.json
|-- requirements.txt     # Závislosti pro Python (jen azure-functions)
`-- swagger.json         # Ručně vytvořená OpenAPI specifikace 
```

---
## Nastavení a Konfigurace

1.  **Azure Function:**
    * Nasaďte obě funkce (`faq` a `swagger_get`) do jedné Function App v Azure.
    * Získejte URL adresu funkce `swagger_get` a její **Function Key** pro ověření.
2.  **Vlastní Konektor:**
    * V `make.powerapps.com` vytvořte nový Vlastní konektor.
    * Jako zdroj importujte OpenAPI ze souboru `swagger.json` nebo z URL adresy funkce `swagger_get`.
    * V sekci "Zabezpečení" nastavte ověřování typu **Klíč rozhraní API (API Key)**. Jako název parametru zadejte `x-functions-key` a umístění nastavte na `Hlavička (Header)`.
3.  **Power Automate Tok:**
    * Vytvořte tok spouštěný z Copilot Studia (Power Virtual Agents).
    * Přidejte akci volající váš nový Vlastní konektor.
    * Přidejte klíčový krok **"Parsovat JSON"**, který zpracuje `Tělo (Body)` odpovědi z konektoru. Schéma vygenerujte z ukázky: `{ "answer": "test" }`.
    * Přidejte finální krok **"Vrátit hodnotu(y) do Power Virtual Agents"** a do výstupní proměnné `answer` vložte `Body answer` z kroku "Parsovat JSON".
4.  **Copilot Studio Téma:**
    * Vytvořte nové Téma.
    * Nastavte spouštěč (buď pomocí **frází**, nebo **popisu** pro Generativní AI).
    * Přidejte uzel "Položit otázku" pro získání dotazu od uživatele.
    * Přidejte uzel "Zavolat akci" a vyberte váš vytvořený Power Automate tok. Propojte vstupní a výstupní proměnné.
    * Přidejte uzel "Odeslat zprávu" pro zobrazení finální odpovědi.

---
## Klíčové poznatky 
* **Problémy se závislostmi třetích stran:** Automatická generace OpenAPI specifikace pomocí knihovny `azure-functions-openapi` se ukázala jako nespolehlivá kvůli nekompatibilitě se současným prostředím Azure. Ruční vytvoření `swagger.json` je robustnější alternativou.
* **Explicitní parsování v Power Automate:** Pro spolehlivé předání dat z konektoru zpět do Copilota je naprosto zásadní použít akci **"Parsovat JSON"**. Bez ní tok sice může skončit úspěšně, ale data se do Copilota nepředají ve správném formátu.
* **Vývoj UI v Copilot Studiu:** Rozhraní se rychle mění. Je důležité rozumět rozdílu mezi klasickým spouštěčem na bázi **frází** a novým generativním přístupem na bázi **popisu** tématu.

---
## 🚀 GIF LIVE DEMO BOT

![Ukázka konverzace s KBC Botem](assets/demo.gif)