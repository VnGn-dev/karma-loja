# Roteiro do projeto: Kar.ma Loja

Loja virtual própria para a **Kar.ma Clube** (artesanato e decoração), para
substituir a loja atual na Nuvemshop:
https://studiokarma.lojavirtualnuvem.com.br

A loja da Nuvemshop continua no ar até esta estar pronta e testada com uma
compra real.

---

## 1. O que o site atual tem (leitura de 26/10/2026)

### Páginas
| Página | O que tem |
|---|---|
| Início | faixa de aviso ("NOVO PRODUTO!!! PORTA_VELAS!!!"), 3 carrosséis, 3 produtos em destaque, 3 banners, link do Instagram |
| Produtos | lista com filtros e ordenação |
| Categoria | DECORAÇÃO |
| Produto | foto, preço, preço no Pix, frete por CEP |
| Contato | formulário: nome, e-mail, telefone, mensagem |
| Carrinho | itens, cupom, frete por CEP, pedido mínimo |
| Conta | entrar / criar conta |

### Produtos
| Produto | Preço | No Pix | Situação |
|---|---|---|---|
| PORTA_VELA BUTTERFLY | R$ 69,90 | R$ 66,41 | disponível |
| PORTA_VELA FLOR | R$ 39,00 | R$ 37,05 | disponível |
| PORTA_VELA (amarelo) | R$ 49,90 | R$ 47,41 | disponível |
| Chaveiro Lovito | R$ 45,00 | R$ 42,75 | esgotado |

### Regras de negócio que aparecem no site
- **Desconto no Pix: 5%** (ex.: 49,90 → 47,41).
- **Pedido mínimo: R$ 45,00**, sem contar o frete.
- Etiqueta **"Frete grátis"** em todos os produtos.
- Filtros: **cor** (Branco, Verde Claro), **marca** (Studio Kar.ma) e **faixa de preço**.
- Ordenação: preço (menor/maior), A-Z, Z-A, mais novos, mais antigos, mais vendidos.
- Aviso de cookies no primeiro acesso.

### Coisas para melhorar (anotar e conversar com ela)
- O link do Instagram está com o nome incompleto (`_________kar.ma`).
- Nomes com sublinhado (`PORTA_VELA`) e produto sem nome próprio ("PORTA_VELA" amarelo).
- Não existe página **Sobre**: o site não conta quem é a artista.
- Sem WhatsApp, telefone ou e-mail visível no contato.
- Campos de preço vazios aparecendo como "R$ 0,00" e "0% OFF".
- O banner aponta para outro endereço (`karmaclube.lojavirtualnuvem.com.br`).

---

## 2. O que vamos construir

### Tecnologias
| Parte | Ferramenta | Por quê |
|---|---|---|
| API e páginas | **FastAPI** (Python) | rápida, com documentação automática em `/docs` |
| Páginas HTML | **Jinja2** | o servidor monta o HTML; sem precisar aprender React agora |
| Banco de dados | **PostgreSQL** | o banco mais usado em vagas de back-end |
| Ligação Python ↔ banco | **SQLModel** | feito pelo mesmo autor do FastAPI, com pouco código |
| Pagamento | **Mercado Pago Checkout Pro** | o cliente paga na página do Mercado Pago; dados de cartão nunca passam pelo site |
| Frete | valor fixo/grátis → depois **Melhor Envio** | começar simples |
| Tudo rodando | **Docker Compose** | igual ao homelab |

### Tabelas do banco (primeira versão)
```
Categoria      id, nome, slug
Produto        id, nome, slug, descricao, preco, estoque, ativo,
               cor, frete_gratis, imagem, categoria_id, criado_em
Pedido         id, nome_cliente, email, telefone, endereco, cep,
               total, forma_pagamento, status, criado_em
ItemPedido     id, pedido_id, produto_id, quantidade, preco_unitario
Mensagem       id, nome, email, telefone, texto, criado_em
```
- O **preço no Pix** não é guardado: é calculado (`preco × 0,95`).
- O **slug** é o nome no endereço: "Porta-vela Flor" → `/produtos/porta-vela-flor`.
- **Esgotado** = `estoque == 0`.

---

## 3. Etapas

Cada etapa termina com um commit e algo funcionando.

### Etapa 1: Banco de dados e produtos na API
- [ ] Adicionar o PostgreSQL no `docker-compose.yml` (com volume e `.env`)
- [ ] Conectar a API ao banco com SQLModel
- [ ] Criar as tabelas `Categoria` e `Produto`
- [ ] Script que cadastra os 4 produtos atuais (o "seed")
- [ ] Rota `GET /api/produtos` (lista)
- [ ] Rota `GET /api/produtos/{slug}` (um produto, 404 se não existir)

**Pronto quando:** em `/docs`, a lista mostra os 4 produtos vindos do banco.

### Etapa 2: As páginas da loja
- [ ] Modelo base (`base.html`): cabeçalho, menu, rodapé, aviso de cookies
- [ ] Página inicial com produtos em destaque
- [ ] Página de produtos com filtros (cor, preço) e ordenação
- [ ] Página do produto (preço, preço no Pix, "esgotado")
- [ ] Página Sobre (texto da artista)
- [ ] CSS com as cores e a fonte da marca

**Pronto quando:** dá para navegar pela loja inteira no navegador.

### Etapa 3: Carrinho
- [ ] Adicionar, alterar quantidade e remover itens
- [ ] Guardar o carrinho na sessão do navegador
- [ ] Mostrar subtotal, desconto do Pix e total
- [ ] Bloquear a finalização abaixo do pedido mínimo (R$ 45,00)
- [ ] Não deixar comprar mais do que o estoque

**Pronto quando:** consigo montar um carrinho e as regras funcionam.

### Etapa 4: Painel da artista
- [ ] Login com senha (só ela entra)
- [ ] Cadastrar, editar e desativar produtos
- [ ] Enviar fotos dos produtos
- [ ] Ver os pedidos e mudar o status (pago, enviado, entregue)
- [ ] Ver as mensagens do formulário de contato

**Pronto quando:** ela cadastra um produto novo sozinha e ele aparece na loja.

### Etapa 5: Finalizar compra e pagamento (modo de teste)
- [ ] Formulário com dados do cliente e endereço
- [ ] Frete: grátis ou valor fixo (Melhor Envio fica para depois)
- [ ] Criar o pedido no banco com status "aguardando pagamento"
- [ ] Mandar o cliente para o Checkout Pro do Mercado Pago
- [ ] Rota de **webhook**: o Mercado Pago avisa quando o pagamento foi aprovado
- [ ] Baixar o estoque e marcar o pedido como "pago"
- [ ] E-mail de confirmação para o cliente e aviso para ela

**Pronto quando:** uma compra com cartão de teste chega como "pago" no painel.

### Etapa 6: Contato
- [ ] Formulário salva a mensagem no banco
- [ ] Envia um aviso por e-mail
- [ ] Campo oculto antispam

### Etapa 7: No ar de verdade
- [ ] Domínio próprio (Registro.br)
- [ ] Servidor na nuvem, com HTTPS
- [ ] Páginas de política de privacidade e de trocas (LGPD)
- [ ] Credenciais reais do Mercado Pago
- [ ] Compra real de teste
- [ ] Trocar a Nuvemshop pela loja nova

### Depois (melhorias)
- Frete calculado pelo CEP (Melhor Envio)
- Cupons de desconto
- Variações de produto (cores, modelos)
- Ordenação por "mais vendidos"
- Testes automáticos com pytest
- Resumo de vendas por e-mail

---

## 4. Para pedir à artista

- [ ] Lista completa dos produtos: nome, descrição, preço, estoque, cores
- [ ] Fotos dos produtos em boa qualidade
- [ ] Logotipo em alta resolução
- [ ] Cores e fonte da marca (se tiver)
- [ ] Texto da página **Sobre**
- [ ] Instagram correto, WhatsApp e e-mail de contato
- [ ] Confirmar regras: 5% no Pix? Frete sempre grátis? Pedido mínimo de R$ 45?
- [ ] Política de trocas e devoluções
- [ ] Conta no Mercado Pago (CPF ou CNPJ)
- [ ] Ela emite nota fiscal?
