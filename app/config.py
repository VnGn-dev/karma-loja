"""Informações da loja usadas nas páginas.

Mude aqui e o site inteiro atualiza: nome, contatos, regras de venda.
"""

from decimal import Decimal

LOJA = {
    "nome": "Kar.ma Clube",
    "slogan": "Artesanato e decoração feitos à mão",
    # Logo atual, hospedado na Nuvemshop. Depois, troque por um arquivo em
    # app/static/img/ (ex.: "/static/img/logo.png").
    "logo": (
        "https://dcdn-us.mitiendanube.com/stores/006/804/689/themes/common/"
        "logo-8711127800104245889-1793064156-685e04dbf5f68a485823ebee2be6de68"
        "1793064156-640-0.webp"
    ),
    # O endereço do Instagram no site atual está incompleto ("_________kar.ma").
    # Coloque aqui o certo, ex.: "https://instagram.com/nome.da.conta".
    # Enquanto estiver vazio (None), o link não aparece.
    "instagram": None,
    "email": None,  # ex.: "contato@karmaclube.com.br"
    "whatsapp": None,  # só números, com DDD e país, ex.: "5547999999999"
    "aviso": "NOVO PRODUTO · PORTA-VELAS",
}

# Regras de venda (iguais às da loja atual)
PEDIDO_MINIMO = Decimal("45.00")
DESCONTO_PIX = 5  # em %, só para mostrar nas páginas
