# Fato de frota

O fato Gold `data/gold/fato_frota.csv.gz` é construído por `src/transformations/fleet_fact.py` a partir da Silver SENATRAN de marca/modelo.

Cada linha tem o indicador `measure_type=ESTOQUE`. O grão é período, UF, município, marca/modelo, ano de fabricação e quantidade. A chave `frota_key` é determinística e a proveniência permanece em cada linha.

Essa marcação é obrigatória para análises: FENABRAVE e ABVE medem fluxo mensal de emplacamentos; SENATRAN mede estoque registrado na frota. O modelo não permite interpretar o fato de frota como venda mensal.

Execução:

```powershell
$py = 'C:\Users\Desktop\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m src.transformations.fleet_fact --period 2026-09 --silver-root data/silver/senatran --gold-root data/gold
```
