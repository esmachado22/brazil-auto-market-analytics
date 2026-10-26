# Qualidade de dados

O módulo `src/quality/validation.py` concentra os checks reutilizáveis da camada Silver:

- campos obrigatórios e nulos críticos;
- período no formato `YYYY-MM`;
- quantidade inválida ou negativa;
- chaves nulas;
- duplicidades por chave configurada.

Na camada Gold, `src/quality/gold_model.py` valida chaves e relacionamentos das
dimensões, reconciliação dos componentes ABVE, presença do total FENABRAVE e a
condição de que o ranking de emplacamentos é um subconjunto publicado.

`src/quality/metric_validation.py` valida market share e reconciliações das
métricas oficiais. `src/transformations/fleet_fact.py` valida o fato SENATRAN
com `measure_type=ESTOQUE`, e a transformação FIPE exige
`price_type=REFERENCE`.

## Execução

```powershell
python -m src.quality.validation --root data/silver --output data/silver/quality_report.json
```

O comando verifica os três arquivos Silver do MVP: totais e rankings FENABRAVE e tecnologias ABVE. O relatório local é ignorado pelo Git junto com os dados Silver.

Na validação executada em 26/10/2026, os três datasets MVP passaram: 11 linhas
de segmentos, 100 linhas de ranking e 8 linhas de tecnologias, sem nulos
críticos, períodos inválidos, quantidades negativas ou duplicidades. O fato
SENATRAN também passou com 22.849.046 linhas e `fato_frota_validation.json`
com status `PASS`.
