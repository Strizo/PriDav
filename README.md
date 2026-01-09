# PriDav

Dobre hopefully vsetci viete ako tak s gitom narabat lebo ked nie tak sa nezarucujem ze to budem vediet fixnut xddd prinajmensom si davajte pozor na force veci a take tie zaklady no


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
Obsahuje 30 párov záverečných prác - diplomová práca a bakalárska práca od jedného autora.
Práce zároveň spĺňajú pravidlo, že bakalárske práce boli napísané v rokoch 2022 a pred, pričom diplomové práce po roku 2022
(vzhľadom na to že prvý generatívny AI model ChatGPT vznikol v novembri 2022).

Dáta boli zozbierané zo stránky `https://opac.crzp.sk`. 
Stránka je nevhodná na web-scraping. Síce každá práca má vlastný link na stránke, hľadanie prác prebieha cez JavaScript app, čiže vyhľadávanie sa nedá určiť v URL a následne výsledky zobrazuje len 20 až 100 výsledkov naraz. 
Tento fakt výrazne komplikoval zber dát, lebo tým pádom musel prebehnúť manuálne.

Výber prác chcel odrážať rozdelenie prác na stránke, z hľadiska odboru, školy a pohlavia autora.
Na to najprv poslúžili získané počty diplomových prác podľa odboru: 

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
|  5141 | Všeobecné lekárstvo* |     614 |
|  5166 | Zubné lekárstvo*      |      94 |
|  5214 | Farmácia*             |       5 |
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
