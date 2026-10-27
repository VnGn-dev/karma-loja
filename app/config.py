"""Informações da loja usadas nas páginas.

Mude aqui e o site inteiro atualiza: nome, contatos, imagens da página
inicial e regras de venda.
"""

from decimal import Decimal

# Imagens do tema atual, hospedadas na Nuvemshop. Antes de desligar a loja
# antiga, baixe e coloque em app/static/img/ (ex.: "/static/img/logo.webp").
_CDN = "https://dcdn-us.mitiendanube.com/stores/006/804/689/themes/"

LOJA = {
    "nome": "Kar.ma Clube",
    "logo": _CDN + "common/logo-8711127800104245889-1793064156-"
                   "685e04dbf5f68a485823ebee2be6de681793064156-640-0.webp",
    # Texto da faixa que fica rolando no topo do site
    "aviso": "NOVO PRODUTO!!!!!! °° PORTA_VELAS!!!!!!",
    "email": "studiodebka@gmail.com",
    # O endereço do Instagram no site atual está incompleto ("_________kar.ma").
    # Coloque aqui o certo, ex.: "https://instagram.com/nome.da.conta".
    # Enquanto estiver vazio (None), o ícone não aparece.
    "instagram": None,
    "whatsapp": None,  # só números, com país e DDD, ex.: "5547999999999"
}

# Carrossel grande da página inicial (na ordem em que aparecem)
CARROSSEL = [
    _CDN + "morelia/2-slide-1793065841575-8122919289-"
           "8c11a9ffc6553aa625850cd3ff30342d1793065841-1920-1920.webp",
    _CDN + "morelia/2-slide-1793058973992-365446131-"
           "d6789353a0264fbd2779135b0f91b4ba1793058974-1920-1920.webp",
]

# Os 3 banners quadrados do fim da página inicial
BANNERS = [
    _CDN + "morelia/2-slide-1793057797856-2349982657-"
           "90520503a7e90fc045bedaa57231c3311793057799-1920-1920.webp",
    _CDN + "morelia/2-slide-1793057797856-4625195699-"
           "ed97441c6c4c947c53c0a71d41f9fb8f1793057799-1920-1920.webp",
    _CDN + "morelia/2-slide-1793057797856-6519550141-"
           "b126b1405e0b64b973b46f26076cce111793057799-1920-1920.webp",
]

# Regras de venda (iguais às da loja atual)
PEDIDO_MINIMO = Decimal("45.00")
DESCONTO_PIX = 5  # em %, só para mostrar nas páginas
