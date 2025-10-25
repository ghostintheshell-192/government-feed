# Government Feed - Documento di Visione

**Versione**: 2.0
**Data**: 25 Ottobre 2025
**Stato**: Vision Consolidata

---

## 1. Panoramica del Progetto

**Government Feed** è un aggregatore intelligente di notizie istituzionali che democratizza l'accesso alle informazioni primarie governative, combinando un sistema configurabile con un marketplace condiviso di feed, alimentato da intelligenza artificiale locale e supportato da una community di curatori.

A differenza degli aggregatori generalisti, Government Feed si focalizza esclusivamente su **fonti primarie ufficiali** - comunicazioni dirette da banche centrali, ministeri, istituzioni pubbliche e organismi governativi - offrendo ai cittadini la possibilità di accedere alle informazioni **senza intermediazione mediatica** che potrebbe distorcerne il significato o l'importanza.

### Evoluzione del Concept

Il progetto è nato come aggregatore RSS specializzato ed è evoluto in un **ecosistema configurabile con feed registry condiviso**, dove:

- Gli utenti hanno pieno controllo sui feed che seguono
- Una community contribuisce curando e condividendo configurazioni
- Starter pack preconfezionati facilitano l'onboarding
- L'intelligenza artificiale locale riassume automaticamente i contenuti
- I costi rimangono sostenibili anche con crescita significativa

---

## 2. Analisi di Contesto

### Il Problema

Il progetto nasce per risolvere criticità reali nell'accesso alle informazioni istituzionali:

**1. Dispersione delle Fonti**
Le comunicazioni ufficiali sono distribuite su decine di siti web istituzionali. Per un cittadino monitorarle tutte richiede:
- Visitare regolarmente numerosi portali diversi
- Iscriversi a multiple newsletter (ricevendo grandi quantità di contenuti non rilevanti)
- Dedicare tempo significativo alla ricerca manuale

**2. Sovraccarico Informativo**
Le istituzioni pubblicano grandi volumi di informazioni quotidianamente. La maggior parte ha limitata rilevanza per il singolo cittadino, rendendo difficile individuare ciò che conta davvero.

**3. Complessità Tecnica e Linguistica**
Le comunicazioni istituzionali sono spesso redatte in linguaggio tecnico o burocratico, risultando difficilmente comprensibili senza contestualizzazione adeguata.

**4. Dipendenza dall'Intermediazione Mediatica**
I media tradizionali tendono a:
- Selezionare solo alcune notizie istituzionali, ignorando comunicazioni potenzialmente importanti
- Interpretare e riassumere secondo linee editoriali specifiche
- Ritardare la pubblicazione rispetto alla fonte primaria

Il cittadino che vuole mantenersi informato si trova costretto a **scegliere tra l'inefficienza della ricerca diretta e la parzialità dell'intermediazione giornalistica**.

### La Soluzione

Government Feed elimina questo trade-off fornendo:
- **Accesso diretto** alle fonti primarie
- **Centralizzazione** in un'unica interfaccia
- **Filtri intelligenti** per ridurre il rumore
- **Riassunti AI** per comprendere rapidamente il contenuto
- **Autonomia totale** nella scelta delle fonti da seguire

---

## 3. Filosofia di Design

### Principi Fondamentali

**1. Autonomia dell'Utente**
Il sistema è completamente configurabile. Nessun gatekeeping su quali fonti sono "importanti" o "rilevanti". L'utente decide cosa seguire.

**2. Community-Driven**
Le configurazioni di feed sono condivise dalla community, non imposte dal creatore. Il marketplace di feed cresce organicamente con i contributi degli utenti.

**3. Starter Pack per Facilità d'Uso**
Nonostante l'enfasi sulla configurabilità, il sistema fornisce **starter pack curati** per chi vuole iniziare immediatamente senza dover cercare manualmente ogni feed. Esempi:
- "Italia - Economia Base" (BCE, MEF, Banca d'Italia)
- "Europa - Politica Monetaria" (ECB, Commissione EU)
- "Locale - Regione Lombardia" (Regione, ARPA, ASL)

**4. Privacy-First**
I riassunti AI sono generati localmente. I dati dell'utente non escono dal sistema. Nessun tracking, nessuna profilazione.

**5. Semplicità nell'Interfaccia**
GUI chiara e lineare, senza tutorial invasivi o wizard obbligatori. Il sistema deve essere intuitivo per chi ha familiarità con feed reader o aggregatori di notizie.

---

## 4. Feed Registry - Il Cuore dell'Innovazione

### Concept

Un **marketplace condiviso di feed istituzionali** dove:

- Ogni utente può contribuire feed che conosce
- Altri possono trovare, importare e usare questi feed con un click
- La community valida qualità e attualità dei feed
- Starter pack curati facilitano l'onboarding

### Funzionalità Chiave

**Discovery (Scoperta)**
- Ricerca per keyword: "tassi interesse", "ambiente", "sanità"
- Filtri: geografia, categoria, lingua, tipo di istituzione
- Ordinamento: popolarità, aggiornamento recente, valutazione

**Contribution (Contribuzione)**
- Pulsante "Aggiungi Feed" accessibile a tutti
- Form semplice: URL, titolo, descrizione, tag, categoria
- Validazione automatica (feed funzionante)
- Submit → entra nel registry pubblico

**Social Features**
- Numero di follower per feed (quanti lo stanno usando)
- "Feed simili consigliati" basati su pattern d'uso
- Segnalazione "feed non funzionante" dalla community

**Import/Export**
- Export configurazione completa (JSON)
- Import con drag-and-drop
- Starter pack curati scaricabili direttamente

### Esempio: Schema Configurazione

```json
{
  "version": "1.0",
  "metadata": {
    "name": "Italia - Economia Base",
    "description": "Feed essenziali per monitorare economia italiana",
    "author": "community",
    "tags": ["economia", "italia", "finanza"],
    "created": "2025-10-25"
  },
  "feeds": [
    {
      "url": "https://www.bancaditalia.it/media/notizie/rss/",
      "source": "Banca d'Italia",
      "category": "monetary-policy",
      "language": "it",
      "description": "Comunicati e notizie ufficiali"
    },
    {
      "url": "https://www.mef.gov.it/rss/comunicati-stampa",
      "source": "Ministero Economia e Finanze",
      "category": "policy",
      "language": "it",
      "description": "Comunicati stampa MEF"
    }
  ]
}
```

### Implementazione Incrementale

Il feed registry evolverà progressivamente:

- **Phase 1**: Repository GitHub con file JSON, interfaccia statica
- **Phase 2**: Backend con API, database, interfaccia dinamica
- **Phase 3**: Account utente, rating system, trending, moderazione

---

## 5. Target di Utenza

### Utenti Primari: Cittadini Informati

Il target principale sono **cittadini normali** che:

- Vogliono informarsi direttamente dalle fonti ufficiali
- Sono stanchi dell'intermediazione mediatica
- Hanno interesse specifico in alcune aree (economia, sanità, ambiente, locale)
- Sono disposti a configurare un tool per ottenere informazioni di qualità

**NON** sono necessariamente professionisti dell'informazione (giornalisti, analisti, lobbisti), anche se questi potrebbero trovare il sistema utile.

### Early Adopters Attesi

Ci si aspetta che i primi utilizzatori siano:

- **Smanettoni** con alta literacy digitale
- Persone **molto interessate** a notizie di prima fonte
- Utenti disposti ad **applicarsi** per configurare il sistema secondo le proprie esigenze

La GUI è pensata per essere **semplice e lineare**, senza tutorial invasivi, perché questo profilo di utente preferisce esplorare autonomamente.

### Espansione Graduale

Con il tempo, grazie agli starter pack e alla semplificazione progressiva, il sistema potrebbe diventare accessibile anche a utenti meno tecnici.

---

## 6. Benefici Chiave

### 1. Disintermediazione Mediatica

**Accesso diretto alle fonti primarie** senza filtri editoriali:
- Le comunicazioni istituzionali arrivano senza interpretazioni
- Nessun ritardo rispetto alla pubblicazione ufficiale
- Possibilità di formarsi opinioni indipendenti

### 2. Centralizzazione e Risparmio di Tempo

- **Un'unica interfaccia** per decine di fonti istituzionali
- Eliminazione della necessità di visitare siti multipli
- Filtri intelligenti riducono il rumore informativo

### 3. Comprensione Facilitata

- **Riassunti AI automatici** per comprendere rapidamente il contenuto
- Contestualizzazione delle notizie tecniche in linguaggio più accessibile
- Collegamenti tra notizie correlate da fonti diverse

### 4. Autonomia e Personalizzazione

- Pieno controllo sui feed seguiti
- Configurazione basata su interessi personali
- Nessun algoritmo opaco che decide cosa è "importante"

### 5. Maggiore Consapevolezza Civica

- Accesso a informazioni che influenzano direttamente la vita quotidiana
- Possibilità di anticipare cambiamenti normativi o economici
- Maggiore trasparenza sui processi decisionali delle istituzioni

---

## 7. Sistema di Rilevanza e Filtro

### Approccio Incrementale

Il sistema di ranking evolve progressivamente per adattarsi alle preferenze dell'utente:

**Phase 1 - Euristica Base**
- Ranking per autorità della fonte (BCE > Ministero > Agenzia locale)
- Tipo di atto (Decreto > Comunicato > Verbale)
- Keyword critiche ("scadenza", "modifica fiscale", "bando", "allerta")
- Ricorrenza cross-fonte (3+ fonti parlano dello stesso tema → bump priorità)

**Phase 2 - Preferenze Utente (Collaborative Filtering Semplice)**

Il sistema apprende dalle interazioni dell'utente:

```python
user_preferences = {
    'sources': {'BCE': 0.8, 'Comune_Milano': 0.2},
    'keywords': {'tassi': 0.9, 'cultura': 0.1},
    'categories': {'economia': 0.95, 'sport': 0.05}
}
```

Meccanica:
- Click/lettura notizia → +1 score per quella fonte/categoria/keyword
- Nascondi/ignora → -1 score
- Ranking si adatta automaticamente nel tempo

**Phase 3 - Semantic Matching (Opzionale, Futuro)**
- Embedding semantici per trovare "notizie simili a quelle che hai letto"
- Raggruppamento automatico di temi correlati

### Controlli UI per l'Utente

L'interfaccia fornisce controlli diretti:
- Toggle: "Nascondi comunicati stampa generici"
- Filtri per keyword personalizzati
- "Segna come importante/ignorabile" → salva preferenze
- Reset preferenze se il sistema "impara" pattern sbagliati

---

## 8. Mercato Geografico

### Focus Primario: Italia ed Europa

La strategia di lancio si concentra su Italia ed Europa per motivi strategici:

**Vantaggi Competitivi**:
- **Minore competizione** rispetto al mercato USA (dove esistono player consolidati come GovExec, FedScoop, Quorum Analytics)
- **Struttura istituzionale EU più centralizzata**, che facilita l'aggregazione
- **Gap maggiore** nel mercato consumer europeo per questo tipo di strumento
- **Barriere linguistiche** proteggono da player anglofoni che dominano il mercato USA

**Opportunità Locali**:
- Forte interesse per comunicazioni EU (policy, direttive, regolamenti)
- Frammentazione nazionale (ogni paese ha le sue istituzioni) crea valore nell'aggregazione
- Civic tech community attiva in crescita

### Mercato USA: Non Prioritario

Il mercato USA è saturo di soluzioni professionali costose. Non è un focus iniziale, anche se il modello potrebbe essere replicato in futuro.

---

## 9. Aspetti Legali

### Riutilizzo di Contenuti Istituzionali

**In Italia e nell'Unione Europea:**

✅ **Legale e Incoraggiato**

- **CAD (Codice Amministrazione Digitale) Art. 52**: I dati pubblici sono riutilizzabili per default
- Comunicati ufficiali e documenti pubblici = pubblico dominio o licenza CC-BY
- I **feed RSS esistono esattamente per facilitare l'aggregazione**

**Requisiti da Rispettare:**

- ✅ **Attribuzione della fonte** (sempre citare l'istituzione originale)
- ✅ **Non modificare i contenuti** citati (riassunti AI ok, ma link a originale sempre presente)
- ✅ **Chiarire** che Government Feed è un aggregatore terzo, non un canale ufficiale
- ❌ **Non spacciare** il servizio per comunicazione ufficiale delle istituzioni

**Conclusione Legale:**

L'uso di feed RSS istituzionali per creare un aggregatore è il **caso d'uso previsto** dalle stesse istituzioni. Non ci sono ostacoli legali significativi.

---

## 10. Filosofia sul Successo

### Il Successo si Misura nell'Utilità, Non nei Numeri

Government Feed è progettato primariamente come **strumento di utilità personale**. Il successo del progetto non si misura in metriche quantitative (utenti attivi, revenue, market share), ma in:

- **Utilità quotidiana**: Il tool viene usato regolarmente per informarsi
- **Qualità dell'informazione**: Le fonti sono affidabili e rilevanti
- **Autonomia ottenuta**: L'utente ha maggiore controllo sul proprio flusso informativo
- **Impatto civico**: Maggiore consapevolezza dei processi istituzionali

Se il progetto serve bene anche solo una manciata di utenti appassionati - incluso il creatore stesso - è un successo.

**La community eventuale è un bonus, non l'obiettivo primario.**

---

## 11. Opportunità Future

Il progetto è pensato per evolvere in base all'uso reale. Alcune direzioni possibili:

### Espansione Funzionale
- **Notifiche push** per comunicazioni critiche (scadenze, allerte)
- **Analisi trend** cross-fonte (quali temi stanno emergendo)
- **Archivio storico** ricercabile di comunicazioni istituzionali

### Espansione Geografica
- Supporto per istituzioni di altri paesi europei
- Localizzazione in altre lingue (francese, tedesco, spagnolo)

### Integrazioni
- **API pubblica** per sviluppatori terzi
- **Esportazione dati** in formati standard (RSS, JSON, CSV)
- **Integrazione con tool di produttività** (Notion, Obsidian, Readwise)

### Community Features
- **Discussioni** su comunicazioni specifiche
- **Annotazioni condivise** e fact-checking collaborativo
- **Newsletter curate** dalla community su temi specifici

Queste opportunità saranno esplorate **solo se emergono organicamente** dall'uso reale del sistema.

---

## Conclusione

Government Feed risolve un problema reale: **l'accesso frammentato e mediato alle informazioni istituzionali ufficiali**.

Lo fa combinando:
- **Tecnologia moderna** (AI locale, feed aggregation)
- **Filosofia community-driven** (feed registry condiviso)
- **Facilità d'uso** (starter pack, GUI semplice)
- **Autonomia dell'utente** (piena configurabilità)

Il progetto è open source, sostenibile, e progettato per utilità personale prima che per scala commerciale.

**Build it, use it, share it.** Se risuona con altri, la community farà il resto.

---

*Versione: 2.0*
*Data: 25 Ottobre 2025*
*Stato: Vision Consolidata - Ready for Implementation*
