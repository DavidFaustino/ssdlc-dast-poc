# Matriz de avaliação DAST

Atualizada em **30/10/2026**. Escopo de avaliação: segurança, qualidade da detecção e operação. Estas famílias definem o que avaliar; não representam testes implementados ou aprovados. Cada família precisa ser desdobrada em casos por alvo, endpoint, identidade e comportamento esperado antes da execução autorizada.

Sete cenários de API em um mock não substituem esta matriz nem comprovam sete categorias inteiras do OWASP API Top 10. O [histórico](HISTORICO-E-REUSO.md) preserva os resultados anteriores; novas rodadas precisam de evidências próprias.

## Ambientes e finalidade

| Etapa | Finalidade | Critério de interpretação |
|---|---|---|
| Laboratório com falhas conhecidas | Avaliar detecção, lacunas e falsos positivos | Usar casos vulneráveis e controles seguros/corrigidos com resultado esperado conhecido |
| Dois microserviços autorizados na AWS | Avaliar cobertura, autenticação, conectividade, impacto e métricas reais | Ausência de findings não comprova capacidade de detecção |
| QA como destino operacional | Executar por release e integrar evidência à promoção | Disparo, política e operação precisam de validação própria |

VAmPI, Juice Shop, crAPI e mocks controlados têm papéis complementares. Juice Shop permite avaliar navegação web/SPA; crAPI permite preparar cenários de API e autorização; mocks fornecem controles repetíveis. A versão e os casos conhecidos de cada alvo devem ser fixados: o nome do laboratório não comprova cobertura. Os demais controles históricos constam do histórico de origem; não estão automaticamente empacotados neste repo.

## Segurança

Ferramentas abaixo são métodos previstos, não garantias de detecção. Test pack significa conjunto de casos direcionados, com identidades, dados e resultado esperado definidos.

| ID | Capacidade | O que testar e comprovar | Ferramenta ou método previsto |
|---|---|---|---|
| SEG-01 | Descoberta de APIs | Importar OpenAPI; identificar métodos, rotas e parâmetros; comparar operações previstas e exercitadas | ZAP e inventário |
| SEG-02 | Contrato e entradas | Tipos, campos obrigatórios, limites, entradas inválidas e divergências contrato/implementação | Schemathesis e casos direcionados |
| SEG-03 | Autenticação | Acesso com/sem credencial, credencial inválida/expirada e controles do login | ZAP/Nuclei configurados e casos direcionados |
| SEG-04 | Sessão autenticada | Manter sessão durante o scan, renovar credenciais, detectar perda de autenticação e testar logout quando aplicável | Monitoramento de sessão e testes específicos |
| SEG-05 | BOLA: autorização por objeto | A acessa seu objeto, mas não pode ler ou alterar objeto de B | Test packs com duas identidades e dados controlados |
| SEG-06 | BOPLA: autorização por propriedade | Campos sensíveis não são expostos nem alteráveis por quem não tem permissão | Test packs de leitura e alteração de campos |
| SEG-07 | BFLA: autorização por função | Usuário comum não executa operações administrativas ou de outro papel | Matriz de papéis e test packs |
| SEG-08 | SQL injection | Detectar casos conhecidos e comparar com controles corrigidos | ZAP ativo e confirmação controlada |
| SEG-09 | XSS | Separar casos refletidos, armazenados e DOM; demonstrar quais foram exercitados | ZAP e navegador/testes específicos |
| SEG-10 | Command injection | Detectar execução indevida em casos preparados, com evidência não destrutiva | ZAP/templates aprovados e confirmação controlada |
| SEG-11 | SSRF | Verificar requisições indevidas do servidor para destinos controlados | Casos direcionados; OAST quando necessário e autorizado |
| SEG-12 | Headers de segurança | Presença e adequação ao tipo de aplicação e resposta | ZAP passivo e regras contextualizadas |
| SEG-13 | Cookies | Atributos de segurança, escopo e comportamento de cookies de sessão | ZAP e inspeção de sessão |
| SEG-14 | CORS | Origens permitidas, credenciais e possibilidade de leitura indevida pelo navegador | Requisições direcionadas e navegador |
| SEG-15 | TLS | Certificado, nome, validade, protocolos e cifras no ponto de entrada escolhido | Verificador TLS dedicado, a selecionar |
| SEG-16 | Exposição de informações | Erros detalhados, stack traces, diagnóstico e dados sensíveis indevidos | ZAP/Nuclei e revisão contextual |
| SEG-17 | Crawling web/SPA | Alcançar páginas, rotas client-side, formulários e áreas autenticadas | Crawlers do ZAP e navegador |
| SEG-18 | CSRF | Operações de alteração de estado não podem ser acionadas indevidamente usando a sessão da vítima | Casos específicos com navegador |
| SEG-19 | Consumo de recursos e abuso | Limites de paginação, tamanho, frequência e fluxos sensíveis | Testes limitados e monitorados, não carga irrestrita |
| SEG-20 | Inventário e divergências | Contrastar API declarada/observada; identificar endpoints não documentados, versões antigas e divergências | Reconciliação OpenAPI, descoberta e release |
| SEG-21 | Consumo de APIs externas | Tratamento de respostas não confiáveis, erros e limites de dependências | Dependências simuladas e casos direcionados |
| SEG-22 | Exposições e vulnerabilidades conhecidas | Templates pertinentes à tecnologia, com versão e escopo registrados | Nuclei com templates aprovados |

XSS, cookies e CSRF não se aplicam automaticamente a toda API. TLS precisa identificar o terminador avaliado: Gateway, Ingress ou outro. Testar apenas o acesso interno não comprova controles do caminho externo, nem o inverso. Justificar cada exclusão.

Scan ativo não comprova todas as injeções; baseline passiva não equivale a avaliação completa de TLS. Autenticação deve priorizar os mecanismos nativos; proxy/adaptador é fallback condicionado a necessidade demonstrada. OAST é observação fora de banda para casos aplicáveis, não autorização para saída irrestrita.

## Qualidade da detecção

| ID | Avaliação | Evidência necessária |
|---|---|---|
| QUA-01 | Detecção correta | Caso vulnerável conhecido, resultado esperado e detecção confirmada |
| QUA-02 | Falso negativo | Falha conhecida não detectada; distinguir caso exercitado de rota que não foi alcançada |
| QUA-03 | Falso positivo | Alerta em caso seguro/corrigido, revisado com evidência |
| QUA-04 | Cobertura real | Operações e funcionalidades exercitadas por método, rota e identidade, não apenas URLs |
| QUA-05 | Reprodutibilidade | Repetições com mesma versão, configuração e dados; diferenças explicadas |
| QUA-06 | Reteste da correção | Falha detectada antes, correção aplicada e comportamento seguro confirmado depois |
| QUA-07 | Qualidade do finding | Evidência, origem, confiança, impacto, orientação de correção e limitações |
| QUA-08 | Complementaridade | Resultado por motor, sobreposição e lacunas sem contar duplicatas como ganho |

Um teste direcionado que comprova uma falha não comprova que o scanner a detectou. Preservar essa distinção. Não calcular precisão/recall sem conjunto de referência, denominadores e critérios de classificação explícitos. Falta de cobertura deve aparecer mesmo quando não entra no denominador de detecção.

## Operação na AWS e evolução para QA

| ID | Avaliação | O que comprovar |
|---|---|---|
| OPE-01 | Escopo e conectividade | Alvos autorizados alcançáveis; restrições de destino e redirecionamento funcionando |
| OPE-02 | Credenciais | Obtenção segura, menor privilégio, renovação e ausência de segredos nos relatórios |
| OPE-03 | Identidade da execução | Aplicação, ambiente, release, commit, digest e versões das regras vinculados ao resultado |
| OPE-04 | Tempo por etapa/perfil | Preparação, autenticação, descoberta, testes, consolidação e publicação medidos separadamente |
| OPE-05 | Recursos e FinOps | CPU/memória do executor, duração faturável, armazenamento/rede e custo com fonte |
| OPE-06 | Impacto no alvo | Latência, erros e recursos antes/durante/depois; critérios de interrupção |
| OPE-07 | Falhas e cancelamento | Timeout, perda de sessão, indisponibilidade, retries e limpeza sem sucesso falso |
| OPE-08 | Concorrência | Isolamento entre execuções e limites de jobs, sem interferência indevida |
| OPE-09 | Relatório e evidências | HTML privado, sanitização, integridade, retenção e consulta autorizada |
| OPE-10 | Disparo após deploy | Execução ligada à versão efetivamente implantada; detectar mudança durante o scan |
| OPE-11 | Política de promoção | Resultado técnico separado do gate; tratamento de parcial, ausência e exceções |
| OPE-12 | Correção e operação assistida | Contexto para Devin, investigação, testes de correção, reteste e passagem de trabalho |

OPE-10 e OPE-11 são evolução para QA, não pré-requisitos para a medição manual no playground. Registrar o estágio de cada caso. A existência dos scripts de medição não significa que todas as métricas acima já sejam coletadas; consultar o [contrato de resultados](RESULTADOS-E-METRICAS.md).

## Registro de cada caso

| Campo obrigatório | Conteúdo |
|---|---|
| Identificação | ID do caso e família SEG/QUA/OPE; perfil e etapa |
| Alvo | Aplicação, versão/digest, ambiente, ponto de entrada, método/rota ou função |
| Pré-condições | Contrato, dados, papéis, controles positivos/negativos e autorização |
| Procedimento | Passos reproduzíveis, motor/regra e versão, limites e limpeza |
| Esperado | Comportamento seguro/vulnerável conhecido; critério definido antes do teste |
| Execução | Executado, parcial, bloqueado, não executado ou não aplicável; motivo |
| Detecção | Detectou, não detectou ou inconclusivo; não aplicável para caso puramente operacional |
| Validação | Verdadeiro positivo, falso positivo, falso negativo, controle seguro confirmado ou inconclusivo |
| Evidência | Run-id e caminhos sanitizados; referências dos resultados e métricas |
| Continuidade | Pendência, responsável, próximo passo e reteste relacionado |

Exemplo apenas didático: SEG-05 em laboratório vulnerável com usuário A e objeto de B. Se o teste comprovar acesso indevido e o motor alertar corretamente, a detecção é verdadeiro positivo; a aplicação continua vulnerável. Se a requisição não puder ser executada por falha do ambiente, registrar bloqueado/inconclusivo, não falso negativo nem controle seguro.

## Como usar a matriz

1. Selecionar os casos aplicáveis por alvo, sem apagar as exclusões: registrar justificativas.
2. Fixar versões e controles conhecidos no laboratório antes de medir detecção.
3. Reconciliar resultados históricos com os casos correspondentes, preservando o run original; não herdar aprovação para uma nova versão ou alvo.
4. Executar nos dois serviços somente o recorte autorizado, com limites e critérios de interrupção acordados.
5. Publicar resultado por caso, lacunas e métricas, sem percentual global que misture famílias, endpoints e execuções.
6. Decidir a evolução para QA com base nas evidências. Critérios quantitativos e cobertura obrigatória por perfil precisam ser acordados antes da rodada; esta matriz não inventa limiares de aprovação.

Não é necessário executar todas as famílias em todo deploy. O [desenho de arquitetura](ARQUITETURA.md) propõe perfis smoke, release, deep e incident; sua seleção e os tempos precisam de medição. DefectDojo permanece na segunda etapa; agente AI local, IAST/RASP e ampliação de protocolos são experimentos separados. GraphQL e protocolos assíncronos dependem do inventário e de casos/executores próprios, sem cobertura implícita pela matriz REST/web.

## Documentos relacionados

- [Plano de execução](PLANO.md): etapas e critérios de entrega.
- [Runbook do Devin](RUNBOOK-DEVIN.md): preparação e operação do pacote disponível.
- [Relatórios e métricas](RESULTADOS-E-METRICAS.md): formato das evidências e limitações de implementação.
- [Histórico e reaproveitamento](HISTORICO-E-REUSO.md): resultados anteriores e fontes de laboratório.
- [Passagem de trabalho](HANDOFF.md): estado e próxima ação.
