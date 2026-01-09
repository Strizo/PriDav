# PriDav

Tím: `bez názvu` \
Autori: ``Martin Kostolník, Filip Prutkay, Jakub Skaloš, Martin Striženec`` \
Zadanie: ``LLM začali byť populárne začiatkom roku 2023. Preto je teraz ideálna doba pozrieť sa na to,
ako ho používajú študenti pri písaní záverečných prác: veľa študentov, ktorí odovzdávali
svoju bakalársku prácu v roku 2022 (pred nástupom LLM) následne v roku 2024 (v čase už
hojného používania LLM) odovzdávali diplomovku na podobnú tému. Pomocou analýzy štýlu
písania (napríklad frekvencie k-tic písmen v nejakom úseku textu) skúste odhadnúť, za akú
časť diplomových prác študentov sú zodpovedné LLM``

**úvod**

**prečo slovenčina?**


## Hypotezy

1.  pozrieme sa na vyskyt n-gramov v danych pracach postupom rokov (bolo by za potreba velmi vela dat aby davalo aspon trochu zmysel typujem) a hypoteza bude ze sa samozrejme budu menit postupom rokov ako sa meni jazyk ale po roku 2022 nastanu vyraznejsie zmeny zmena nieco take
2.  Ai-cka si casto vymyslavala linky takze vedeli by sme predpokladat ze prace po 2022 budu mat vacsi vyskyt neexistujucich linkov (aj ked problemom moze byt ze pri tych starsich aj ked vtedy existovali uz nemusia)
3. práce po 2022 budú mať výrazne väčšiu entropiu slov ako práce predtým, keďže AI má lepšiu slovnú zásobu. Samozrejme študentovi sa mohla zvýšiť slovná zásoba, preto nás zaujíma výrazný rozdiel
4. podobne by práce po 2022 mali mať vyššiu entropiu druhov viet podľa štruktúry, keďže čerpá zo štylistyky viac autorov. Tiež nás zaujíma iba štatisticky významný rozdiel 
5. rozdelenie dĺžok viet má v diplomových prácach nižšiu entropiu ako v bakalárskych (kvôli zásahu LLM)
6. diplomové práce častejšie obsahujú nepresné alebo neoveriteľné citácie než bakalárske práce rovnakých autorov
7. v diplomových prácach bude viac tzv. generických fráz, ktoré sú typické pre LLM (napr. frázy ako "je možné konštatovať" alebo "vo všeobecnosti platí")


## Dáta

Použitý dataset sa nachádza v priečinku `./prace`.
Obsahuje 30 párov záverečných prác - diplomová práca a bakalárska práca od jedného autora v slovenčine, čo je náš skúmaný jazyk.
Práce zároveň spĺňajú pravidlo, že bakalárske práce boli napísané v rokoch 2022 a pred, pričom diplomové práce po roku 2022
(vzhľadom na to že prvý generatívny AI model ChatGPT vznikol v novembri 2022).

Dáta boli zozbierané zo stránky `https://opac.crzp.sk`. 
Stránka je nevhodná na web-scraping. Síce každá práca má vlastný link na stránke, hľadanie prác prebieha cez JavaScript app, čiže vyhľadávanie sa nedá určiť v URL a následne výsledky zobrazuje len 20 až 100 výsledkov naraz. 
Tento fakt výrazne komplikoval zber dát, lebo tým pádom musel prebehnúť manuálne.

Výber prác chcel odrážať rozdelenie prác na stránke, z hľadiska odboru, školy a pohlavia autora.
Na to najprv poslúžili získané počty diplomových prác podľa odboru (* označuje odbory, kde nepíšu bakalársku prácu, tieto neboli zohľadnené vo výbere): 

|   KÓD | POPIS                                           |   POČET |
|------:|:------------------------------------------------|--------:|
|  1113 | Matematika                                      |       5 |
|  1217 | Vedy o Zemi                                     |       7 |
|  1420 | Chémia                                          |       4 |
|  1536 | Biológia                                        |      20 |
|  1610 | Ekologické a environmentálne vedy               |       4 |
|  2118 | Získavanie a spracovanie zemských zdrojov       |       8 |
|  2381 | Strojárstvo                                     |      52 |
|  2508 | Informatika                                     |      30 |
|  2647 | Kybernetika                                     |      13 |
|  2675 | Elektrotechnika                                 |      13 |
|  2820 | Chemické inžinierstvo a technológie             |       7 |
|  2908 | Biotechnológie                                  |       4 |
|  2940 | Potravinárstvo                                  |       8 |
|  3331 | Drevárstvo                                      |       3 |
|  3507 | Architektúra a urbanizmus                       |       6 |
|  3636 | Geodézia a kartografia                          |       5 |
|  3659 | Stavebníctvo                                    |      15 |
|  3772 | Doprava                                         |       7 |
|  4190 | Poľnohospodárstvo a krajinárstvo                |       5 |
|  4219 | Lesníctvo                                       |       2 |
|  5141 | Všeobecné lekárstvo*                            |     614 |
|  5166 | Zubné lekárstvo*                                |      94 |
|  5214 | Farmácia*                                       |       5 |
|  5602 | Ošetrovateľstvo                                 |     506 |
|  5607 | Verejné zdravotníctvo                           |     168 |
|  5618 | Zdravotnícke vedy                               |      65 |
|  6107 | Filozofia                                       |      12 |
|  6115 | Sociológia a sociálna antropológia              |       6 |
|  6171 | Teológia                                        |       9 |
|  6213 | Ekonómia a manažment                            |     775 |
|  6718 | Politické vedy                                  |      87 |
|  6835 | Právo                                           |     158 |
|  7115 | Historické vedy                                 |      27 |
|  7205 | Mediálne a komunikačné štúdiá                   |      55 |
|  7320 | Filológia                                       |      48 |
|  7418 | Veda o športe                                   |      32 |
|  7605 | Učiteľstvo a pedagogické vedy                   |     385 |
|  7701 | Psychológia                                     |      79 |
|  7761 | Sociálna práca                                  |     920 |
|  8110 | Veda o umení a kultúre                          |      27 |
|  8202 | Umenie                                          |      61 |
|  9205 | Bezpečnostné vedy                               |     390 |
|  9610 | Obrana a vojenstvo                              |      14 |


Následne prebiehal výber. Príbuzné odbory, kde bolo k dispozícii málo prác, boli spojené do jednej query a z nej bol vytiahnutý pseudo-náhodný (s ohľadom na školu a pohlavie). V tabuľke nižšie je prehľad všetkých prác, pričom medzi odbormi sú všetky z query, výsledne vybraný je označený boldom:

| ODBORY                                                                                                                                                                    | MENO         | PRIEZVISKO      | NAZOV_BAK                                                                                                   | NAZOV_DIP                                                                                                                               |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------|:----------------|:------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------|
| Matematika, **Informatika**, Kybernetika,Elektrotechnika                                                                                                                        | Tomáš        | Vago            | Webová aplikácia na správu strešných stavieb                                                                | GPS systém pre kynologické záchranné zložky                                                                                             |
| Vedy o Zemi, Chémia, Biológia, **Ekologické a environmentálne vedy**, Získavanie a spracovanie zemských zdrojov, Chemické inžinierstvo a technológie, Biotechnológie, Potravinárstvo | Juraj        | Obuch           | Hodnotenie retencie vody a mikrobiálnej diverzity v zhutnených lesných a poľnohospodárskych pôdach          | Využitie retenčných vlastností superabsorpčných polymérov ako adaptačného opatrenia pre ochranu pôdy voči klimatickej zmene             |
| Strojárstvo                                                                                                                                                               | Miroslav     | Mareček         | Vplyv hluku na kvalitu pracovného prostredia vo vybranom podniku                                            | Návrh technologicko-technického riešenia objektu na farme dojníc v Oponiciach                                                           |
| Drevárstvo, Architektúra a urbanizmus, Geodézia a kartografia, Stavebníctvo, Doprava, Poľnohospodárstvo a krajinárstvo, **Lesníctvo**                                               | Jana         | Kľačková        | Zhodnotenie a návrh úprav poľovníckych chát na území LS Kyslinky, OZ Kriváň                                 | Analýza vývoja trofejovej kvality jelenej zveri v CHPO Poľana od roku 1995 po súčasnosť vplyvom dodržiavania kritérií selektívneho lovu |
| Filozofia, Sociológia a socialna antropológia, Teológia, **Filológia**, Historické vedy                                                                                           | Jozef        | Žigo            | Komentovaný preklad eseje od Rolanda Barthesa                                                               | ANALÝZA PREKLADU VLASTNÝCH MIEN A NÁZVOV V DIELE TEMNÝ OHEŇ                                                                             |
| Zdravotnícke vedy                                                                                                                                                         | Anna         | Hubčíková       | VPLYV MUTÁCIE FAKTORA V LEIDEN NA TEHOTENSTVO A JEHO DIAGNOSTIKA                                            | MONITOROVANIE ANTITROMBOTICKEJ LIEČBY NÍZKOMOLEKULOVÝMI HEPARÍNMI U HOSPITALIZOVANÝCH PACIENTOV POČAS PANDÉMIE COVID-19                 |
| Verejné zdravotníctvo                                                                                                                                                     | Patrik       | Posvancz        | DIAGNOSTICKÉ A TERAPEUTICKÉ METÓDY PRI OCHORENIACH ÚSTNEJ DUTINY A PAŽERÁKA                                 | Optimalizácia radiačnej ochrany na pracovisku so zdrojmi ionizujúceho žiarenia                                                          |
| Verejné zdravotníctvo                                                                                                                                                     | Vivien       | Stefankoviczová | Komunitná pneumónia ako problém verejného zdravotníctva                                                     | Infekčné ochorenia dýchacích ciest u detí                                                                                               |
| Politické vedy                                                                                                                                                            | Klaudia      | Kurillová       | Aktuálne podoby medzinárodného terorizmu                                                                    | Postoje krajín V4 voči Európskej migračnej kríze                                                                                        |
| Mediálne a komunikačné štúdiá                                                                                                                                             | Samuel       | Reščák          | Súčasné trendy v marketingovej komunikácii medzi firmou a spotrebiteľom                                     | Optimalizácia nákupného procesu vybraného e-shopu                                                                                       |
| **Umenie**, Veda o umení a kultúre                                                                                                                                             | Anežka       | Hudáčková       | Využitie cimbalu v jazzovej a populárnej hudbe                                                              | Interpretácia ázijskej hudobnej literatúry so zameraním na santour, yangqin, qanun                                                      |
| Psychológia                                                                                                                                                               | Martina      | Glosová         | Sebahodnotenie a sociálno-emocionálne zdravie žiakov Montessori školy a tradičnej základnej školy           | Sociálne reprezentácie polyamorie u psychoterapeutov a psychoterapeutiek na Slovensku                                                   |
| Právo                                                                                                                                                                     | Réka         | Kosárová        | Ochrana informácií v obchodno-právnych vzťahoch                                                             | Medzinárodnoprávna ochrana životného prostredia počas ozbrojeného konfliktu                                                             |
| Právo                                                                                                                                                                     | Volodymyr    | Prokofiiev      | Reforma Spoločného Európskeho Azylového Systému                                                             | Hodnotenie dôkazov v civilnom procese                                                                                                   |
| Veda o športe                                                                                                                                                             | Martin       | Činčár          | Využitie pohybových hier v pohybovej príprave detí                                                          | Vzťah pohybovej aktivity a kognitívnych schopnosti adolescentov                                                                         |
| Bezpečnostné vedy                                                                                                                                                         | Miklós       | Hervay          | Možnosti využitia vedľajších produktov z poľnohospodárskej výroby                                           | Zásady bezpečnosti práce pri opravách a údržbe strojov vo vybranom poľnohospodárskom podniku                                            |
| Bezpečnostné vedy                                                                                                                                                         | Miloš        | Mražík          | Kyberšikana adolescentov a možnosti jej riešenia                                                            | Branná príprava obyvateľov ako základný prvok obrany štátu                                                                              |
| Učiteľstvo a pedagogické vedy                                                                                                                                             | Nikola       | Špaková         | Možnosti využitia kruhových cvičení v školskom klube detí                                                   | Poruchy pozornosti u učiteliek a učiteľov pre primárne vzdelávanie                                                                      |
| Učiteľstvo a pedagogické vedy                                                                                                                                             | Dominika     | Kiššová         | Využitie audiovizuálnej didaktickej techniky v hudobnom vzdelávaní                                          | Vplyv pamäte a pozornosti na čítanie s porozumením u detí v prvom ročníku ZŠ                                                            |
| Učiteľstvo a pedagogické vedy                                                                                                                                             | Tomáš        | Hilkovič        | Prvá cesta okolo sveta a staré mapy s ňou súvisiace                                                         | Individuálna koncepcia vyučovania učiteľov dejepisu                                                                                     |
| Ošetrovateľstvo                                                                                                                                                            | František    | Pelikán         | Komplexná ošetrovateľská starostlivosť o pacienta s náhlou cievnou mozgovou príhodou                        | Informovanosť laickej verejnosti o postupoch prvej pomoci pri akútnom infarkte myokardu                                                 |
| Ošetrovateľstvo                                                                                                                                                           | Dominika     | Chladná         | Ošetrovateľský proces u pacienta s posttraumatickou stresovou poruchou                                      | Posttraumatická stresová porucha u zdravotníckych pracovníkov v zariadeniach pre seniorov v pandémii COVID-19                           |
| Ošetrovateľstvo                                                                                                                                                           | Lucia        | Šišmičová       | Komplexná ošetrovateľská starostlivosť o pacienta s Polyetiologickou demenciou                              | KVALITA ŽIVOTA U KLIENTOV V ZARIADENÍ SOCIÁLNYCH SLUŽIEB S AMYOTROFICKOU LATERÁLNOU SKLERÓZOU                                           |
| Ošetrovateľstvo                                                                                                                                                           | Lea          | Baloghová       | Kvalitatívna porucha vedomia pacientov na jednotkách intenzívnej starostlivosti                             | Assessment bazálnej stimulácie pri ošetrovateľskej starostlivosti o pacientov v kóme                                                    |
| Ekonómia a manažment                                                                                                                                                      | Simona       | Moravská        | VYUŽITIE PSYCHOLÓGIE V MARKETINGU A V REKLAMÁCH                                                             | PSYCHOLOGICKÉ FAKTORY VPLÝVAJÚCE NA SPOTREBITEĽSKÉ SPRÁVANIE                                                                             |
| Ekonómia a manažment                                                                                                                                                      | Miroslava    | Podracká        | Distribučné systémy v ubytovacích zariadeniach                                                              | Kognitívna mapa a jej adaptácia v rozhodovaní manažérov                                                                                 |
| Ekonómia a manažment                                                                                                                                                      | Radka        | Petríková       | Náklady a výnosy a ich vplyv na hospodársky výsledok podniku                                                | Minimálna mzda v krajinách V4 a jej vplyv na zamestnanosť                                                                               |
| Ekonómia a manažment                                                                                                                                                      | Patrik Tomáš | Galanda         | Aktuálne problémy MSP pri získavaní finančných zdrojov                                                      | Podpora univerzít zo zdrojov politiky súdržnosti                                                                                        |
| Ekonómia a manažment                                                                                                                                                      | Andrej       | Adamov          | Podnikateľské prostredie v krajinách Európskej únie                                                         | Lokalizácia ako dôležitý predpoklad znižovania budúcich nákladov podniku                                                                |
| Ekonómia a manažment                                                                                                                                                      | Alena        | Mižíková        | Analýza využívania metodík projektového riadenia v závislosti od typu projektu a prostredia jeho realizácie | Digitálna transformácia práce - výzvy a riziká                                                                                          |


## Metodológia a výsledky

### Hypotéza 3: entropia slovnej zásoby

Táto hypotéza sa zameriava na globálnu tendenciu používať viac generatívne AI na písanie prác. 
Premisou tejto hypotézy je fakt, že AI bolo natrénované na veľkom množstve autorov, preto bude niesť zjednotenie množstva slovných zásob.
Tým pádom slovná zásoba akéhokoľvek jednotlivca by mala byť podmnožinou tej AI.
To by sa malo preukázať v zvýšenej entropii v diplomovvých prácach oproti tým bakalárskym.

Na overenie tejto hypotézy potrebujeme uskutočniť:
1. Všetky slová z každej práce transformovať do gramaticky neutrálnej podoby
2. Pre každú prácu vypočítať entropiu z počtov rovnakých slov vrámci práce
3. Štatisticky overiť signifikantnosť výsledkov

Prvý krok vykonáva program `lemmatization.py`, ktorý načíta knižnicu `stanza` v slovenskom jazyku a vypíše výsledný text.
Knižnica používa na túto úlohu neurónovú sieť, ktorá avšak neuvádza 100% presné výsledky.
To nám však neprekáža, pretože chyby robí pomerne konzistentne, inak vysloňované slovo s rovnakým základom stále uvedie do rovnakého tvaru.

Druhý krok vykonáva program `word_entropy.py`, ktorý si slová ukladá do `dictionary` a z nich vypočíta pravdepodobnosti pre funkciu `scipy.stats.entropy`.
Výsledné entropie vypíše vo formáte `.csv`.

Tretí krok vykonáva `statistics.py`, ten najprv overí normalitu dát pomocou Shapiro-Wilk testu.
Ak dáta výjdu normálne v oboch distribúciach pre bakalárske aj diplomové práce, použije párový T-test.
Ak aspoň jedna nevýjde, použije radšej neparametrický párový Wilcoxonov test.
Tiež vykreslí histogramy pre porovnanie distribúcií.

Dáta pre diplomové práce nevyšli normálne, čiže bol použitý Wilcoxonov test. Ten ukázal $p-value \approx 0.9$, 
čiže hypotézu $H_0 : \theta_bak = \theta_dip$ zamietnuť nemôžme.
To potvrdzuje aj očný test na grafoch: