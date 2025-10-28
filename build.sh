#!/bin/bash

# Stop het script onmiddellijk als er een fout optreedt
set -e

echo "Automatisch build- en versleutelingsproces gestart..."

# --- Voorbereiding: Maak benodigde mappen aan ---
mkdir -p input
mkdir -p output

# --- Stap 1: Controleer of er een payload is ---
echo "1/4: Controleren op een .exe-bestand in de 'input' map..."

# Zoek naar het eerste .exe-bestand in de input map
PAYLOAD=$(ls input/*.exe 2>/dev/null | head -n 1)

if [ -z "$PAYLOAD" ]; then
    echo "FOUT: Geen .exe-bestand gevonden in de 'input' map."
    echo "Plaats het te versleutelen .exe-bestand in de 'input' map en probeer het opnieuw."
    exit 1
else
    echo "Payload gevonden: $PAYLOAD"
fi

# --- Stap 2: Compileer de Stub ---
echo "2/4: De Stub (loader) voor Windows aan het compileren..."

# Maak de build-directory aan als deze niet bestaat
mkdir -p stub/build

# Compileer de stub in een subshell om de directory niet te veranderen
(cd stub/build && cmake -DCMAKE_TOOLCHAIN_FILE=../mingw-w64-toolchain.cmake .. > /dev/null && make)
echo "Stub succesvol gecompileerd."

# --- Stap 3: Compileer de Builder ---
echo "3/4: De Builder (versleutelingstool) aan het compileren..."

# Maak de build-directory aan als deze niet bestaat
mkdir -p builder/build

# Compileer de builder
(cd builder/build && cmake .. > /dev/null && make)
echo "Builder succesvol gecompileerd."

# --- Stap 4: Versleutel de payload ---
echo "4/4: De payload aan het versleutelen..."

# Bepaal de naam voor het output-bestand
FILENAME=$(basename -- "$PAYLOAD")
FILENAME_NO_EXT="${FILENAME%.*}"
OUTPUT_FILE="output/${FILENAME_NO_EXT}_crypted.exe"

# Voer de builder uit met de juiste bestanden
./builder/build/builder stub/build/stub.exe "$PAYLOAD" "$OUTPUT_FILE"

echo ""
echo "----------------------------------------------------"
echo "PROCES VOLTOOID!"
echo "Je versleutelde bestand is opgeslagen als: $OUTPUT_FILE"
echo "----------------------------------------------------"
