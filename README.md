# DirittoTributarioHelper

Portale interattivo per supportare lo studio del diritto tributario. L'applicazione web, realizzata con Streamlit, interroga DuckDuckGo per reperire l'articolo normativo di riferimento, una spiegazione sintetica e un esempio pratico relativi all'argomento inserito.

## Panoramica del progetto

- **Interfaccia intuitiva**: tre schede (articolo, spiegazione, esempio) con risultati immediatamente consultabili e link alle fonti originali.
- **Ricerca web mirata**: per ogni scheda il portale costruisce query specializzate su DuckDuckGo, restituendo fino a 10 risultati per categoria.
- **Strumenti completamente gratuiti**: Streamlit per l'interfaccia, DuckDuckGo Search per le interrogazioni, pandas per la manipolazione dei dati, FPDF2 per l'esportazione in PDF e Python come linguaggio di sviluppo.
- **Cartella degli elementi necessari**: consulta `risorse/elementi_necessari.md` per un elenco sintetico dei prerequisiti hardware e software.

## Struttura delle cartelle

```
DirittoTributarioHelper/
├── README.md
├── requirements.txt
├── risorse/
│   └── elementi_necessari.md
└── tributary_portal/
    └── streamlit_app.py
```

## Guida passo-passo per Windows 11 con Visual Studio

Le istruzioni seguenti fanno riferimento a Visual Studio 2022 Community (gratuito) con il componente "Sviluppo desktop con Python", ma funzionano anche usando Visual Studio Code con terminale integrato.

1. **Installazione di Python**
   - Scarica il pacchetto Windows x64 da [python.org](https://www.python.org/downloads/windows/).
   - Durante l'installazione seleziona *Add Python to PATH* e completa la procedura guidata.

2. **Preparazione dell'ambiente in Visual Studio**
   - Apri Visual Studio.
   - Vai su `Visualizza > Terminale` per aprire il terminale integrato (ad esempio *Developer PowerShell* o *Prompt dei comandi*).
   - Naviga nella cartella dove vuoi salvare il progetto, ad esempio:
     ```powershell
     cd C:\Users\<nome_utente>\Documents
     ```

3. **Clonazione o download del progetto**
   - Se utilizzi Git:
     ```powershell
     git clone https://github.com/<tuo-account>/DirittoTributarioHelper.git
     cd DirittoTributarioHelper
     ```
   - In alternativa scarica l'archivio ZIP del progetto e decomprimilo, quindi spostati nella cartella estratta:
     ```powershell
     cd C:\Users\<nome_utente>\Downloads\DirittoTributarioHelper
     ```

4. **Creazione dell'ambiente virtuale**
   - Dal terminale di Visual Studio esegui:
     ```powershell
     py -3.11 -m venv .venv
     .\.venv\Scripts\activate
     ```
   - Il prompt mostrerà `(.venv)` a indicare che l'ambiente è attivo.

5. **Installazione delle dipendenze gratuite**
   - Con l'ambiente attivo, installa le librerie richieste:
     ```powershell
     pip install --upgrade pip
     pip install -r requirements.txt
     ```

6. **Avvio del portale**
   - Sempre dal terminale di Visual Studio lancia Streamlit:
     ```powershell
     streamlit run tributary_portal/streamlit_app.py
     ```
   - Al termine del caricamento, Streamlit aprirà automaticamente il browser di default su `http://localhost:8501`. Se non accade, copia manualmente l'indirizzo dal terminale al browser.

7. **Utilizzo dell'interfaccia**
   - Inserisci nel campo di testo l'argomento tributario (es. `ravvedimento operoso`).
   - Seleziona il numero di risultati che desideri per ogni categoria (1-10).
   - Esamina le tre schede (Articolo di riferimento, Spiegazione dell'argomento, Esempio pratico). Ogni risultato contiene titolo, sintesi e collegamento alla fonte originale.
   - Se vuoi una nuova ricerca, modifica l'argomento nel campo di testo.

8. **Arresto dell'applicazione**
   - Nel terminale premi `Ctrl+C` per interrompere Streamlit.
   - Disattiva l'ambiente virtuale con `deactivate` quando hai finito di lavorare.

## Risoluzione dei problemi più comuni

- **Il comando `streamlit` non viene riconosciuto**: assicurati che l'ambiente virtuale sia attivo (`(.venv)` nel prompt) e che l'installazione dei requisiti sia andata a buon fine.
- **La pagina non si apre automaticamente**: copia manualmente nel browser il link completo mostrato nel terminale (`http://localhost:8501`).
- **Nessun risultato o risultati scarsi**: prova a riformulare l'argomento con parole chiave diverse o più specifiche.

## Licenze

- Streamlit, duckduckgo_search, pandas e fpdf2 sono librerie open-source.
- Le ricerche sfruttano i risultati pubblici di DuckDuckGo; verifica sempre l'affidabilità delle fonti ottenute.
