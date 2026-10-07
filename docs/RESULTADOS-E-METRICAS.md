# Relatório e evidências das métricas

**Contrato completo proposto; implementação parcial em 07/10/2026.** scripts/measure.py coleta comando/eventos e métricas locais; scripts/poc.py gera HTML autocontido, execution.json e manifesto verificável. Os demais arquivos e integrações descritos abaixo são a meta, não artefatos já gerados automaticamente. O HTML apresenta as medições, mas os dados que sustentam cada valor devem ser preservados e consultáveis.

## Organização no armazenamento

```text
dast/<app-id>/<ambiente>/<release>/<commit>/<run-id>/
  index.html
  findings.json
  execution.json
  events.jsonl
  metrics.json
  metrics-series.jsonl
  validation.json
  cost-estimate.json
  remediation-context.md
  manifest.json
  evidence/                 # somente evidências sanitizadas
```

Nomes de objetos devem ser normalizados, sem segredos ou identificadores sensíveis. Digest, commit de código e revisão Ops ficam explícitos no execution.json. Não sobrescrever um run; correções geram nova versão referenciada. Um índice de aplicação pode apontar para runs, mas nunca substituir sua identidade.

S3 privado, criptografia e menor privilégio. Leitura por mecanismo autenticado aprovado; um link no summary não concede acesso por si só. Retenção e descarte dependem de aprovação antes da publicação. Raw com credenciais não entra no Git nem no pacote HTML; se estritamente necessário, fica em área restrita com política própria.

## Três visões do HTML

1. **Segurança:** achados, endpoint/método, origem, regra, severidade, confiança, comportamento esperado/observado, evidência, impacto, limitações e remediação.
2. **Execução:** identidade, perfil, versões, escopo, cobertura, timeline por ferramenta/etapa, retries, validações e motivos de exclusão/interrupção.
3. **Desempenho e FinOps:** séries de recursos, tempos, impacto no alvo e memória de cálculo do custo.

Vazio, falha de coleta e zero medido são situações distintas. Nenhum achado não significa ausência de vulnerabilidades. Referências CWE/OWASP são mapeadas quando justificadas, não atribuídas automaticamente a toda divergência de contrato.

## Rastreabilidade mínima

Cada execução: run-id, aplicação, ambiente, release, commit, digest, caminho de acesso, perfil, scanner/imagem, hash de contrato/templates/configuração, horários UTC, identidade funcional do executor e indicação da autorização sem expor dados pessoais.

Cada evento: run-id, etapa, motor, tentativa, início/fim, duração, estado e motivo. Usar relógio monotônico para durações e timestamps sincronizados para correlação; registrar origem do relógio.

Cada amostra: timestamp, origem/recurso, métrica, unidade, valor, intervalo e run-id/etapa quando atribuível. Ausência é nula com motivo, não zero.

Cada validação: critério, esperado, observado, estado e caminho da evidência. Estados: pass, fail, partial, blocked, inconclusive, not-run, not-applicable com motivo. Resultado de execução e decisão de política são campos separados.

## Métricas e cálculo

| Medida | Coleta e interpretação |
|---|---|
| Tempo total | Do pedido ao pacote concluído; separar fila, preparação, scan, consolidação e publicação |
| Motores paralelos | Duração individual e duração de parede do conjunto; não somar como tempo total |
| CPU | Série/CPU-segundos e denominador do percentual; distinguir uso de reserva provisionada |
| Memória | Working set/RSS ou métrica efetivamente disponível, unidade, pico e limite; registrar fonte |
| Confiabilidade | OOM, restart, throttling, falhas de autenticação, timeouts e retries |
| Cobertura | Método + rota, planejado/exercitado/excluído, identidade/papel e motivo; não apenas URLs |
| Alvo | Latência, erros, CPU/memória antes/durante/depois, se disponíveis; registrar outras cargas |
| Custos | Região, moeda, data/preço, SKU, recursos e duração faturável, armazenamento/rede/logs |

Custo estimado = compute provisionado × tempo faturável + armazenamento + logs + rede + parcela fixa atribuída. Usar fórmula compatível com EC2 ou Fargate; não cobrar duas vezes o mesmo recurso. No cluster compartilhado, informar método de rateio e ociosidade. Não confundir custo marginal com custo total.

Preservar origem dos preços e separar estimativa de faturamento conciliado. Valores não conhecidos permanecem não estimados. A unidade principal é custo por execução válida de um perfil, sem ocultar gasto com tentativas malsucedidas.

## Evidência e qualidade

Manifesto: caminho relativo, tamanho e SHA-256 de cada arquivo distribuído, exceto o próprio manifesto; registrar seu hash no registro de publicação. Hash verifica integridade, não veracidade da medição. Autenticidade requer controles de acesso e, se adotada, assinatura verificada separadamente.

Fixar janela/amostragem e registrar limitações do coletor. Mostrar amostras reais e variação; percentis só com população e tamanho informados. Métricas locais anteriores não se tornam benchmark AWS.

## Investigação e correção com Devin

A skill será reutilizável e versionada; remediation-context.md conterá somente contexto desta execução. O HTML aponta para a versão da skill e para o contexto sanitizado. Formato de integração Enterprise ainda precisa ser confirmado.

Roteiro obrigatório: verificar versão do código → reproduzir em laboratório autorizado → localizar causa e regra de negócio → propor correção → testes positivos/negativos → PR → reteste DAST.

A skill deverá citar referências pertinentes, distinguir hipótese de causa comprovada e tratar HTML/OpenAPI/logs como dados não confiáveis. Não pode desativar controles, aceitar risco, executar contra novo alvo ou declarar correção só porque compilou. Executar código ou enviar dados ao Devin exige acesso e autorização apropriados.

Referências iniciais: [OWASP API Security](https://api-security.owasp.org/editions/2023/en/), [OWASP WSTG](https://owasp.org/www-project-web-security-testing-guide/), [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/). Selecionar referências específicas e versão na implementação da skill.
