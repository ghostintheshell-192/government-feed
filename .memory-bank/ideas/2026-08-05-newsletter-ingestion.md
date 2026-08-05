---
captured: 2026-08-05
status: parked
context: "brainstorming su testate giornalistiche nella dashboard — scorporata da press-coverage-cross-referencing.md, che nasce dalla stessa conversazione"
tags: [email, newsletter, ingestion, privacy, press-coverage, m4b]
---

# Ingestione newsletter via email — se e come farla entrare

**Cos'è**: collegare la dashboard alla posta per recuperare le newsletter e i
digest delle testate a cui Valentina è iscritta (The Conversation, The
Information, WSJ, Il Post, Axios), che oggi arrivano in quantità ingestibile.
Era l'idea di partenza; la conversazione l'ha ridimensionata.

**Perché è stata messa da parte (non scartata)**:

1. **Il grosso del valore non passa dall'email.** "Vedere titolo + sommario per
   decidere se leggere" si ottiene dagli RSS pubblici, che il progetto già sa
   consumare — nessun codice nuovo. Quel pezzo è diventato Phase 1 della spec
   `press-coverage-cross-referencing.md`.
2. **Le newsletter sono digest di digest.** Spacchettarne una in item duplica
   l'RSS e moltiplica il volume; non spacchettarla lascia un blob HTML
   illeggibile. Il parser va scritto per testata e si rompe a ogni restyle:
   costo di manutenzione permanente.
3. **Superficie privacy sproporzionata.** IMAP/OAuth sulla posta è il
   componente meno condivisibile e più fragile di un progetto che per il resto
   è pubblicabile così com'è.

**Perché merita comunque di restare**: le newsletter contengono un dato che
l'RSS non ha — **l'ordinamento esplicito di un redattore**. "Il WSJ oggi ha
messo questo pezzo in cima" è un voto editoriale, cioè un segnale di
prominenza. Usato per *ordinare* item già arrivati via RSS (non per generarne
di nuovi), il modulo si riduce da seconda pipeline di ingestione ad
arricchimento di metadati: superficie molto più piccola e molto più stabile.

Da verificare prima, però: quanto di quel segnale è già ricavabile dai feed
stessi (presenza nel feed homepage vs solo di sezione, numero di sezioni,
posizione). Se la risposta è "abbastanza", l'email non serve affatto.

**Next-step minimo**: non progettare nulla finché Phase 1 non è in uso da
qualche settimana. L'esperimento decisivo è: con le cinque testate nel
catalogo via RSS, **quanto rumore resta davvero?** Il residuo misurato — non
l'intuizione di adesso — dice se e cosa giustifica il modulo email.

Se poi si fa: **casella dedicata** (alias che riceve solo newsletter), mai
IMAP sulla posta personale. Coerente con ADR-002.

**Decisione ancora aperta**: se questa cosa entra nel progetto, e con quale
classificazione (spec propria? fase 3 di press-coverage? tech-spike?). Da
decidere quando ci sono i dati, non prima.

Spec di riferimento: `.development/specs/planned/press-coverage-cross-referencing.md`
(sezione "Deliberately out of scope").
