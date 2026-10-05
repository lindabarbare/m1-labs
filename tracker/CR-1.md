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
exported: "2026-10-05 · Ezermalas pieteikumu sistēma (simulācija)"
data_check: "Nav personas datu, iekšējo adrešu vai pielikumu. Personas kodi piemēros ir sintētiski."
---

# CR-1 · Personas koda pārbaude iesniegumā

> Noteikumi vienkāršoti mācību vajadzībām.

## Apraksts (description)

Iesniegumos bieži ir nepareizi personas kodi. Sistēmai jāpārbauda, vai personas kods ir derīgs, un nederīgi iesniegumi jānoraida.

## Pieņemšanas kritēriji (acceptance criteria)

| # | Ievade | Sagaidāmais rezultāts |
|---|---|---|
| 1 | `32000000001` | 201, saglabāts `32000000001` |
| 2 | `320000-00001` | 201, saglabāts `32000000001` |
| 3 | `" 32000000001 "` | 201 (atstarpes noņemtas) |
| 4 | `3200000000` (10 cipari) | 400 `INVALID_FORMAT` |
| 5 | `320000000012` (12 cipari) | 400 `INVALID_FORMAT` |
| 6 | `32000000O01` (burts O) | 400 `INVALID_FORMAT` |
| 7 | Lauka nav | 400 `REQUIRED` |
| 8 | Vecā formāta sintētisks kods `311299-21233` (31.12.2099, nākotnē) | 400 `INVALID_FORMAT` |
| 9 | `3200-0000001` (defise nepareizā vietā) | 400 `INVALID_FORMAT` | 10 | `092089-10078` (20. mēnesis) | 400 `INVALID_FORMAT` |
| 11 | `290200-10000` (29.02.1900, nav garais gads) | 400 `INVALID_FORMAT` |
| 12 | `290200-20000` (29.02.2000, garais gads) | 201, saglabāts `29020020000` |
| 13 | `150385-50000` (gadsimta cipars 5) | 400 `INVALID_FORMAT` |
| 14 | `00000010000` (sākas ar `00`) | 400 `INVALID_FORMAT` |
| 15 | Sintētisks vecā formāta kods `150385-00003` (15.03.1885) | 201, saglabāts `15038500003` |


## Precizējumi (clarifications)

| Jautājums | Atbilde | Kas atbildēja, kad |
|---|---|---|
| Vai pieņemt defisi? | Abus veidus: `DDMMYY-NNNNN` un 11 ciparus. Saglabāt 11 ciparus bez defises. | Produkta īpašnieks, 2026-09-30 |
| Vai pārbaudīt dzimšanas datumu vai kontrolciparu? | Jā. Vecajiem kodiem priekšā ir jābūt eksistējošam datumam. Jaunajiem kodiem (sākas ar `32`) nav ne viena, ne otra. | Produkta īpašnieks, 2026-09-30 |
| Tukša virkne vai tikai atstarpes? | Tāpat kā tad, ja lauka nav: 400 `REQUIRED`. | Produkta īpašnieks, 2026-09-30 |
| Kāda ir kļūdas atbilde? | 400 pēc līguma (API contract): `INVALID_FORMAT`, vai `REQUIRED`, ja lauka nav. Kļūda atbilst līguma kļūdu shēmai. | Produkta īpašnieks, 2026-09-30 |
| Vai kļūdas ziņojumā drīkst atkārtot ievadīto kodu? | Nē. Ne atbildē, ne žurnālā. Tikai lauka nosaukums un kļūdas kods. | Produkta īpašnieks, 2026-09-30 |
| Vai mainās atbildes shēma? | Nē. | Produkta īpašnieks, 2026-09-30 | Vai pārbaudīt dzimšanas datumu vai kontrolciparu? | Datumu jā, kontrolciparu nē. Vecajiem kodiem (nesākas ar `32`) pirmajiem 6 cipariem jābūt eksistējošam datumam DDMMGG. Jaunajiem kodiem (sākas ar `32`) nav ne viena, ne otra. | Produkta īpašnieks, 2026-10-05 |
| Kā noteikt gadsimtu? | Pēc 7. cipara: 0 = 1800, 1 = 1900, 2 = 2000. Ja 7. cipars ir 3–9, kods nav derīgs. | Produkta īpašnieks, 2026-10-05 |
| Vai kods, kas sākas ar `00` vai `33`–`99`, ir derīgs? | Nē. Tas nav ne datums, ne jaunais formāts. | Produkta īpašnieks, 2026-10-05 |
| Kāda kļūda, ja datums neeksistē vai gadsimta cipars nav derīgs? | 400 `INVALID_FORMAT`. | Produkta īpašnieks, 2026-10-05 | Vai dzimšanas datums drīkst būt nākotnē? | Nē. Datums nedrīkst būt vēlāks par iesnieguma saņemšanas dienu (Latvijas laiks). Šodien dzimis ir derīgs. Kļūda: 400 `INVALID_FORMAT`. | Produkta īpašnieks, 2026-10-05 |



## Ārpus tvēruma (out of scope)

- Kontrolcipara pārbaude
- Pārbaude reģistrā, vai persona eksistē (CR-2)
- Citu lauku pārbaude: vārds, e-pasts, temats, teksts
- Esošie iesniegumi ar nepareiziem kodiem
- Ārvalstnieki bez personas koda

## Komentāri (comments)

- 2026-09-28 · Reģistrācijas nodaļa: "Vakar 12 iesniegumi ar nepareizu kodu. Visi jālabo ar roku."
