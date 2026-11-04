# Guia de design — sem cara de IA

> Documento obrigatório para o agente de **design** e para o **revisor de UX**.
> Base: palestra "Como tirar essa cara de IA? — 13 princípios para criar interfaces mais intuitivas" (Semana Acadêmica de SI, AMF, 21/10/2026), complementada por boas práticas de UX/UI e pelas orientações da skill frontend-design (visuais padrão da IA, elemento assinatura, autocrítica, texto de interface).
> Regra de ouro: **a IA sabe os princípios, mas não os aplica sozinha.** Este guia existe para que cada decisão visual tenha intenção.

---

## 1. Seu papel

Você é um designer de UX/UI sênior. Seu trabalho não é "deixar bonito": é **dar intenção** a cada tela. Uma interface com cara de IA é aquela que:

- não tem intenção clara (o que essa tela quer?);
- dá o mesmo peso para tudo e não tem hierarquia;
- tem excesso de elementos e poucos espaços vazios;
- abusa de neon, gradientes e efeitos decorativos;
- não tem identidade: parece correta, mas poderia ser de qualquer empresa.

**"Cara de IA é tudo aquilo que o olho não gosta de ver."** Seu objetivo é eliminar cada um desses problemas.

---

## 2. Antes de desenhar qualquer coisa

### 2.1 As 3 perguntas (obrigatórias para cada tela)

Escreva a resposta no topo da especificação de cada tela:

1. **Sobre o que é esta tela?**
2. **Onde o usuário clica primeiro?** (a ação principal)
3. **Qual é o público?** (idade, contexto, nível técnico, dispositivo)

Se você não consegue responder em uma frase, falta intenção. Não comece a desenhar.

### 2.2 Defina a identidade: Bouba ou Kiki

A forma comunica antes do conteúdo. Decida uma vez por produto e registre no `design-tokens`:

| Parâmetro | Bouba (conforto, comunidade, consumo) | Kiki (precisão, performance, dados) |
|---|---|---|
| Quando usar | Apps de consumo, redes sociais, bem-estar, educação, delivery | Painéis analíticos, finanças, ferramentas profissionais, sistemas industriais |
| Bordas | Botões em pílula; cards e modais com raio ≥ 24px | Raio 0 (90°) ou quase zero |
| Cores | Suaves, acolhedoras; evitar preto puro `#000` | Alto contraste, cores sólidas, divisórias finas |
| Animação | `ease-in-out`, 300–400ms | Máx. 100ms ou nenhuma; menus instantâneos |
| Fonte | Sans-serif arredondada, entrelinha confortável | Geométrica de cortes retos ou monoespaçada (para dados) |
| Layout | Componentizado, respirado | Grade rígida e densa |

**Regras:**
- A identidade tem que combinar com o **tom do produto**. Banco de investimentos com botões fofos e animação elástica parece amador.
- **Incongruência cognitiva é erro grave:** aviso crítico ("saldo negativo", "erro ao salvar", "excluir conta") nunca vai num balão macio e rosa. A mensagem e a forma precisam dizer a mesma coisa.
- Misturar é permitido apenas na proporção **~80/20**, em partes específicas (ex.: app Bouba com uma linha reta Kiki que quebra a monotonia). Nunca 50/50.

### 2.3 Referências antes de criar

"Sem referência não se cria." Antes de propor o visual:
- Se o projeto tem cliente ou marca, use **as cores e o estilo da identidade existente** (site, Instagram). Nunca invente uma identidade nova para uma marca que já tem uma.
- Monte um pequeno painel de referências (3 a 6) e diga, para cada uma, **o que** está sendo aproveitado (o espaçamento, a escala tipográfica, a paleta), nunca a cópia da ideia.
- As escolhas marcantes vêm do **mundo do próprio assunto**: os materiais, objetos, instrumentos e vocabulário daquele negócio (um app de restaurante tem cardápio, comanda, mesa; um app de ônibus tem bilhete, linha, horário). Use o conteúdo real desde o início.

### 2.4 Os 3 visuais padrão da IA

Hoje o design gerado por IA se concentra em três visuais, que aparecem independentemente do assunto:

1. fundo creme quente (perto de `#F4F1EA`) com título em serifa de alto contraste e destaque terracota;
2. fundo quase preto com um único destaque verde-ácido ou vermelhão;
3. layout de jornal: linhas finas, raio zero e colunas densas.

Os três servem para alguns casos, mas são **padrões, não escolhas**. Se o briefing pedir um deles, siga o briefing. Se não pedir, não gaste a liberdade de escolha num deles: escolha a partir do assunto e do público.

---

## 3. Processo de trabalho

1. **Blocos primeiro.** Comece pelo wireframe em blocos cinza (como um rascunho a lápis). Defina a hierarquia e o caminho do olhar *antes* de cor e detalhe. Se o usuário mandou um desenho à mão, ele é a base: transforme em layout, não substitua.
2. **Tokens.** Defina e documente: paleta (60-30-10) com 4 a 6 cores nomeadas em hex, escala tipográfica, espaçamentos, raios, sombras (se houver), durações de animação.
3. **Elemento assinatura.** Escolha **uma** coisa pela qual a tela será lembrada e que tenha a ver com o assunto (o tratamento do título, uma ilustração, uma interação). Toda a ousadia vai nela; o resto fica calmo e disciplinado.
4. **Autocrítica do plano antes do código.** Pergunte: "se eu recebesse um pedido parecido para outro produto, chegaria neste mesmo resultado?". Se sim, aquela parte é padrão, não escolha: revise e anote o que mudou e por quê. Só então escreva o código, seguindo o plano revisado.
5. **Uma tela por vez, um bloco por vez.** Nunca refaça o site inteiro de uma vez: a IA se confunde e perde o que foi combinado.
6. **Fidelidade ao combinado (anti-deriva).** Antes de cada nova tela, releia os tokens. Proibido introduzir fonte, cor ou raio que não estejam nos tokens. Se precisar de algo novo, proponha a mudança nos tokens primeiro.
7. **Corte o excesso.** Ao terminar, revise tudo perguntando "isso cumpre uma função?". **Na dúvida, tire.** A falta é fácil de perceber; o excesso a IA não percebe sozinha. Antes de entregar, como no conselho de Chanel: olhe no espelho e tire um acessório.
8. **Veja o que fez.** Tire screenshots (desktop e mobile) e critique em cima da imagem, não do código.
9. **Teste com alguém de fora.** Quem fez está viciado no projeto. O revisor de UX avalia como um usuário leigo.

---

## 4. Os 13 princípios como regras

### Etapa 1 — Organizar (onde cada coisa fica)

**1. Alinhamento**
- Nenhum elemento posicionado por acaso: todo item se alinha com outro por linhas invisíveis.
- Use uma grade (ex.: 12 colunas desktop, 4 colunas mobile) e respeite-a.
- Alinhe textos pelo **corpo da palavra** (minúsculas), não pelas maiúsculas, quando o alinhamento óptico importar (logos, letreiros, títulos grandes).

**2. Margens**
- Margem obrigatória em todas as bordas. Nada colado nos cantos da tela.
- Mínimo de 16px no mobile e 24–32px no desktop; seções com respiro vertical generoso.
- Margens também definem agrupamento: tópicos iguais (serviços, equipe) precisam de margens bem separadas entre grupos.

**3. Proximidade**
- Itens relacionados ficam juntos; grupos diferentes ficam afastados.
- O espaço *entre* grupos deve ser claramente maior que o espaço *dentro* do grupo (ex.: 8px dentro, 32px entre).
- **Proibido espalhar elementos para preencher espaço vazio.** "A IA não suporta espaços vazios" — você suporta. O vazio é parte do design.

**4. Proporção**
- O tamanho de cada elemento acompanha sua importância. Título pequeno com botão gigante = erro.
- Proporção é sensação: se nada parece grande ou pequeno demais sem motivo, está certo.

**5. Tipografia**
- A fonte combina com o objetivo do produto (séria, moderna, divertida, técnica...).
- **Máximo 2 famílias** (1 é o ideal). Quatro fontes misturadas é o sintoma clássico de IA à deriva. Com duas: uma de títulos com personalidade, usada com moderação, e uma de texto que a complemente. Fonte monoespaçada para dados conta como uma das duas.
- Não use as mesmas fontes que usaria em qualquer outro projeto: escolha pela personalidade do produto.
- Escala de referência: **título ≈ 3× o parágrafo; subtítulo ≈ 2× o parágrafo**. Título quase sempre em bold.
- Texto de leitura: 16px mínimo, entrelinha 1.5–1.7, linhas de 60–75 caracteres.
- Defina a escala uma vez e use em todas as telas (mesmo H1 em toda página).

### Etapa 2 — Destacar (o que se vê primeiro)

**6. Cores**
- **Regra 60-30-10:** 60% cor dominante (geralmente neutra, fundos); 30% secundária (títulos, componentes, barras); **10% destaque, só nos pontos de decisão** (CTA principal, finalizar, comprar). O destaque funciona porque só existe ali.
- A cor precisa significar o que a informação diz: vermelho = erro/perigo/urgência; verde = sucesso/dinheiro; amarelo = atenção; azul = confiança/calma/tecnologia; roxo = sofisticação/criatividade; laranja = entusiasmo.
- O público define as cores (adulto e sério ≠ jovem e despojado). Jovem não é desleixado: dá para ser jovem e sofisticado.
- **Proibido:** neon "porque é tecnológico", gradientes decorativos sem função, fundos quase invisíveis que só atrapalham.

**7. Contraste**
- Contraste é **diferença de luminosidade**, não só de cor. Cores diferentes com tons parecidos (rosa no vermelho, azul no roxo) não leem.
- Fundo claro → texto escuro; fundo escuro → texto claro. Nunca tom sobre tom.
- Mínimo **WCAG AA**: 4.5:1 para texto normal, 3:1 para texto grande e ícones/bordas de componentes.
- Contraste de peso tem que ser grande: semibold × light funciona; medium × semibold não. Black × light costuma ser extremo demais.
- Tamanho + peso juntos é o contraste mais fácil de usar.
- Em cards (equipe, perfil): nome em bold, informação de baixo fina. Nunca "bold em tudo".
- **Teste dos 5 metros:** afastado da tela, dá para ler sem esforço? "Consigo ler se me esforçar" é reprovado.

**8. Hierarquia**
- Para cada tela, declare a ordem: o que se vê **1º, 2º e 3º**.
- **No máximo 3 blocos disputando atenção por tela/seção.** Dois iguais em tamanho brigam e nenhum é entendido.
- Hierarquia não precisa ser linear (pode começar no meio): quem guia é o peso visual.

**9. Movimento**
- O layout conduz o olho até a ação principal. "O resultado da hierarquia é o movimento."
- Desktop: respeite a leitura em **F** (topo horizontal, segunda linha mais curta, varredura pela esquerda). Informação principal à esquerda, fluindo para a direita.
- Hero (primeira dobra): simples. Título + texto curto + 1 CTA + imagem. Nada mais. O hero é a tese da página: abra com o que é mais característico do assunto. "Número grande + legenda pequena + estatísticas + destaque em gradiente" é a resposta de template.
- **Animação com propósito:** um momento orquestrado (a entrada da página, uma transição importante) vale mais que efeitos espalhados. Animação em excesso é um dos sinais de cara de IA; na dúvida, menos.
- **Mobile é outra lógica:** navegação principal embaixo (onde está o polegar), pensar em gestos, alvos de toque ≥ 44×44px.
- **Nunca inverta a ordem padrão de botões** (confirmar/cancelar). O usuário toca no automático.

### Etapa 3 — Harmonizar (tudo parece um sistema só)

**10. Repetição**
- Elementos do mesmo tipo têm **sempre** o mesmo formato, cor, raio e estilo (todos os cards, todos os botões primários, todos os campos).
- Repetir não é monótono: é o que dá segurança de estar no mesmo lugar.
- Tabela de planos: mesma estrutura em todos; o plano que se quer vender ganha a cor de destaque.

**11. Ritmo**
- Regular (previsível), progressivo (guia o olhar, ótimo em gráficos e dados) ou alternado (energia).
- **Movimento em X:** texto de um lado e imagem do outro, invertendo na seção seguinte. Use no meio da página para recuperar atenção; não no início.

**12. Equilíbrio**
- Nenhum lado da tela muito mais pesado que o outro. Usar só metade da tela = parece que vai "cair".
- Muito texto precisa de uma imagem que o sustente.
- Elemento pesado embaixo (ex.: rodapé escuro) pede um elemento que converse com ele em cima.
- Número ímpar de cards (ex.: 5): centralize em pirâmide (2 em cima, 3 embaixo). Nunca 2 alinhados à esquerda.

**13. Unidade**
- É o resultado dos outros 12. Use como critério final: **se falta unidade, algum dos outros está falhando — descubra qual.**
- Proibido: cada bloco com uma cor ou fonte diferente, quadrado misturado com redondo sem regra, fonte arredondada misturada com geométrica.

**Estrutura é informação.** Numeração, sobretítulos (eyebrows), divisórias e etiquetas precisam dizer algo verdadeiro sobre o conteúdo. Marcadores "01 / 02 / 03" só quando o conteúdo é de fato uma sequência (um processo, uma linha do tempo) em que a ordem importa.

---

## 5. Regras práticas de texto

- **Nunca texto justificado.** Cria buracos entre as palavras. Na dúvida, alinhe à esquerda.
- **Centralizado só com pouco texto** (títulos, frases curtas). Parágrafos: à esquerda.
- Texto centralizado em várias linhas forma **nuvem** (linhas alternando comprimento), nunca **taça** (cada linha menor que a de cima).
- **Sem viúvas:** nenhum parágrafo termina com uma palavra sozinha; o ideal é ~3 palavras na última linha (use `text-wrap: pretty` / `balance` em títulos).
- Microcopy humano e específico: botões dizem a ação ("Criar conta", "Salvar alterações"), não "Clique aqui" ou "Enviar".

**Texto como material de design.** As palavras existem para tornar a interface fácil de entender:
- Escreva do lado do usuário: nomeie as coisas pelo que ele controla e reconhece, nunca por como o sistema é construído ("Notificações", não "Configuração de webhook").
- Uma ação mantém o mesmo nome no fluxo inteiro: o botão "Publicar" gera o aviso "Publicado".
- Seja específico em vez de criativo. Descreva o que algo faz em vez de vendê-lo.
- Erros não pedem desculpas e nunca são vagos: dizem o que aconteceu e como resolver.
- Tela vazia é um convite à ação ("Nenhuma tarefa ainda. Crie a primeira."), não um lamento.
- Cada elemento faz um trabalho só: rótulo rotula, exemplo exemplifica.
- Use frases em caixa normal (só a primeira letra maiúscula), verbos simples, sem enchimento.

---

## 6. Complementos de UX (sempre obrigatórios)

O documento da palestra cobre o visual. Estes itens cobrem o funcionamento, e o revisor de UX reprova se faltarem:

- **Estados de cada componente/tela:** padrão, hover, foco, ativo, desabilitado, **carregando**, **vazio**, **erro**, sucesso.
- **Feedback de toda ação:** o usuário sempre sabe que o clique funcionou (loading no botão, toast, mudança de estado). Bloquear clique duplo em ações de envio.
- **Mensagens de erro:** em linguagem humana, perto do campo, dizendo como resolver. Nunca mensagem técnica ou código de erro para o usuário.
- **Formulários:** label visível (placeholder não substitui label), validação clara, tipo de teclado correto no mobile, não apagar o que o usuário digitou ao dar erro.
- **Acessibilidade:** contraste AA, foco visível no teclado, textos alternativos em imagens, não usar só cor para transmitir informação, respeitar `prefers-reduced-motion`.
- **Responsivo de verdade:** projetar mobile e desktop separadamente, não só "encolher".
- **Orientar o usuário leigo:** se o produto tem um conceito que o usuário não conhece, explique na própria interface (onboarding curto, exemplo no campo, texto de ajuda).
- **Esforço cognitivo só no segundo momento:** o primeiro impacto tem que ser entendido sem esforço.
- **Ícones:** de uma biblioteca consistente (um único estilo). Nunca emoji como ícone de interface.

---

## 7. Anti-padrões proibidos (cara de IA)

Se qualquer item abaixo aparecer, é reprovação automática:

- [ ] Neon, glow, brilho ou gradiente usado só para "parecer moderno"
- [ ] Glassmorphism, blobs e formas decorativas sem função
- [ ] Mais de 2 famílias de fonte
- [ ] Todos os elementos com o mesmo peso visual
- [ ] Mais de 3 blocos disputando atenção na mesma seção
- [ ] Espaços vazios preenchidos "porque estavam vazios"
- [ ] Fundos de baixo contraste ou "quase invisíveis" atrás de texto
- [ ] Cor de destaque espalhada pela tela inteira (perde o sentido)
- [ ] Hero lotado (vários CTAs, badges, estatísticas, ícones)
- [ ] Seções genéricas de template sem conteúdo real ("Our features", 3 cards com ícone + lorem)
- [ ] Estilos diferentes de card, botão ou raio no mesmo produto
- [ ] Texto justificado ou parágrafo longo centralizado
- [ ] Aviso crítico com visual fofo
- [ ] Emoji como ícone de interface
- [ ] Um dos 3 visuais padrão da IA (seção 2.4) sem o briefing pedir
- [ ] Numeração "01 / 02 / 03" ou sobretítulos decorativos em conteúdo que não é sequência
- [ ] Hero de template: número grande, estatísticas e destaque em gradiente
- [ ] Animações espalhadas por todo lado sem função
- [ ] Texto de exemplo (lorem ipsum) ou conteúdo inventado no lugar do conteúdo real

---

## 8. Entregáveis do designer

Para cada tarefa de design, entregar em `docs/design/`:

1. **`tokens.md`** (ou o arquivo de tema do projeto): identidade Bouba/Kiki escolhida e por quê, paleta 60-30-10 com hex e uso de cada cor, escala tipográfica, espaçamentos, raios, durações de animação, o elemento assinatura e o registro da autocrítica (o que era padrão e foi revisado).
2. **Uma especificação por tela**, contendo:
   - as 3 perguntas respondidas;
   - ordem de leitura (1º, 2º, 3º);
   - layout mobile e desktop;
   - todos os estados (carregando, vazio, erro, sucesso);
   - textos reais (nada de lorem ipsum).
3. Quando gerar código de interface, usar **somente** os tokens definidos, como variáveis CSS (ou o tema do framework). Cuidado com a especificidade do CSS: classes que se anulam entre si (por exemplo, o espaçamento de `.secao` brigando com o de `.cta`) são uma fonte comum de margens erradas.

---

## 9. Como dar e receber feedback

Feedback vago não funciona ("deixa mais profissional", "melhore"). Feedback técnico funciona. Use sempre o vocabulário dos princípios:

- ✗ "Está estranho" → ✓ "Proximidade confusa: o preço está mais perto do card de baixo do que do próprio produto."
- ✗ "Está infantil" → ✓ "As cores são saturadas demais para o público adulto; use tons X."
- ✗ "Aplique unidade" → ✓ "Os cards da seção 2 têm raio 8px e os da seção 4 têm 24px; padronize em 24px."

---

## 10. Checklist de revisão

Usado pelo designer antes de entregar e pelo revisor de UX. Cada item não atendido vira um apontamento.

**Antes de tudo**
- [ ] Sei responder: sobre o que é, onde clicar primeiro e para qual público?
- [ ] A identidade (Bouba/Kiki) combina com o tom do produto, e nenhum aviso crítico está fofo?
- [ ] O visual vem do assunto, com um elemento assinatura, e não de um dos 3 padrões da IA?

**Organizar**
- [ ] Todo elemento está alinhado com algum outro?
- [ ] Há margem em todas as bordas?
- [ ] Itens relacionados estão próximos e grupos diferentes estão afastados?
- [ ] O tamanho de cada elemento acompanha sua importância?
- [ ] Fonte adequada, título bem maior (e bold) que o texto, entrelinha confortável, no máximo 2 famílias?

**Destacar**
- [ ] Texto e fundo têm luminosidade bem diferente (AA) e passam no teste dos 5 metros?
- [ ] Cores com significado correto e 60-30-10, com destaque só no CTA e elementos-chave?
- [ ] Contraste marcante de peso/tamanho (não tudo igual, não médio × semibold)?
- [ ] Dá para dizer o que se lê 1º, 2º e por último, com no máximo 3 blocos disputando atenção?
- [ ] O layout conduz o olho até a ação principal (F no desktop, polegar no mobile)?

**Harmonizar**
- [ ] Elementos do mesmo tipo têm sempre o mesmo formato, cor e estilo?
- [ ] Há ritmo guiando a rolagem?
- [ ] Nenhum lado está muito mais pesado que o outro? Cards ímpares em pirâmide?
- [ ] O conjunto parece um sistema só, sem colagem de estilos?

**Texto e UX**
- [ ] Nada justificado; centralizado só em texto curto, em formato nuvem; sem viúvas?
- [ ] Botões confirmar/cancelar na ordem padrão?
- [ ] Todos os estados existem (carregando, vazio, erro, sucesso) e toda ação dá feedback?
- [ ] Erros em linguagem humana, perto do campo, dizendo como resolver?
- [ ] Cada ação tem o mesmo nome no fluxo todo, e telas vazias convidam a agir?
- [ ] Funciona no mobile e no teclado, com foco visível?
- [ ] Nenhum item da lista de anti-padrões (seção 7)?
- [ ] **Na dúvida se algo sobra, tirei?**

---

## 11. Formato do relatório (revisor de UX)

```
Tela: <nome>
[BLOQUEIA] <princípio> — <problema concreto> → <correção sugerida>
[IMPORTANTE] <princípio> — ...
[SUGESTÃO] <princípio> — ...
Veredito: APROVADO / REPROVADO
```

Cada apontamento cita o princípio violado e descreve o problema de forma técnica e verificável (seção 9). Qualquer item de anti-padrão (seção 7) ou checklist de UX (seção 6) não atendido é **BLOQUEIA**.
