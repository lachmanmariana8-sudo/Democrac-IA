# Mapeo ISO 3166 ↔ UN M49

PEIRS usa **código numérico ONU (M49)** como llave maestra. Los datasets externos usan mayormente ISO3 (o peor, nombres en inglés con variantes). Por eso necesitamos una tabla de traducción.

## Fuente oficial

https://unstats.un.org/unsd/methodology/m49/

Descargar el archivo "M49 Standard Country or Area Codes" y complementar con ISO 3166 de https://www.iso.org/obp/ui/.

## Formato esperado

`iso/un_m49_country_codes.csv` con estas columnas:

```csv
country_code,iso3,iso2,name_en,name_es,region,subregion
32,ARG,AR,Argentina,Argentina,Americas,South America
604,PER,PE,Peru,Perú,Americas,South America
68,BOL,BO,Bolivia (Plurinational State of),Bolivia (Estado Plurinacional de),Americas,South America
858,URY,UY,Uruguay,Uruguay,Americas,South America
...
```

## Países de foco para PEIRS (Latam)

| M49 | ISO3 | Nombre ES |
|-----|------|-----------|
| 32 | ARG | Argentina |
| 68 | BOL | Bolivia |
| 76 | BRA | Brasil |
| 152 | CHL | Chile |
| 170 | COL | Colombia |
| 188 | CRI | Costa Rica |
| 192 | CUB | Cuba |
| 214 | DOM | República Dominicana |
| 218 | ECU | Ecuador |
| 222 | SLV | El Salvador |
| 320 | GTM | Guatemala |
| 340 | HND | Honduras |
| 484 | MEX | México |
| 558 | NIC | Nicaragua |
| 591 | PAN | Panamá |
| 600 | PRY | Paraguay |
| 604 | PER | Perú |
| 630 | PRI | Puerto Rico |
| 858 | URY | Uruguay |
| 862 | VEN | Venezuela |

## Códigos conflictivos

- **530**: Antillas Holandesas (disueltas en 2010). Usar 531 (Curaçao), 534 (Sint Maarten), 535 (Bonaire, Sint Eustatius y Saba).
- **736**: Sudán antes de 2011. Actual: 729 (Sudán), 728 (Sudán del Sur).
- **891**: Serbia y Montenegro (disuelta 2006). Actual: 688 (Serbia), 499 (Montenegro).
- **158** (Taiwán): no reconocido por ONU como M49 separado. Algunos datasets lo usan igual; documentar la fuente.
- **Kosovo**: sin código M49 oficial. V-Dem y FH lo incluyen con código propio (XKX o KSV). Decidir política del proyecto (ignorar, o mapear a un código interno >900).
