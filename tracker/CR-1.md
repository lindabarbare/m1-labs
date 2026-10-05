---
id: CR-1
type: change-request
title: "Personas koda pārbaude iesniegumā"
status: READY
priority: high
reporter: "Reģistrācijas nodaļa (izdomāts)"
owner: "@<github-lietotājvārds>"
contract: "docs/openapi.yaml · POST /submissions · personalCode"
depends_on: []
exported: "2026-09-30 · Ezermalas pieteikumu sistēma (simulācija)"
data_check: "Nav personas datu, iekšējo adrešu vai pielikumu"
---

# CR-1 · Personas koda pārbaude iesniegumā

> Noteikumi vienkāršoti mācību vajadzībām.

## Apraksts (description)

Iesniegumos bieži tiek norādīti nepareizi personas kodi, kas rada papildu manuālu darbu reģistrācijas nodaļai. Sistēmai pirms iesnieguma saglabāšanas jāpārbauda personas koda formāts un datuma daļas korektums.

Ja personas kods neatbilst noteikumiem, iesnieguma iesniegšana nav atļauta un lietotājam jāparāda saprotams kļūdas paziņojums.

## Biznesa mērķis (business value)

- Samazināt manuālo kļūdu labošanu.
- Uzlabot datu kvalitāti sistēmā.
- Samazināt nepareizi aizpildītu iesniegumu skaitu.
- Samazināt reģistrācijas nodaļas darba apjomu.

## Funkcionālās prasības (functional requirements)

1. Sistēma pieņem personas kodu ar vai bez defises.
2. Sistēma pārbauda, ka personas kods satur 11 ciparus.
3. Ja ievadīta defise, tā var atrasties tikai pēc sestā simbola.
4. Jāvalidē datuma daļa:
   - diena;
   - mēnesis;
   - gads.
5. Ja personas koda pirmie divi cipari ir no 01 līdz 31, jāpiemēro klasiskais personas koda formāts.
6. Ja personas koda pirmie divi cipari ir 32, personas kods jāuzskata par jaunā formāta personas kodu.
7. Pēc validācijas personas kods datubāzē tiek saglabāts bez defises.
8. Nederīga personas koda gadījumā iesniegums netiek saglabāts.

## Pieņemšanas kritēriji (acceptance criteria)

| # | Ievade | Sagaidāmais rezultāts |
|---|---|---|
| 1 | 091288-10078 | akceptēts, datubāzē saglabā 09128810078 |
| 2 | 09238910078 | neakceptēts, datums 09.23.89 neeksistē |
| 3 | 322389-10078 | akceptēts, jaunā formāta personas kods |
| 4 | 32238910078 | akceptēts |
| 5 | 09128810078 | akceptēts |
| 6 | 310281-10067 | neakceptēts, februārī nav 31. datuma |
| 7 | 31028110067 | neakceptēts |
| 8 | 091288--10078 | neakceptēts, nederīgs formāts |
| 9 | 091288-1007 | neakceptēts, par maz ciparu |
|10 | 091288100789 | neakceptēts, par daudz ciparu |
|11 | 091288-10A78 | neakceptēts, atļauti tikai cipari un viena defise |
|12 | tukša vērtība | neakceptēts, obligāts lauks |

## Kļūdas paziņojumi (error messages)

| Kods | Ziņojums |
|--------|--------|
| PC-001 | Ievadiet personas kodu. |
| PC-002 | Personas koda formāts nav derīgs. |
| PC-003 | Personas kodā norādītais datums nav derīgs. |
| PC-004 | Personas kods drīkst saturēt tikai ciparus un vienu defisi. |

## Nefunkcionālās prasības (non-functional requirements)

- Validācija jāveic servera pusē.
- Validācijas rezultāts jāsaņem vienā API pieprasījumā.
- Validācijas izpildes laiks nedrīkst pārsniegt 1 sekundi normālas slodzes apstākļos.
- Personas kods nedrīkst tikt modificēts, izņemot defises izņemšanu pirms saglabāšanas.

## Precizējumi (clarifications)

| Jautājums | Atbilde | Kas atbildēja, kad |
|---|---|---|
| Vai jāatbalsta personas kodi ar defisi? | Jā, jāatbalsta abi formāti. | Reģistrācijas nodaļa, 2026-09-28 |
| Kā saglabāt personas kodu datubāzē? | Vienmēr bez defises. | Sistēmas īpašnieks, 2026-09-28 |
| Vai jāveic kontrolsummas pārbaude? | Nē, šīs izmaiņas ietvaros nav nepieciešams. | Produkta īpašnieks, 2026-09-29 |

## Ārpus tvēruma (out of scope)

- Personas koda kontrolsummas validācija.
- Personas datu pārbaude ārējās sistēmās.
- Dzimuma vai vecuma noteikšana no personas koda.
- Esošo ierakstu migrācija vai labošana datubāzē.

## Tehniskās piezīmes (implementation notes)

- API līmenī validācija jāizpilda pirms datu saglabāšanas.
- Pēc veiksmīgas validācijas jānormalizē vērtība, izņemot defisi.
- Validācijas loģiku ieteicams realizēt atsevišķā servisā vai utilītē, lai to varētu izmantot atkārtoti citās sistēmas vietās.

## Komentāri (comments)

- 2026-09-28 · Reģistrācijas nodaļa: "Vakar 12 iesniegumi ar nepareizu kodu. Visi jālabo ar roku."
- 2026-09-29 · Produkta īpašnieks: "Svarīgi saglabāt atbalstu ievadei gan ar defisi, gan bez tās."
``