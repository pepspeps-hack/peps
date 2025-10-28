# Private Crypter

Dit project is een private crypter die is ontworpen om `.exe`-bestanden te versleutelen en te verbergen voor beveiligingssoftware.

## Benodigdheden

Voordat je het script kunt uitvoeren, moet je ervoor zorgen dat de volgende software op je systeem (bijv. Ubuntu/Debian) is geïnstalleerd:

*   **build-essential**: Bevat basis C++ compilers en `make`.
    ```bash
    sudo apt-get update
    sudo apt-get install build-essential
    ```
*   **cmake**: Nodig om de projecten te bouwen.
    ```bash
    sudo apt-get install cmake
    ```
*   **mingw-w64**: Cross-compiler om Windows-bestanden te bouwen op Linux.
    ```bash
    sudo apt-get install mingw-w64
    ```

Het `build.sh` script zal automatisch controleren of deze software aanwezig is en je een foutmelding geven als er iets ontbreekt.

## Hoe te Gebruiken (Vereenvoudigd)

Het hele proces is geautomatiseerd. Volg gewoon deze drie simpele stappen.

### Stap 1: Plaats je EXE-bestand

*   Plaats het `.exe`-bestand dat je wilt versleutelen in de `input` map.

### Stap 2: Voer het Build Script uit

*   Open een terminal en voer het volgende commando uit in de hoofdmap van het project:
    ```bash
    ./build.sh
    ```
*   Het script zal automatisch alle benodigde tools compileren en je `.exe`-bestand versleutelen.

### Stap 3: Vind je Versleutelde Bestand

*   Het uiteindelijke, versleutelde `.exe`-bestand wordt opgeslagen in de `output` map. De naam wordt automatisch aangepast naar `[originele-naam]_crypted.exe`.

---

## Technische Details

### Componenten

*   **Builder**: De tool (gecompileerd voor Linux) die de payload (`.exe`) versleutelt met AES-256 en samenvoegt met de Stub.
*   **Stub**: De Windows loader (`stub.exe`) die de versleutelde payload in het geheugen ontsleutelt en injecteert in een legitiem proces (`svchost.exe`) via reflective loading.

### Beveiligingstechnieken

*   **AES-256 Encryptie**: Vervangt de simpele XOR-versleuteling voor robuuste bescherming.
*   **Dynamische IV**: Gebruikt een cryptografisch veilige, willekeurige IV voor elke versleuteling.
*   **Key Obfuscation**: De AES-sleutel is opgesplitst en wordt pas tijdens runtime in het geheugen samengevoegd.
*   **Reflective Loading**: De payload wordt nooit op de schijf geschreven, maar direct in het geheugen van een ander proces uitgevoerd.
*   **Stille Fouten**: De loader is ontworpen om stil te falen zonder foutmeldingen te tonen.
