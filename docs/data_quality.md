# Qualidade de dados

O módulo `src/quality/validation.py` concentra os checks reutilizáveis da camada Silver:

- campos obrigatórios e nulos críticos;
- período no formato `YYYY-MM`;
- quantidade inválida ou negativa;
- chaves nulas;
- duplicidades por chave configurada.

## Execução

```powershell
python -m src.quality.validation --root data/silver --output data/silver/quality_report.json
```

O comando verifica os três arquivos Silver do MVP: totais e rankings FENABRAVE e tecnologias ABVE. O relatório local é ignorado pelo Git junto com os dados Silver.

Na validação executada em 26/10/2026, os três datasets passaram: 11 linhas de segmentos, 100 linhas de ranking e 8 linhas de tecnologias, sem nulos críticos, períodos inválidos, quantidades negativas ou duplicidades.
