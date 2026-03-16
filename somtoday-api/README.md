# Somtoday API & AI Portaal

Dit is een simpele lokale API-server die praat met **Somtoday**.
Je kunt deze tool gebruiken om via een simpele webpagina je rooster en huiswerk in te zien.
Daarnaast is deze opzet speciaal gemaakt zodat je in de toekomst makkelijk AI-tools (zoals ChatGPT of vergelijkbare lokale AI's) de opdracht kunt geven: *"Bekijk mijn rooster voor morgen"* of *"Wat is mijn huiswerk?"*. De AI kan dan simpelweg deze API bevragen.

---

## 🚀 De makkelijkste manier om te starten (met het .bat bestand)

Om dit zo eenvoudig mogelijk te maken is er een speciaal opstart-script (`start_somtoday.bat`) in de hoofdmap geplaatst. Zo werkt het:

### 1. Wat heb je nodig?
Zorg dat je [Node.js](https://nodejs.org/en) geïnstalleerd hebt op je computer (hier is geen technische kennis voor nodig, gewoon downloaden en "volgende" klikken tot het afgerond is).

### 2. Starten met één klik
1. Zoek naar het bestand **`start_somtoday.bat`** in de hoofdmap (dus nét buiten de `somtoday-api` map).
2. **Dubbelklik hierop!**
3. Het script zal nu automatisch alle lastige installatiestappen voor je overslaan (het downloadt zelf wat het nodig heeft op de achtergrond).

### 3. Inloggegevens Invullen
De allereerste keer dat je op het `.bat` bestand klikt, zal hij merken dat je nog geen inloggegevens hebt ingesteld.
Hij maakt dan automatisch een `.env` bestand voor je aan.
- Open dit `.env` bestand in Kladblok.
- Vul achter `SCHOOL=` de naam in van je school (bijv: "Mijn Middelbare").
- Vul je `USERNAME=` (leerlingnummer) en `PASSWORD=` in.

*Let op: Dit is helemaal veilig. Dit bestand staat lokaal op je computer, je inloggegevens worden alleen gebruikt om te kletsen met Somtoday, ze worden door niemand anders opgeslagen.*

### 4. Portaal gebruiken
Klik nogmaals op het **`start_somtoday.bat`** bestand als je je inloggegevens hebt ingevuld.
- Je browser opent vanzelf.
- Er blijft een zwart schermpje open staan: **sluit dit niet**, want dit zorgt ervoor dat de code kan nadenken op de achtergrond.
- Je kunt nu in je browser op de knoppen klikken voor je rooster en huiswerk.

---

## 🌐 De Website (Gebruikersinterface)
Als de server draait, open je gewoon je webbrowser (zoals Chrome of Edge) en ga je naar:
**[http://localhost:3000](http://localhost:3000)**

Hier zie je of je succesvol bent ingelogd en vind je knoppen om je **Rooster** en **Huiswerk** op te halen.

---

## 🤖 Voor de AI (Hoe kan de AI hiermee praten?)

De server biedt 3 handige "Endpoints" (URL's) die simpel te lezen zijn voor AI. Ze geven zogenoemde JSON data terug (dat snapt AI super goed).

1. **Status check:** `GET http://localhost:3000/api/status`
   *(Check of je bent ingelogd)*
2. **Rooster ophalen:** `GET http://localhost:3000/api/rooster`
   *(Haalt de afspraken en het lesrooster op voor de komende 7 dagen)*
3. **Huiswerk ophalen:** `GET http://localhost:3000/api/huiswerk`
   *(Haalt al het aankomende huiswerk, leerwerk en toetsen op)*

Als je later een AI (Agent) instelt, kan je hem simpelweg de opdracht geven: *"Verbind met http://localhost:3000/api/rooster en vertel me welke vakken ik morgen heb."*
De AI zal dit vlekkeloos kunnen oppakken!