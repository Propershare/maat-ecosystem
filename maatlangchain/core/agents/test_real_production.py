"""
PRODUCTION-READY TESTING with REAL OCR Results
Tests quality validation against actual extracted text from real images
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.chains.quality_validator import QualityValidator, ValidationStatus

# REAL extracted text from the 5 graphs we just processed
REAL_OCR_RESULTS = [
    {
        "name": "Graph 1: graph1.png",
        "extracted_text": """RFEAM
#A#+x
XtebtatUtRZ
#6f4
#+2R6E8t-
#1e+F#20a"
FRR,a)
#mejn0]
t03J_>iA
AR
#ERATA
p#z8J
A2
EEXBJAF
Aait#i
BJFTR Ezh
ET4
ARA#AJBR-
TQEAPIA
IsAjr#8i
TQE,
Atiebesmofataz
82
Mam
671*4013*71
4np964
102S6FFj###MJEA#ZJI
3w28805-
F#afig
13
##
3m28805_@4tf44
AJaizzWM]AIA
(#RYAtiz)
RA##AJ 5t01-714
5S14
#FXATiAS#E'AFA
##9jib]@E'AF1A21AE2B
#+F
tptib]
BJAwAzB
21Azi0,+2)
82##8Ja
^B
S#T
E
#a4MJRWAWTR
Evt6i#MF (#RzAj
98R1REA3-E+#F
i2)
4,8514
DZXAZMRIETRMWTT
#F
#FFJKer-AMEHEY#
Eztt
si23mAjr##aJ1R >t*1->
ABF#EX#+E
M1a#
HE3#2at01712
4FAB
2+053ER,
##Aaiti
6Y
83-263710JF18
Ew
EAR)
##TJAF
4et0JLYE#E
#r28tMt46R2
40
482
#+UJE?
#W8A
IaemMIETBJFIA,
6*
A348
AR4A2EAw
0Jitu>ia
CAJHEA %J-
Ftajm#
0Rz*R
# A l]uiti
'etXyE#F
#mRat
REZ
#MJF
1a
370426371P@FmTE
W4IL0a#
Etths), 5me}}
RMfi
RMMEEBT-#SRTRH
270132
C#FMe#TIII 
S#828#0-1438, #
5#62
BzP]
PA@gI
YiLt#mEjua
THTIIR
I+RA#e6j#
TQEAJI_
E#1
@#FFtI
#RW*#6atwajqi
13428+01154918
###E+BAE, 55ROJkla_
ERaj#0jztwiayIA-
#t#
ErEtx,
V1T ,
pl{l  -
YiLtEm
'XIB
#iek'
141A243+8j5
f#Mjm
'XIZASFTHRAJIEYEM;
#2, #713IS,
RTESFA
1423+04#J16
#BARWRiBRRZT,
4247
T1++EA#z
Mb2hntftbjissRY)
194
F#AR#TBRZETII
R@EQETRM
t#m-=R
ETA
Aiz78MAIS
13+2*ER64AM4#+6J
#b2arnJ#8J_T+at#,
IAr
Jji#gz
#8MF#
AEB
J7219101/52,
RSATERFEA+IMeut
4LjI##F
0M)'MBT'
19M6
# IAIR91144kiav#
ZW'EIT'
PA@RS
5R12
RIFZRAR'
#I
Iat34/6#7
#FAR'
#IFR _
#EtR ltlbzkhi L#F-
fkzk
A#AR#TE
[*+
84
8Y
IAT
IA#ERFEA+i-
RFEA+E
J2169018,2
F=bF2m4*4R#/1
RZBSF
12#
BA24TpEWm"88
Bjajzd
EA+i
EA+i2tAT-
EAm
#TF(Jtt
1MZEAwEMAKEY
tert
#RZEAMEIJLAIRSEfis
00J*L+]
#FEEATEI)l@rRati
EAT=
EEJLt
EBw_ZABBMAIA
R8B
FTIRU T+#
FT16
eS1z0,320j/#6
2F42Sm,a8j#8
#F4
02+25144,5210J0+2
Aw_eSm8]AI
Sle
Fsm SaEJ1R-
#A
##R2328tE802
##Z
'IeWeER0w Snhbjl#tan
4e,0e
#*42rziteiz
##L
EM2SM0,41J##R
EX
#(7itt
#(ibttzist81_
16
I6282341jteiZ
I/2x
2342S1w0,53811#2
I7492328j1812
I7#%
#tixmzazitlz
#6i)
MARAMI[Az=zijtlzg
#ARA IPA""",
        "ocr_confidence": {
            "avg_confidence": 0.1657,
            "min_confidence": 0.0041,
            "confidence_scores": [0.7286, 0.1464, 0.0147, 0.1262, 0.1762]  # Sample
        }
    },
    {
        "name": "Graph 2: graph2.png",
        "extracted_text": """G8*
705
303S4642+2"F45280/770
303S41421XFY 2317ITEtkT#_E
A84
AB0H ReRRtEtkTF_
tkT}
WktFZZiMRtaTit
1k74S(7w#at lbjxkthae
Fi}
(7z0
(#i#Miz) 2324646013
2E+6483771*74 (tEFM
(Juzzhkij__##
AR2380-T4
m#eZii]--Tp
#EXz=ii--T#
4J2780-#0
8++2
13)
KWE+Miz)
2ETE
(Jic
#R
#etr
EX
4h""",
        "ocr_confidence": {
            "avg_confidence": 0.1479,
            "min_confidence": 0.0028,
            "confidence_scores": [0.1513, 0.2394, 0.0300, 0.0028, 0.1143]
        }
    },
    {
        "name": "Graph 3: graph3.png",
        "extracted_text": """neo4j$ match
(n)
return
(n)
80
Node properties
1#5
Graph
ENTITY5079b4b8_1704_42b4_abdc_62e177b2f4cf
Me.
Table
EJ2
0704
ENTITYdc931789_3dc0 4559 85ad_32e168a91d23
<elementld>
4.b47fcbd5-2755-4b3a-bac5-
Text
pa}
08aebdbd5324.0
Katk
<id>
attributes
[HiktapAhxPA'J=IA
Code
a31e4
(SSSB)
Kamaaie,3#px
{94#
FAJREEHJZIMI##FFIARE,
RTxAMAAZE (#r) ,
Jp
Attze#E,xxWWREHXFA
Rat_
#ajtitBAR#tAxatlfhj
68b,4+2HNAIAJIK , LRFQ
'Jzeb,Etx'JMP/2007
'Mja
871Z
R50n"E*Z8T134EAJ%
+A@TS,AEFAYE #kik
441p18#
KMB
Show all]
chunks
[eee2e263-057f-4560-9475-
Nutn
30-1-7700n1
okc^737
Jc0c""",
        "ocr_confidence": {
            "avg_confidence": 0.4834,
            "min_confidence": 0.0104,
            "confidence_scores": [0.8815, 0.9998, 1.0000, 0.9999, 0.8801]
        }
    },
    {
        "name": "Graph 4: Evolution_Slavery.jpg",
        "extracted_text": """The-Process-and-Historical-Evolution-of-the-Enslavemenk-of-Africans _ From-Arab-to-European-Systems
Phase- /-Period.
Date-
Key-Actors-/-Invadersc
Main-Events-&-Processestt
Centers;, Routes-& -Mechanisms-of
Cultural; Political;-and-Demographic:
Ranger
Enslavementt
Consequencesn
African-Kmt-(Egypt)-functioned as-a
Icomplex; moral; and-scientific society
IState-labor-for-irrigation;
~Pre-Invasion-Africa
Before-656
lIndigenous:Africans-
lwithout-chattel-slavery
Labor-was-
lagriculture; pyramid-building
all-|Balanced-social-organization;-unity-of-religion;-
(Kmt-Civilization)a
BCEd
((Kmt
 Nile-Valley:
organized-through-communal; state;"
lwithin-kinship-based-citizenship-
science; and-governance;-no-enslavement
Civilizations)a
institution &
land-temple-service
not-ownership-ofilsystems&
humans &
Assyrians-
Persians-
Continuous-waves-of-foreign-conquest:
Armies-from-Western:Asia-
-Initial-Asian-Invasions
656-BCE:
~Greeks:
Romans-
eroded:African sovereignty-in-Kmt
entered-via-the-Sinai-and-Nile"
African-institutions-weakened; roads-opened:
of-Africax
642 CEx
for-later:Arab-domination &
VVandalsa
and North-Africa d
Delta&
Arabs-seized Egypt:from-Byzantine:
3. Arab-Conquest-of:
642-CE:
Arab-Caliphate-under:
Irule; renamed-the-capital-Cairo-(al-
Desert-and-sea-invasions-from -
Collapse-of:African-Kmt-religion; script; and-
Arabia-through-the-Red-Sea,
ladministration;-beginning-of-mass-cultural
North Africax
onwarda
Amr-ibn-al Asa
Qahira);-integrated North Africa-into
ISinai;; and-Maghreb.&
Arabization &
the-Arab-Islamic world&
Slave-centers: Cairo, Muscat;
Arabs-developed-a-systematic:
Jiddah; Aden; Mecca; Zeila;
Arabic-word-"'abd"-(meaning-both-
Black" _
~Institutionalization-of:
Umayyad; Abbasid, _
enslavement-economy-combining:
Zanzibar; Kilwa; Malindi;
and "slave") reflects-linguistic racism: Arab
7th _ 19th- lland-later-Sultanates
lreligion;, trade; and-imperial
African-Enslavement-by-
centuriesa
Oman; Zanzibar;
expansion: Africans captured-inland-
Mogadishu:
elites-integrated-enslavement-into-culture-and:
Arabsa
Yemen)a
land-sold-through-desert-and-coastal:
Markets:-Mecca;-Zabid,-Muscat; _
religion:-Millions-displaced, killed, or-
Aden;-Socotra; Massawa;Zeila
assimilated:
routes &
Bagamoyo; Sofala &
Isea-routes:-East:Africa-
7Arabia
Arabs-captured:Zanzibar-and-much-of:
The-Indian-Ocean-Slave-Trade-enslaved-an-
Persia-
India: &
Expansion-of-Arab-
1711-CE:-
Omani:Sultanate  &
Ithe-East:African-coast-(711-CE); built:
estimated-10
120-million-Africans-were-killed-
Maritime-Slave-Routesa
1800s3
Red-Sea-tradersa
fortresses-and-port:towns-for-export:
Land-routes: Central:Africa-
to-enslave-25-million-over-1,200-years   Arab-
lof:Africans_&
Isudan-
Egypt:
~Mecca
colonies-established-across-coastal:Africa.&
Baghdad.&
Arab_-Portuguese
500 _
[Portuguese-Empire;
Portuguese-joined Arab-traders-along
Kilwa;-Mombasa; and:Zanzibar:
European-colonial powers-adopted-and
Collaborationa
700-CEx
Arab-tradersa
East:and-West:African-coasts -merging served-asjointhubsa
lindustrialized-the Arab-model-of-mass-
JAtlantic-and-Indian-Ocean-systems_&
enslavement;-turning it-toward-the Americas_&
7. Transition-to
Portuguese"
Spanish- I[Europe-adapted Arab-slave-logistics:
Routes:-West:Africa: > Atlantic:
Over-30_45-million-Africans-were-shipped-
European-Atlantic-
1441_
British -
French-
into-a-triangular-trade-system:
Ocean-
Caribbean: / North
across the Atlantic;-an additional-150_200
Enslavementa
1888-CEx
Dutch-
Americansa
Africans-Were-exported-inthips-to-thelfoem Americabb
Imillion-died-during-capture-or-transport&
Americas-for-plantation-labor.&
~Total-Duration-and-
Cumulative-toll: over*300-million-Africans:
-Scale-of:
CE
Arab-and-European
Combined:Arab-and-European
Across-Sahara;-Red-Sea; and:
displaced; killed; or-enslaved: Entire-regions:
Demographic-
1900-CEx
powersa
enslavement-lasted-~1,250-years&
Atlantic-systems_&
Idepopulated; -massive-loss of-civilization-
Enslavementa
Icontinuity&
7th:
Language-as-weapon: ~
Abd" =-Black
Arabic and-Islamic-institutions-
Cultural-genocide: erasure-of:African-tongues,
9.-Linguistic-and-Cultural
century:
Arab-and-later-
~slave;-enforced-conversion-and-
Ireplaced-indigenous-education -
temples;
and-knowledge systems; Arab-and
Colonizationa
[European settlersa
European "civilization"-built-upon-African-
presenta
lrenaming &
land-worship-systems&
exploitation.&
Postcolonial-states-
7506
"of-the-world' s Arab-population"
10.-Long-Term-Legacy-
1900 _
dominated-by-foreign
now-resides-in-Africa;-indigenous-
Migratory-expansion-
Arabia- structural-dependency-and-underdevelopment
land-Present-Conditionsa
2025-CEx
lreligions;-languages,
populations-in-North-Africa-largely-
linto African-territories-(Egypt;
persist; Africa-continues-to-pay-human-and-
and-economiesa
eliminated.&
ISudan; Maghreb)&
economic-costs-while-Europe-and:Asia-profit &
'650 _
~from""",
        "ocr_confidence": {
            "avg_confidence": 0.6764,
            "min_confidence": 0.2070,
            "confidence_scores": [0.4365, 0.3491, 0.8480, 0.5271, 0.4376]
        }
    },
    {
        "name": "Graph 5: pipeline.jpg",
        "extracted_text": """Data Preparation
Indexing
Query
Retrieval
Generation
Response
Data
Data
Query
Sources
Loaders
Transformation
Qucry
OCR
HistoryContext
Caption
Query
Data
Chunk
Rewrite
Processing
Summary
Knowledge
LLM
Response
Graph
Model
Generation
BM25
OpenAI-compatibic API
Embedding
Hybrid
Ollama mojol
Retrieval
DenscRotrieval
OpenAI-corhpatibic API
KnowledgcGraph
Olam
mooci
Index Stroage
Rerank
Vector
OpenAI-compatibic API
Meta
Stroage
posiress
Chunk
Elasticsearch""",
        "ocr_confidence": {
            "avg_confidence": 0.8318,
            "min_confidence": 0.1193,
            "confidence_scores": [0.9910, 0.9148, 1.0000, 0.9514, 0.9998]
        }
    }
]

def main():
    """Test quality validation against REAL OCR results."""
    print("=" * 80)
    print("PRODUCTION-READY TESTING: Real OCR Results")
    print("=" * 80)
    print()
    print("Testing quality validation against ACTUAL extracted text from real images")
    print("This is what happens in production - not simulated tests")
    print()
    
    validator = QualityValidator()
    
    results_summary = {
        "should_reject": [],
        "should_accept": [],
        "should_review": []
    }
    
    for i, ocr_result in enumerate(REAL_OCR_RESULTS, 1):
        print("=" * 80)
        print(f"TEST {i}: {ocr_result['name']}")
        print("=" * 80)
        print()
        
        text = ocr_result['extracted_text']
        conf = ocr_result['ocr_confidence']
        
        print(f"OCR Confidence: {conf['avg_confidence']:.2%} avg, {conf['min_confidence']:.2%} min")
        print(f"Text length: {len(text)} chars, {len(text.split())} words")
        print()
        
        # Run ALL validation checks
        print("RUNNING QUALITY VALIDATION:")
        print("-" * 80)
        
        # 1. Confidence check
        conf_result = validator.validate_ocr_confidence(conf)
        print(f"1. Confidence: {conf_result.status.value.upper()}")
        print(f"   → {conf_result.reason}")
        
        # 2. Readability check
        read_result = validator.validate_readability(text)
        print(f"2. Readability: {read_result.status.value.upper()}")
        print(f"   → {read_result.reason}")
        
        # 3. Content quality check
        content_result = validator.validate_content_quality(text)
        print(f"3. Content: {content_result.status.value.upper()}")
        print(f"   → {content_result.reason}")
        
        # 4. Structure check
        struct_result = validator.validate_structure(text, None)
        print(f"4. Structure: {struct_result.status.value.upper()}")
        print(f"   → {struct_result.reason}")
        
        print()
        
        # Final decision
        all_results = [conf_result, read_result, content_result, struct_result]
        should_reject, reject_reason = validator.should_reject(all_results)
        should_review, review_reason = validator.should_review(all_results)
        
        print("PRODUCTION DECISION:")
        print("-" * 80)
        if should_reject:
            print(f"❌ REJECTED")
            print(f"   Reason: {reject_reason}")
            print()
            print("   → This garbage will NOT enter the RAG system")
            results_summary["should_reject"].append(ocr_result['name'])
        elif should_review:
            print(f"⚠️  REVIEW NEEDED")
            print(f"   Reason: {review_reason}")
            print()
            print("   → Flagged for human review before storage")
            results_summary["should_review"].append(ocr_result['name'])
        else:
            print(f"✅ ACCEPTED")
            print()
            print("   → This content will be stored in the RAG system")
            results_summary["should_accept"].append(ocr_result['name'])
        
        print()
        print()
    
    # Summary
    print("=" * 80)
    print("PRODUCTION TEST SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ ACCEPTED: {len(results_summary['should_accept'])}/{len(REAL_OCR_RESULTS)}")
    for name in results_summary['should_accept']:
        print(f"   - {name}")
    print()
    print(f"❌ REJECTED: {len(results_summary['should_reject'])}/{len(REAL_OCR_RESULTS)}")
    for name in results_summary['should_reject']:
        print(f"   - {name}")
    print()
    print(f"⚠️  REVIEW: {len(results_summary['should_review'])}/{len(REAL_OCR_RESULTS)}")
    for name in results_summary['should_review']:
        print(f"   - {name}")
    print()
    
    # Production readiness check
    print("PRODUCTION READINESS:")
    print("-" * 80)
    if len(results_summary['should_reject']) >= 2:
        print("✅ Quality system correctly rejects garbage extraction")
    else:
        print("❌ Quality system NOT rejecting garbage - NEEDS FIX")
    
    if len(results_summary['should_accept']) >= 2:
        print("✅ Quality system correctly accepts good content")
    else:
        print("❌ Quality system NOT accepting good content - NEEDS FIX")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

