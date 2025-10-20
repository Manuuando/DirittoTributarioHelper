# DirittoTributarioHelper

Portale interattivo per supportare lo studio del diritto tributario. L'applicazione web, realizzata con Streamlit, integra strumenti di ricerca, pianificazione e ripasso per accompagnare l'utente lungo tutto il percorso di studio.

## Caratteristiche principali

- **Ricerche mirate**: tre schede tematiche (Articolo di riferimento, Spiegazione, Esempio pratico) alimentate da ricerche automatiche su DuckDuckGo con query ottimizzate.
- **Archivio appunti**: modulo integrato per creare, filtrare ed esportare gli appunti delle ricerche in formato Markdown, testo o PDF.
- **Piano di studio interattivo**: generatore di calendario che distribuisce gli argomenti nel tempo, con download del piano in CSV o ICS per l'importazione nel proprio calendario.
- **Quiz personalizzati**: questionari a scelta multipla caricati dal file `risorse/quiz_tributario.json`, con modalità di ripasso sugli errori e statistiche in tempo reale.
- **Dipendenze completamente gratuite**: Streamlit, duckduckgo_search, pandas e fpdf2 sono librerie open-source e facilmente installabili.

## Prerequisiti

- **Sistema operativo**: Windows 11 (qualsiasi edizione).
- **Python**: versione 3.10 o successiva. Le istruzioni qui riportate sono testate con Python 3.11.
- **Visual Studio 2022 Community**: installa il carico di lavoro "Sviluppo desktop con Python" per avere `Python`, `pip`, `venv` e il terminale "Developer PowerShell" già configurati.
- **Git**: installato automaticamente con Visual Studio o scaricabile da [git-scm.com](https://git-scm.com/download/win).
- **Connessione Internet**: necessaria per eseguire le ricerche su DuckDuckGo e per installare le dipendenze.

Consulta `risorse/elementi_necessari.md` per un riepilogo di hardware e software consigliato.

## Guida passo-passo per Windows 11 con Visual Studio 2022

### 1. Preparazione dell'ambiente

1. Avvia **Visual Studio 2022**.
2. Nella schermata iniziale, apri il menu a ingranaggio ➜ **Strumenti** ➜ **Get Tools and Features** per assicurarti che il carico di lavoro _Sviluppo desktop con Python_ sia selezionato. Riavvia Visual Studio al termine dell'installazione.
3. Verifica la presenza di Python aprendo **Strumenti ➜ Gestione pacchetti Python ➜ Ambienti**. Dovresti vedere un interprete Python 3.11.

### 2. Clonare il repository con l'interfaccia di Visual Studio

1. Dalla schermata iniziale seleziona **Clona un repository**.
2. Inserisci l'URL `https://github.com/<tuo-account>/DirittoTributarioHelper.git` nel campo _Repository location_.
3. Scegli una cartella di destinazione locale (es. `C:\Users\<Nome>\source\repos\`).
4. Fai clic su **Clona**. Visual Studio scaricherà il progetto e lo aprirà automaticamente.

> 💡 In alternativa puoi scaricare il progetto come ZIP da GitHub e decomprimerlo, quindi aprirlo in Visual Studio con **File ➜ Apri ➜ Cartella...**.

### 3. Configurare l'ambiente virtuale

1. Dal menu principale scegli **Visualizza ➜ Altro Windows ➜ Developer PowerShell** per aprire il terminale integrato.
2. Assicurati di trovarti nella cartella del progetto appena clonata, ad esempio:

   ```powershell
   cd C:\Users\<Nome>\source\repos\DirittoTributarioHelper
   ```

3. Crea l'ambiente virtuale `.venv` con Python 3.11:

   ```powershell
   py -3.11 -m venv .venv
   ```

4. Attiva l'ambiente virtuale:

   ```powershell
   .\.venv\Scripts\activate
   ```

   Il prompt mostrerà il prefisso `(.venv)` a conferma dell'attivazione.

### 4. Installare le dipendenze del progetto

1. Aggiorna `pip` per evitare avvisi di compatibilità:

   ```powershell
   python -m pip install --upgrade pip
   ```

2. Installa i pacchetti necessari a DirittoTributarioHelper:

   ```powershell
   pip install -r requirements.txt
   ```

3. Al termine dell'installazione verifica la lista dei pacchetti con `pip list` se vuoi controllare le versioni installate.

### 5. Avviare l'applicazione Streamlit

1. Sempre dal terminale `Developer PowerShell`, con l'ambiente virtuale attivo, esegui:

   ```powershell
   streamlit run tributary_portal/streamlit_app.py
   ```

2. Visual Studio mostrerà nel terminale l'URL locale, tipicamente `http://localhost:8501`. Il browser predefinito dovrebbe aprirsi automaticamente; in caso contrario copialo e incollalo manualmente nella barra degli indirizzi.

3. Mantieni aperto il terminale mentre lavori: chiuderlo interromperà il server Streamlit.

### 6. Personalizzare i dati didattici

1. In **Esplora Soluzioni**, espandi la cartella `risorse/`.
2. Fai doppio clic su `programma_base.json` per modificare l'elenco degli argomenti del piano di studio (una voce per riga, tra virgolette).
3. Modifica `quiz_tributario.json` per aggiungere o aggiornare le domande del quiz. Ogni voce deve rispettare la struttura: `id`, `question`, `options` (lista), `correct_answer`, `explanation`, `topic` (facoltativo).
4. Salva i file: Streamlit ricaricherà automaticamente i contenuti al successivo avvio.

### 7. Gestione quotidiana del progetto

- Per avviare nuovamente il portale: apri Visual Studio, riattiva l'ambiente (`.\.venv\Scripts\activate`) e rilancia `streamlit run ...`.
- Per aggiornare le dipendenze: `pip install --upgrade -r requirements.txt`.
- Per interrompere l'app: premi `Ctrl+C` nel terminale oppure chiudi il processo `streamlit` dal Task Manager.
- Per sincronizzare eventuali modifiche con GitHub usa **Git ➜ Commit or Stash...** dentro Visual Studio, quindi **Push**.

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
