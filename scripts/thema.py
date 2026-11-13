#!/usr/bin/env python3
"""Alles Themenspezifische der taeglichen Studienauswahl — und sonst nichts.

Diese Datei ist die EINZIGE unter scripts/, die sich von Portal zu Portal
inhaltlich unterscheidet. `update_studies.py` bleibt in allen Portalen
wortgleich und importiert von hier. Wer die Auswahl aendern will, aendert
Text in dieser Datei — keinen Code.

Erzeugt von neues-portal.py aus dem Themenprofil `themen/genom.json`.
Weiterentwickelt wird danach hier, nicht im Profil.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------- Kennungen
# NCBI bittet bei automatisierten Zugriffen um eine Tool-Kennung.
NCBI_TOOL = "genom-portal"

# ----------------------------------------------------------- Die Suchabfrage
# Zwei Bloecke, die BEIDE zutreffen muessen. Ohne den zweiten spuelt die Abfrage
# Arbeiten herein, die das Thema nur streifen; ohne den ersten kommt beliebige
# Versorgungsliteratur.
#
# Zur Feldwahl: [MeSH Terms] fasst breit, [Majr] verlangt das Haupt-Schlagwort,
# [Title/Abstract] fasst am breitesten, [Title] am engsten. Faustregel aus den
# Schwesterportalen: Steht ein Begriff in fremden Abstracts als blosses Werkzeug
# oder Beiwerk, ist [Title/Abstract] untauglich — dann [Majr]/[Title]. Im
# KI-Portal sank die Trefferzahl dadurch von 605.000 auf 321.000, und erst die
# kleinere Menge handelte tatsaechlich vom Thema.
#
# Vor dem Livegang die Trefferzahl in PubMed nachsehen und hier notieren, damit
# spaetere Aenderungen messbar bleiben.
_THEMA = (
    '(("Genetic Testing"[Majr] OR "Genetic Counseling"[Majr] OR '
    '"Pharmacogenomic Testing"[Majr] OR "Pharmacogenetics"[Majr] OR '
    '"Neonatal Screening"[Majr] OR "Genetic Carrier Screening"[Majr] '
    'OR "Whole Genome Sequencing"[Majr] OR "Exome Sequencing"[Majr] OR '
    '"Precision Medicine"[Majr] OR "precision medicine"[Title] OR '
    '"genomic medicine"[Title] OR "genetic testing"[Title] OR "genomic '
    'sequencing"[Title]) OR ("Rare Diseases"[Majr] OR "Orphan Drug '
    'Production"[Majr] OR "rare disease*"[Title] OR "orphan '
    'drug*"[Title] OR "ultra-rare"[Title/Abstract] OR "undiagnosed '
    'disease*"[Title]) OR ("Molecular Diagnostic Techniques"[Majr] OR '
    '"Direct-To-Consumer Screening and Testing"[Majr] OR "Genetic '
    'Privacy"[Majr] OR "Biological Specimen Banks"[Majr] OR '
    '"Noninvasive Prenatal Testing"[Majr] OR ("Prenatal '
    'Diagnosis"[Majr] AND ("Genetic Testing"[MeSH] OR "Chromosome '
    'Aberrations"[MeSH] OR "Genetic Diseases, Inborn"[MeSH])) OR '
    '"Preimplantation Diagnosis"[Majr] OR "Gene Therapy"[Majr] OR '
    '"Genetic Therapy"[Majr] OR "pharmacogenomic*"[Title] OR "genetic '
    'counsel*"[Title] OR "newborn screening"[Title])) NOT ("Artificial '
    'Intelligence"[Majr] OR "Machine Learning"[Majr] OR "Deep '
    'Learning"[Majr] OR "Telemedicine"[Majr] OR "Medical '
    'Informatics"[Majr] OR "Nursing"[Majr] OR "Nursing Care"[Majr] OR '
    '"Long-Term Care"[Majr] OR "Nursing Homes"[Majr] OR "Aging"[Majr] '
    'OR "Longevity"[Majr] OR "Frailty"[Majr] OR "Geriatrics"[Majr] OR '
    '"Health Literacy"[Majr] OR "Patient Education as Topic"[Majr] OR '
    '"Climate Change"[Majr] OR "Air Pollution"[Majr] OR '
    '"Vaccination"[Majr] OR "Vaccines"[Majr] OR "Multimorbidity"[Majr] '
    'OR "Patient Safety"[Majr] OR "Medical Errors"[Majr] OR "Cross '
    'Infection"[Majr] OR "Mental Health Services"[Majr] OR "Mental '
    'Disorders"[Majr:noexp] OR "Obesity"[Majr] OR "Bariatric '
    'Surgery"[Majr] OR "Diabetes Mellitus"[Majr] OR "Eye '
    'Diseases"[Majr] OR "Ophthalmology"[Majr] OR "Musculoskeletal '
    'Diseases"[Majr:noexp] OR "Osteoarthritis"[Majr] OR "Arthritis, '
    'Rheumatoid"[Majr] OR "Osteoporosis"[Majr] OR "Back Pain"[Majr])'
)
_KONTEXT = (
    '(hasabstract NOT (Comment[Publication Type] OR '
    'Editorial[Publication Type] OR Letter[Publication Type] OR '
    'News[Publication Type] OR "Published Erratum"[Publication Type] '
    'OR "Retraction of Publication"[Publication Type] OR "Case '
    'Reports"[Publication Type]))'
)
# OHNE "Humans"[MeSH]: Dieses Portal zeigt bewusst auch Grundlagenforschung.
# Tier- und Laborarbeiten kommen damit in den Pool - der Prompt muss sie ordnen.
# Zweiter Grund, den Filter hier wegzulassen: Frisch in PubMed aufgenommene
# Datensaetze sind noch nicht verschlagwortet. In der Woche vom 29.08.2026 trugen
# nur 37 bis 40 Prozent der neuen Datensaetze ueberhaupt "Humans"[MeSH] - ueber
# das ganze Jahr sind es 56 bis 67. Der Filter siebt also auch nach
# Bearbeitungsstand der NLM, nicht nur nach Inhalt.
TERM = os.environ.get(
    "SEARCH_TERM",
    f'(({_THEMA} AND {_KONTEXT}))',
)
# Zweite Abfrage, damit Arbeiten mit Deutschland- und Europabezug den
# Kandidatenpool sicher erreichen. Ueber MeSH und Autorenadresse, nicht ueber
# Journalnamen - deutschsprachige Journale liefern kaum Treffer.
TERM_DE = os.environ.get(
    "SEARCH_TERM_DE",
    f"{TERM} AND (Germany[MeSH Terms] OR Germany[Affiliation] "
    "OR Europe[MeSH Terms] OR Europe[Affiliation])",
)

# Groesse des Kandidatenpools. Europa steht vorn und stellt die Mehrheit -
# ein Sprachmodell gewichtet, was es zuerst liest. Wer das umdreht, bekommt
# eine Auswahl ohne Bezug zu hiesigen Verhaeltnissen; im Klima-Portal ist
# genau das passiert.
POOL_EUROPA = 12
POOL_ALLGEMEIN = 43
# Welche Abfrage vorn steht. True ist der Regelfall und die Lehre aus dem
# Klima-Portal: Steht die allgemeine Abfrage vorn, kommt eine Auswahl ohne
# Bezug zu hiesigen Verhaeltnissen heraus. Das Versorgungsforschungs-Portal
# arbeitet historisch andersherum (40 allgemein + 15 deutsch) - dort steht
# hier False, damit der Anschluss an die Vorlage nichts an seiner taeglichen
# Auswahl geaendert hat. Umstellen ist eine redaktionelle Entscheidung.
EUROPA_ZUERST = True

# Wie viele Studien taeglich erscheinen. SOLL wird im Prompt verlangt und beim
# Kappen verwendet; ueber MAX wird gekappt, unter MIN bricht der Lauf ab.
# **Nicht ins JSON-Schema schreiben** - die Anthropic-API lehnt minItems > 1
# und maxItems ab (am 17.08.2026 zweimal mit HTTP 400 belegt).
ANZAHL_SOLL = 6
ANZAHL_MAX = 7
ANZAHL_MIN = 1
# True: zu viele Studien werden auf ANZAHL_SOLL gekuerzt (die Auswahl ist nach
# Relevanz geordnet, die vorderen sind brauchbar). False: zu viele lassen den
# Lauf scheitern - so hielt es das Versorgungsforschungs-Portal von Anfang an.
KAPPEN = True

# ------------------------------------------------------------------- Prompts
SYSTEM = (
    "Du bist Fachredakteur fuer Genommedizin und Seltene Erkrankungen. "
    "Aus einer Liste von PubMed-Abstracts waehlst du die relevantesten "
    "aktuellen Studien aus und fasst sie praezise auf Deutsch zusammen. "
    "Deine Leserschaft arbeitet im deutschen Gesundheitswesen: "
    "humangenetische Praxen und Institute, Zentren fuer Seltene "
    "Erkrankungen, Labore, Kostentraeger, Selbstverwaltung, "
    "Patientenorganisationen und Gesundheitspolitik. "
    "Sie erwartet beides - was die Diagnostik heute kann und was davon "
    "bei den Betroffenen ankommt und wer es bezahlt."
)

USER_TEMPLATE = """Unten stehen aktuelle PubMed-Abstracts (nach Datum sortiert).

Waehle GENAU 6 Studien aus, die (a) Genetische Diagnostik, Beratung, personalisierte Therapie, Gentherapie oder die Versorgung bei Seltenen Erkrankungen betreffen - oder die Grundlagen, auf denen sie beruhen UND (b) im
Abstract ein BENENNBARES ERGEBNIS berichten. Bei quantitativen Arbeiten heisst
das: konkrete Zahlen (Prozentwerte, Effektstaerken, Odds/Hazard Ratios, Zeit-
oder Kostenwirkungen, Fallzahlen, p-Werte) - und die gehoeren dann auch in die
Zusammenfassung. Qualitative Studien (Interviews, Fokusgruppen) und
Expertenpapiere sind ausdruecklich zugelassen; bei ihnen tritt an die Stelle
der Zahl die klar benannte Kernaussage - welche Faktoren, welche Bedingungen,
welche Empfehlung. Was NICHT genuegt, ist ein Abstract, der nur ankuendigt,
was untersucht wurde, ohne zu sagen, was dabei herauskam.
Ueberspringe Studien ohne Abstract oder ohne benennbares Ergebnis. Achte auf
thematische Vielfalt und mische quantitative und qualitative Arbeiten.

THEMATISCHE RANGFOLGE - in dieser Reihenfolge bevorzugen:
  1. Praxisveraendernde Evidenz: randomisierte Studien, Metaanalysen,
     Leitlinien, Nutzenbewertungen, Registerauswertungen mit grosser
     Fallzahl, und Arbeiten zum diagnostischen Ertrag eines Verfahrens.
  2. Harte Endpunkte: Sterblichkeit, Krankheitsverlauf, vermiedene
     Fehlbehandlung, Dauer bis zur Diagnose, Lebensqualitaet. Die Zeit
     bis zur Diagnose ist bei Seltenen Erkrankungen der Endpunkt, an dem
     sich Versorgung messen laesst - im Schnitt vergehen Jahre.
  3. Versorgung und Zugang: Erreichbarkeit der Diagnostik, Zuweisungswege,
     Erstattung, Zentrumsstruktur, Beratungskapazitaet, und die Kosten -
     Gentherapien stellen die teuersten Arzneimittel der Welt.
  4. Grundlagenforschung mit erkennbarem Weg in die Klinik: ein neu
     beschriebenes Krankheitsgen, eine Zielstruktur, ein Biomarker -
     wenn die Arbeit selbst sagt, wohin es fuehrt.

NICHT in die Auswahl gehoeren:
Reine Tiermodelle und Zellversuche ohne erkennbaren Bezug zum Menschen (die Genetik publiziert davon besonders viel), Arbeiten zur Pflanzen- und Tierzuechtung, bioinformatische Methodenarbeiten ohne klinische Fragestellung, reine Sequenzbeschreibungen, Phase-I-Studien, Fallberichte und Fallserien unter zehn Behandelten - mit EINER Ausnahme: Bei einer Erkrankung, von der weltweit nur wenige Faelle bekannt sind, IST die Fallserie die Evidenz. Sage dann dazu, wie viele Faelle beschrieben sind. Ausserdem bibliometrische Arbeiten, Editorials und Kommentare.

HARTE REGELN ZUR ZUSAMMENSETZUNG (sie gehen der thematischen Rangfolge vor):
  1. MINDESTENS 2 der sechs Studien muessen aus Europa stammen oder
     ein europaeisches Gesundheitssystem betreffen. Der Europa-Anteil
     liegt hier bei 12 Prozent.
  2. HOECHSTENS ZWEI der sechs duerfen reine Grundlagenarbeiten sein
     (Zellsystem, Tiermodell, molekularer Mechanismus, Sequenzanalyse).
  3. KEINE darf einen Impfstoff im Mittelpunkt haben, auch keinen mit
     viralem Vektor oder mRNA. Impfstoffe gehoeren nach impfen.m-vf.de.
     Das ist die heikelste Abgrenzung dieses Hubs: Ein viraler Vektor
     ist dieselbe Technik, einmal zur Immunisierung und einmal zum
     Gentransfer, und PubMed kennt den Unterschied nicht. Gemessen am
     13.11.2026 ueberschneidet sich die Gentherapie allein zu 29,2
     Prozent mit dem Impfen-Hub. Pruefe deshalb bei jeder Arbeit zu
     Vektoren, wozu der Vektor dient: Wird ein fehlendes Gen ersetzt,
     gehoert sie hierher. Wird eine Immunantwort erzeugt, nicht.
     Eine CAR-T-Zelltherapie ist Gentransfer und gehoert hierher,
     auch wenn sie das Immunsystem benutzt.
  4. HOECHSTENS EINE darf eine zielgerichtete Krebstherapie im
     Mittelpunkt haben. Die Praezisionsonkologie gehoert fachlich in
     beide Portale, ihr Schwerpunkt liegt aber bei onkologie.m-vf.de.
     Steht das genetische Verfahren im Mittelpunkt, gehoert die Arbeit
     hierher; steht die Tumortherapie im Mittelpunkt, dorthin.
  5. HOECHSTENS EINE darf eine digitale Anwendung oder ein Verfahren des
     maschinellen Lernens im Mittelpunkt haben. Sie gehoeren nach
     ki.m-vf.de. Die Variantenvorhersage ist dort eines der groessten
     Anwendungsgebiete - ohne diese Quote bestuende die Ausgabe aus
     Algorithmen.
  6. HOECHSTENS ZWEI der sechs duerfen ausschliesslich die Entdeckung
     einer Variante oder eines Gens berichten, ohne eine Folge fuer
     Diagnostik, Behandlung oder Beratung. Dass ein Gen gefunden wurde,
     ist noch keine Nachricht fuer die Versorgung.

ZWEITES AUSWAHLKRITERIUM - Übertragbarkeit auf Deutschland:
Bei sonst gleicher Qualität hat die übertragbare Studie IMMER Vorrang vor der
aktuelleren.

  Hoch:    Deutschland und deutschsprachiger Raum, vergleichbare Sozial-
           versicherungssysteme.
  Mittel:  Übriges Europa, Kanada, Australien - andere Ausgangslage,
           ähnlicher Versorgungsauftrag.
  Gering:  USA und Länder mit grundlegend anderer Finanzierung oder
           Ressourcenlage. Nur nehmen, wenn die Fragestellung davon
           unabhängig ist.

Besonderheit dieses Themenfeldes: Zwischen Studienlage und Versorgung steht in Deutschland vor allem das Gendiagnostikgesetz und die Frage, wer die Diagnostik bezahlt. Genomsequenzierung ist hierzulande keine Regelleistung, sondern laeuft seit 2024 im Modellvorhaben nach Paragraf 64e SGB V - waehrend der britische NHS sie ueber den Genomic Medicine Service seit Jahren regulaer anbietet. Studien zum diagnostischen Ertrag aus Grossbritannien, Australien oder den Niederlanden sind deshalb nur eingeschraenkt uebertragbar, und das gehoert gesagt. Dazu kommt die Beratungspflicht: In Deutschland darf eine praediktive Untersuchung nur nach genetischer Beratung erfolgen, was Kapazitaet bindet und die Wartezeiten erklaert. Bei Seltenen Erkrankungen ist die Zentrumsstruktur entscheidend - 36 Zentren fuer Seltene Erkrankungen, aber kein einheitlicher Zuweisungsweg. Nenne bei internationalen Arbeiten das Gesundheitssystem, in dem sie entstanden sind, und bei Kostenangaben die Waehrung und das Jahr.

Fuer jede Studie:
- journal: Journalname genau so, wie er in der Kopfzeile des Abstracts steht -
  Abkuerzung nicht aufloesen, nichts ergaenzen. (Wird ohnehin durch die Angabe
  aus PubMed ersetzt; rate hier nichts.)
- year: Erscheinungsjahr, z. B. "2026"
- pmid: die PubMed-ID
- title: praegnanter deutscher Titel, **hoechstens 160 Zeichen**. Der
  Torwaechter lehnt alles ueber 200 Zeichen ab und stoppt damit die ganze
  Ausgabe - Methode und Population gehoeren nicht in den Titel, sie stehen
  in sum und transfer.
  **Er MUSS das Ergebnis nennen, nicht nur das Verfahren.** Nicht
  „Exomsequenzierung bei Entwicklungsstoerungen untersucht", sondern
  was dabei herauskam: wie viele Diagnosen, wie viel frueher, mit
  welcher Folge fuer die Behandlung. Wo eine Arbeit Kosten berichtet,
  gehoeren sie in den Titel - bei Gentherapien ist der Preis die
  Nachricht.
- sum: 1 Satz auf Deutsch, was die Studie untersucht hat. Wenn der genannte
  Anlassfall nur das Material ist, an dem gerechnet wurde, sage das
  ausdruecklich - sonst haelt die Leserschaft ihn fuer den Gegenstand.
- result: Deutsch, die konkreten Zahlen/Befunde + ein kurzer Einordnungssatz.
  Deutsches Zahlenformat mit Komma (z. B. 0,63). **Der Einordnungssatz darf
  nicht behaupten, was die Autoren selbst ablehnen.** Wo ein Abstract eine
  Deutung ausdruecklich zurueckweist, diese Einschraenkung uebernehmen statt
  sie zu ueberschreiben. Ein Rechercheportal referiert, es wertet nicht auf.
- transfer: EIN Halbsatz (höchstens 12 Wörter), warum das Ergebnis für Deutschland
  taugt - oder wo die Grenze liegt. Nenne Land bzw. System und Datengrundlage.
  Keine ganzen Sätze, keine Wiederholung des Titels.
  Gut:      "Deutsche Klinikdaten, vergleichbare Dokumentationspflichten"
            "Niederlande, vergleichbares Versicherungssystem"
            "USA - nur der Sicherheitsbefund ist übertragbar"
  Schlecht: "Diese Studie ist gut übertragbar." (sagt nichts)

WICHTIG - Fachterminologie: Etablierte englische Fachbegriffe NICHT eindeutschen.
Sie sind auch im deutschen Fachdeutsch stehende Begriffe; eine woertliche
Uebersetzung wirkt unprofessionell und erschwert das Wiederfinden.
Englisch bleiben: Exom, Panel, Outcome, Baseline, Setting, Follow-up, Screening, Variant of Uncertain Significance, Real-World-Evidenz, CAR-T, CRISPR. Deutsch: Erbgutuntersuchung, Anlagetraeger, Erbgang, Zufallsbefund, Genschere, Waisenarzneimittel, Neugeborenenscreening, Praenataldiagnostik. Uebersetze alles, wofuer es einen eingefuehrten deutschen Ausdruck gibt.
Faustregel: Wuerde eine deutsche Fachzeitschrift wie Monitor Versorgungsforschung
den Begriff englisch stehen lassen, dann tue es auch. Im Zweifel englisch
belassen und bei Bedarf eine kurze deutsche Erlaeuterung in Klammern ergaenzen.

Gib ausschliesslich das geforderte JSON zurueck.

=== ABSTRACTS ===
{abstracts}
"""

# ------------------------------------------------- Newsfeed
# Wonach dieser Hub im MVF-Archiv sucht (scripts/newsfeed.py). Deutsche,
# versorgungsnahe Begriffe - das Archiv ist deutsch, englische Begriffe
# treffen dort hoechstens zufaellig.
#
# Warum eine eigene Liste und nicht die Schnellwahlbegriffe der Seite: Chips
# sind fuer Datenbankabfragen gemacht. Am 29.08.2026 im Gender-Hub gemessen -
# dort stehen "Herzinfarkt" und "Arzneimittelsicherheit" als Chips, weil deren
# geschlechtsspezifische Seite das Thema ist; im Archiv holten dieselben
# Woerter allgemeine Herz- und Arzneimittelmeldungen. Fehlt NEWS_SUCHE, faellt
# newsfeed.py auf die Chips zurueck - das geht, ist aber die schlechtere Wahl.
#
# Neue Begriffe VOR dem Eintragen messen:
#     py scripts/newsfeed.py --probe
NEWS_SUCHE = [
    "Genommedizin",
    "Genomsequenzierung",
    "Seltene Erkrankungen",
    "Humangenetik",
    "Gentherapie",
    "Orphan Drug",
    "Neugeborenenscreening",
    "Pharmakogenetik",
    "Gendiagnostik",
]

# Der Ausschreibungsradar steht NICHT mehr hier. Er laeuft seit dem 28.08.2026
# einmal zentral im Versorgungsforschungs-Portal; die zwoelf Themengebiete,
# ihre Auswahlregeln und Suchbegriffe stehen dort in scripts/radar_themen.py.
# Dieser Hub holt sich mit scripts/radar_hinweis.py nur die Zahl seines
# Gebiets.
