---
captured: 2026-07-03
status: parked
context: "chiusura M4a (feature/starter-packs) — i contatori erano nella spec starter-packs ma rimossi durante feature/geographic-sidebar"
tags: [ux, dashboard, geographic-sidebar, m4b]
---

# Contatori sulla sidebar geografica — UX da ripensare

**Cos'è**: i badge della sidebar geografica (Local/National/Continental/Global)
dovevano mostrare un contatore di articoli "nuovi" per livello. Una prima
implementazione è stata rimossa: i numeri grezzi confondevano più che aiutare
(ambiguità "nuovi" vs "totali", zero poco informativo).

**Perché merita**: il colpo d'occhio "dove è arrivato qualcosa di nuovo" è il
valore principale della sidebar. Il backend è pronto (`news_freshness_hours`
in settings); manca solo una presentazione che sia utile e non confusionaria.
Domande aperte ereditate dalla spec: nuovi vs totali? distinguere "0 nuovi ma
con fonti" da "nessuna fonte a questo livello"?

**Next-step minimo**: quando si progetta la sidebar M4b (filtri custom),
riprendere in mano le due domande e prototipare 2-3 varianti (dot indicator
senza numero, contatore solo se > 0, tooltip con dettaglio) da valutare a
schermo prima di implementare.

Spec di origine: `.development/specs/*/starter-packs.md` (Future Evolution M4b).
