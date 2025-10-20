# DirittoTributarioHelper

Portale interattivo per supportare lo studio del diritto tributario. L'applicazione web, realizzata con Streamlit, integra strumenti di ricerca, pianificazione e ripasso per accompagnare l'utente lungo tutto il percorso di studio.

## Caratteristiche principali

- **Ricerche mirate**: tre schede tematiche (Articolo di riferimento, Spiegazione, Esempio pratico) alimentate da ricerche automatiche su DuckDuckGo con query ottimizzate.
- **Archivio appunti**: modulo integrato per creare, filtrare ed esportare gli appunti delle ricerche in formato Markdown, testo o PDF.
- **Piano di studio interattivo**: generatore di calendario che distribuisce gli argomenti nel tempo, con download del piano in CSV o ICS per l'importazione nel proprio calendario.
- **Quiz personalizzati**: questionari a scelta multipla caricati dal file `risorse/quiz_tributario.json`, con modalità di ripasso sugli errori e statistiche in tempo reale.
- **Dipendenze completamente gratuite**: Streamlit, duckduckgo_search, pandas e fpdf2 sono librerie open-source e facilmente installabili.

## Prerequisiti

Consulta `risorse/elementi_necessari.md` per un riepilogo di hardware e software consigliato. È sufficiente Python 3.10+ con accesso a Internet per effettuare le ricerche web.

## Installazione rapida

Le indicazioni si riferiscono a Windows 11 con Visual Studio 2022 Community, ma possono essere seguite anche con Visual Studio Code o qualsiasi terminale.

```powershell
# 1. Clona o scarica il progetto
git clone https://github.com/<tuo-account>/DirittoTributarioHelper.git
cd DirittoTributarioHelper

# 2. Crea e attiva un ambiente virtuale
py -3.11 -m venv .venv
.\.venv\Scripts\activate

# 3. Installa le dipendenze gratuite
pip install --upgrade pip
pip install -r requirements.txt

# 4. Avvia l'applicazione Streamlit
streamlit run tributary_portal/streamlit_app.py
```

Apri il browser su `http://localhost:8501` se non si apre automaticamente.

## Gestione dei contenuti didattici

Il portale utilizza alcuni file JSON modificabili per adattare l'esperienza alle tue esigenze:

- `risorse/programma_base.json`: elenco predefinito degli argomenti da ripartire nel piano di studio. Accetta una semplice lista di stringhe.
- `risorse/quiz_tributario.json`: database delle domande del quiz. Ogni domanda è un oggetto con campi `id`, `question`, `options`, `correct_answer`, `explanation` e un campo opzionale `topic` per filtrare gli argomenti.

Aggiorna i file con un editor di testo mantenendo la struttura JSON valida. Le modifiche vengono caricate automaticamente al successivo avvio dell'app.

## Funzionalità dell'interfaccia

1. **Ricerca** – inserisci un argomento (es. `ravvedimento operoso`) e scegli il numero di risultati da 1 a 10. Ogni scheda mostra titolo, sintesi e collegamento alla fonte originale, con pulsante rapido per copiare il contenuto.
2. **Appunti** – salva note legate alla ricerca, categorizzale e scarica gli appunti selezionati nei formati supportati. È disponibile una sintesi automatica degli appunti scelti.
3. **Piano di studio** – imposta data dell'esame, ore giornaliere e argomenti da coprire. Il piano risultante può essere scaricato come CSV o importato nel calendario tramite file ICS.
4. **Quiz** – esercitati sugli argomenti caricati. Il sistema memorizza gli errori per permettere sessioni di ripasso mirate.

## Struttura delle cartelle

```
DirittoTributarioHelper/
├── README.md
├── requirements.txt
├── risorse/
│   ├── elementi_necessari.md
│   ├── programma_base.json
│   └── quiz_tributario.json
└── tributary_portal/
    └── streamlit_app.py
```

## Risoluzione dei problemi comuni

- **`streamlit` non riconosciuto** – assicurati di aver attivato l'ambiente virtuale e di aver installato i requisiti.
- **Nessuna risposta dal motore di ricerca** – controlla la connessione Internet o riprova più tardi: DuckDuckGo potrebbe limitare temporaneamente le richieste automatizzate.
- **Errore sui file JSON** – verifica la correttezza della sintassi (virgolette doppie e virgole finali). In caso di dubbio, utilizza un validatore JSON online.

## Licenze e fonti

- Le librerie utilizzate (Streamlit, duckduckgo_search, pandas, fpdf2) sono distribuite con licenze open-source.
- Le informazioni provenienti da DuckDuckGo rimangono soggette alle condizioni d'uso dei rispettivi siti di origine: valida sempre le fonti prima di utilizzarle in ambito professionale o accademico.
