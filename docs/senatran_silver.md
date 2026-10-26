# Silver SENATRAN

O transformador `src/transformations/senatran.py` processa os arquivos oficiais de setembro de 2026 em streaming e cria três tabelas Silver com granularidades explícitas:

- `fleet_brand_model.csv.gz`: UF, município, marca/modelo, ano de fabricação e quantidade. **22.849.046 linhas**.
- `fleet_fuel.csv`: UF, município, combustível e quantidade. **59.504 linhas**.
- `fleet_power.csv`: UF, município, potência e quantidade. **1.125.676 linhas**.

O detalhamento de marca/modelo é armazenado comprimido porque o TXT descompactado tem mais de 1,2 GB e a repetição de proveniência por linha gera um CSV muito maior. A proveniência completa permanece nos metadados Bronze e no `quality_report.json`.

## Limitações de granularidade

Os arquivos de combustível e potência são agregados por UF e município. Eles não contêm uma chave de veículo individual nem uma chave de marca/modelo compatível com o arquivo de marca/modelo. Por isso, a Silver mantém tabelas separadas e não inventa uma associação entre combustível, potência e modelo.

SENATRAN representa estoque de frota. FENABRAVE e ABVE representam fluxo mensal de emplacamentos; os indicadores não devem ser somados ou rotulados como a mesma medida.

## Execução

```powershell
$py = 'C:\Users\Desktop\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m src.transformations.senatran --period 2026-09 --bronze-root data/bronze/senatran --silver-root data/silver/senatran
```
