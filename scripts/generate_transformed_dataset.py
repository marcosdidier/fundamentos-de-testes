from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_DATASET = ROOT / "data" / "original" / "original_dataset.csv"
TRANSFORMED_DATASET_V1 = ROOT / "data" / "transformed" / "transformed_dataset.csv"
TRANSFORMED_DATASET_V2 = ROOT / "data" / "transformed" / "transformed_dataset_v2.csv"

FIELDNAMES = [
    "case_id",
    "original_input_id",
    "transformation_type",
    "original_text",
    "transformed_text",
    "expected_label",
    "manual_review_status",
    "manual_review_notes",
]

PARAPHRASE_PREFIXES_V1 = {
    "refund_request": [
        "Preciso que a loja providencie a devolucao do valor, pois ",
        "Estou pedindo reembolso porque ",
        "Quero receber de volta o dinheiro pago, ja que ",
    ],
    "cancel_order": [
        "Preciso encerrar a compra, pois ",
        "Gostaria que o pedido fosse cancelado, ja que ",
        "Nao quero seguir com a compra, porque ",
    ],
    "delivery_problem": [
        "Estou com um problem de entrega: ",
        "Preciso de ajuda com o recebimento do pedido, pois ",
        "Ha uma falha no envio do meu pedido: ",
    ],
    "payment_issue": [
        "Estou enfrentando um problema no pagamento, pois ",
        "Preciso de suporte com a cobranca porque ",
        "A compra teve uma falha relacionada ao pagamento: ",
    ],
    "product_information": [
        "Quero confirmar uma informacao sobre o produto: ",
        "Tenho uma duvida sobre as caracteristicas do item: ",
        "Preciso saber um detalhe antes de comprar: ",
    ],
    "account_support": [
        "Preciso de ajuda com minha conta, pois ",
        "Estou com dificuldade no cadastro ou acesso: ",
        "Quero suporte para resolver um problema de conta: ",
    ],
    "other": [
        "Minha mensagem para a loja e a seguinte: ",
        "Entro em contato apenas para dizer que ",
        "Gostaria de registrar esta mensagem: ",
    ],
}

PARAPHRASES_V2 = {
    # REFUND REQUEST
    "orig_refund_request_001": [
        "Como o produto que chegou veio com defeito, exijo a devolução do meu dinheiro.",
        "Solicito o estorno do valor pago, pois recebi o item danificado.",
        "O artigo entregue está quebrado e eu gostaria de reaver o pagamento."
    ],
    "orig_refund_request_002": [
        "Peço que façam o reembolso do valor referente à compra que realizei.",
        "Quero pedir a devolução do dinheiro pago nesta transação.",
        "Por favor, deem início ao processo de estorno do meu pedido."
    ],
    "orig_refund_request_003": [
        "Fiz o pedido ontem, mas agora preciso do estorno do pagamento.",
        "Realizei uma compra ontem e gostaria de solicitar a devolução do dinheiro.",
        "Preciso recuperar o dinheiro da compra que efetuei no dia de ontem."
    ],
    "orig_refund_request_004": [
        "Vocês poderiam estornar o valor cobrado por este pedido?",
        "Existe a possibilidade de devolverem o montante que paguei nesta compra?",
        "Gostaria de saber se posso ter meu dinheiro de volta por este item."
    ],
    "orig_refund_request_005": [
        "Entregaram o produto incorreto e por isso exijo o reembolso do valor.",
        "Como o artigo que chegou não foi o que pedi, quero meu dinheiro de volta.",
        "Solicito o estorno do pagamento, pois o produto enviado veio errado."
    ],
    "orig_refund_request_006": [
        "Gostaria de abrir um chamado para reaver o dinheiro pago.",
        "Onde posso solicitar a devolução do valor da minha compra?",
        "Preciso dar entrada no pedido de reembolso do meu pagamento."
    ],
    "orig_refund_request_007": [
        "O produto não atendeu às minhas expectativas e desejo o dinheiro de volta.",
        "Como não gostei da compra, solicito o estorno do pagamento.",
        "Não me agradei com o item recebido e quero a restituição do valor pago."
    ],
    "orig_refund_request_008": [
        "Qual é o procedimento para solicitar o estorno do valor deste item?",
        "Como posso obter a devolução do dinheiro pago por este produto?",
        "Poderiam me orientar sobre como pedir o reembolso dessa mercadoria?"
    ],
    "orig_refund_request_009": [
        "Minha encomenda veio danificada e quero a devolução imediata do valor.",
        "Solicito reembolso total, pois o produto chegou quebrado na minha casa.",
        "O item entregue está avariado e gostaria de ter meu dinheiro de volta."
    ],
    "orig_refund_request_010": [
        "Quero requerer a restituição do dinheiro da minha compra mais recente.",
        "Por favor, providenciem o estorno do pagamento do meu último pedido.",
        "Solicito a devolução do montante cobrado na transação anterior."
    ],

    # CANCEL ORDER
    "orig_cancel_order_001": [
        "Desejo efetuar o cancelamento da minha compra.",
        "Por favor, cancelem o pedido que realizei.",
        "Gostaria de solicitar a anulação da minha encomenda."
    ],
    "orig_cancel_order_002": [
        "Quero cancelar o pedido que fiz há poucos instantes.",
        "Acabei de realizar uma compra, mas mudei de ideia e quero cancelá-la.",
        "Por favor, suspendam a transação que acabei de concluir."
    ],
    "orig_cancel_order_003": [
        "Consigo cancelar a minha compra a essa altura?",
        "Gostaria de saber se o meu pedido já foi enviado ou se ainda posso cancelar.",
        "Será que é possível solicitar a suspensão do pedido agora?"
    ],
    "orig_cancel_order_004": [
        "Peço que cancelem meu pedido antes que a transportadora o recolha.",
        "Favor suspender a compra antes de despacharem o produto.",
        "Gostaria de cancelar a encomenda antes que seja feito o envio."
    ],
    "orig_cancel_order_005": [
        "Quero desistir da compra que realizei na data de hoje.",
        "Solicito o cancelamento da encomenda efetuada hoje mais cedo.",
        "Preciso anular a transação que fiz no dia de hoje."
    ],
    "orig_cancel_order_006": [
        "Perdi o interesse no item e gostaria de suspender a compra.",
        "Decidi que não vou ficar com o produto, então cancelem o pedido por favor.",
        "Como não pretendo mais ficar com a mercadoria, solicito a anulação da ordem."
    ],
    "orig_cancel_order_007": [
        "Qual é o procedimento para suspender o envio antes da entrega da mercadoria?",
        "Como posso cancelar o pedido antes que ele chegue ao meu endereço?",
        "Gostaria de barrar a entrega e cancelar a compra, o que devo fazer?"
    ],
    "orig_cancel_order_008": [
        "Por favor, façam a suspensão da compra de código 4587.",
        "Desejo anular o pedido número 4587.",
        "Solicito o cancelamento imediato da encomenda 4587."
    ],
    "orig_cancel_order_009": [
        "Efetuei o pedido acidentalmente e gostaria de cancelá-lo.",
        "Comprei o item errado sem querer e preciso suspender a transação.",
        "Por engano acabei fazendo uma compra e agora peço o cancelamento."
    ],
    "orig_cancel_order_010": [
        "Gostaria de pedir a anulação do meu pedido mais recente.",
        "Favor realizar o cancelamento da última compra que registrei.",
        "Desejo cancelar o pedido efetuado por último."
    ],

    # DELIVERY PROBLEM
    "orig_delivery_problem_001": [
        "O produto que comprei ainda não foi entregue.",
        "A encomenda que estou esperando ainda não chegou no meu endereço.",
        "Continuo no aguardo da entrega do meu pedido."
    ],
    "orig_delivery_problem_002": [
        "Faz dias que o código de rastreamento da minha compra não mostra movimentação.",
        "O status de envio do produto está paralisado há bastante tempo.",
        "Não vejo atualizações no rastreio da minha encomenda já faz alguns dias."
    ],
    "orig_delivery_problem_003": [
        "No sistema diz que o pedido foi entregue, porém não recebi a mercadoria.",
        "Consta como entregue o produto, mas a entrega não foi realizada para mim.",
        "O rastreamento aponta que a encomenda chegou, mas meu pacote não está aqui."
    ],
    "orig_delivery_problem_004": [
        "Gostaria de uma explicação sobre o atraso no envio do meu pedido.",
        "O prazo estourou e necessito de informações sobre o paradeiro da minha entrega.",
        "Preciso de esclarecimentos porque o produto está atrasado."
    ],
    "orig_delivery_problem_005": [
        "A transportadora alegou endereço não localizado e a encomenda retornou.",
        "O pacote está voltando para a loja porque não acharam a minha residência.",
        "Houve insucesso na entrega por falta de localização do endereço, e o pedido foi devolvido."
    ],
    "orig_delivery_problem_006": [
        "A encomenda veio incompleta, faltando alguns dos produtos comprados.",
        "Só chegou uma fração do meu pedido, o resto está faltando.",
        "Abri o pacote e notei que não vieram todos os itens que eu pedi."
    ],
    "orig_delivery_problem_007": [
        "Desejo saber o motivo de o meu pedido estar demorando para ser entregue.",
        "Poderiam me atualizar sobre a situação da entrega que está em atraso?",
        "Solicito esclarecimentos a respeito do atraso no frete do meu produto."
    ],
    "orig_delivery_problem_008": [
        "A encomenda parece estar retida ou estacionada na empresa de logística.",
        "O rastreamento indica que o item não sai da unidade da transportadora.",
        "Meu pedido travou no centro de distribuição da transportadora."
    ],
    "orig_delivery_problem_009": [
        "O prazo final estimado já venceu e não recebi novos avisos sobre a encomenda.",
        "A data de entrega já expirou e sigo sem informações sobre o meu pedido.",
        "Já passou do dia previsto para o recebimento e não há novidades no sistema."
    ],
    "orig_delivery_problem_010": [
        "Aparece que o produto está em rota de entrega, mas até o momento não recebi.",
        "A encomenda saiu para entrega hoje de manhã, mas ainda não chegou no meu endereço.",
        "Consta que o motorista saiu para entregar, porém a mercadoria não chegou."
    ],

    # PAYMENT ISSUE
    "orig_payment_issue_001": [
        "A transação financeira da minha compra não foi aprovada pelo sistema.",
        "Minha tentativa de pagamento deu como negada.",
        "O sistema rejeitou a forma de pagamento que utilizei."
    ],
    "orig_payment_issue_002": [
        "Houve um débito duplo na minha fatura ao tentar passar o cartão.",
        "Paguei no cartão de crédito, mas a transação foi cobrada duas vezes.",
        "Identifiquei uma cobrança repetida do mesmo valor no meu extrato do cartão."
    ],
    "orig_payment_issue_003": [
        "Não consegui efetuar o pagamento do boleto dentro do prazo de validade.",
        "O prazo do boleto expirou antes que eu pudesse pagar o pedido.",
        "Perdi a data de vencimento do boleto bancário da minha compra."
    ],
    "orig_payment_issue_004": [
        "Enviei o dinheiro por PIX faz tempo, mas o sistema ainda não reconheceu o pagamento.",
        "Já transferi via PIX, contudo a compra permanece aguardando confirmação.",
        "O PIX da minha compra já foi concluído, mas o status do pedido não atualizou."
    ],
    "orig_payment_issue_005": [
        "O site recusa a aprovação do meu cartão de crédito ao tentar encerrar o pedido.",
        "Toda vez que tento pagar com o cartão, ocorre um erro de rejeição no checkout.",
        "Minha compra não é concluída porque o portal não aceita os dados do meu cartão."
    ],
    "orig_payment_issue_006": [
        "O valor cobrado final está divergindo do total exibido na tela de compras.",
        "O sistema me cobrou uma quantia diferente da que constava nos produtos selecionados.",
        "O preço cobrado na transação está maior do que o preço original do carrinho."
    ],
    "orig_payment_issue_007": [
        "Gostaria de suporte pois a aprovação do meu pagamento está travada como pendente.",
        "O status do pagamento da minha compra não muda de pendente, o que devo fazer?",
        "O processamento do meu pagamento parou e preciso de auxílio para resolver."
    ],
    "orig_payment_issue_008": [
        "A fatura do meu cartão já acusa a cobrança, mas o pedido sumiu do meu perfil no site.",
        "Houve o débito no meu cartão de crédito, porém não há registro da compra na minha conta.",
        "Fui cobrado pela compra, mas o pedido não foi listado na minha área de cliente."
    ],
    "orig_payment_issue_009": [
        "Estou tentando pagar a fatura digitando o código de barras, mas dá erro de boleto inválido.",
        "A linha digitável do boleto gerada pelo site não é reconhecida pelo meu banco.",
        "O código para pagamento do boleto está dando erro na hora de finalizar."
    ],
    "orig_payment_issue_010": [
        "Ocorreu uma falha sistêmica durante a etapa de processamento da transação financeira.",
        "A transação deu erro logo após eu digitar os dados de pagamento.",
        "O sistema gerou uma mensagem de erro ao processar o pagamento da compra."
    ],

    # PRODUCT INFORMATION
    "orig_product_information_001": [
        "Qual é o tempo e as condições de garantia oferecidos para este item?",
        "Gostaria de saber se o produto vem com garantia de fábrica.",
        "Existe cobertura de garantia para este artigo?"
    ],
    "orig_product_information_002": [
        "Vocês possuem estoque deste modelo de smartphone na opção de cor preta?",
        "Tem o celular preto disponível para pronta entrega?",
        "O aparelho em questão conta com a variação na cor preta no momento?"
    ],
    "orig_product_information_003": [
        "Poderiam me informar as dimensões detalhadas (altura, largura e profundidade) desta mesa?",
        "Quais são as medidas de comprimento e largura desse móvel?",
        "Preciso saber o tamanho preciso desse modelo de mesa."
    ],
    "orig_product_information_004": [
        "O carregador acompanha o computador na embalagem original?",
        "Gostaria de confirmar se a fonte de alimentação está inclusa na compra do laptop.",
        "Esse modelo de notebook já vem com o cabo de carregar?"
    ],
    "orig_product_information_005": [
        "Existe algum guia de tamanhos disponível para esta peça de vestuário?",
        "Onde encontro a tabela com as dimensões dessa roupa em centímetros?",
        "Essa peça de roupa possui tabela de medidas para referência?"
    ],
    "orig_product_information_006": [
        "Gostaria de esclarecer se o item à venda é de marca oficial ou se é uma réplica/paralelo.",
        "Trata-se de uma mercadoria legítima da fabricante ou de um modelo genérico?",
        "Esse artigo anunciado é original ou trata-se de um produto compatível secundário?"
    ],
    "orig_product_information_007": [
        "Quando vocês pretendem restabelecer o estoque deste produto que está indisponível?",
        "Há alguma data estimada para que o artigo volte a ficar à venda no site?",
        "Este produto esgotado voltará ao catálogo em breve?"
    ],
    "orig_product_information_008": [
        "Poderiam me passar a ficha técnica completa (resolução, taxa de atualização, entradas) desta tela?",
        "Quais as principais características de hardware e especificações do monitor?",
        "Quero ver os detalhes técnicos de fabricação desse monitor."
    ],
    "orig_product_information_009": [
        "O fone de ouvido é compatível com sistemas operacionais Android?",
        "Consigo parear e usar todos os recursos deste fone em um smartphone Android?",
        "Esse modelo de fone de ouvido tem suporte para celulares da linha Android?"
    ],
    "orig_product_information_010": [
        "Qual é a capacidade máxima de peso em kg que este assento consegue aguentar com segurança?",
        "Essa cadeira suporta peso de até quantos quilogramas?",
        "Gostaria de saber o limite de carga recomendado para essa cadeira."
    ],

    # ACCOUNT SUPPORT
    "orig_account_support_001": [
        "Estou tendo problemas para fazer login na minha área pessoal.",
        "Não estou conseguindo entrar no meu perfil cadastrado no site.",
        "Minhas credenciais não me deixam acessar minha conta."
    ],
    "orig_account_support_002": [
        "Não me recordo da senha cadastrada e gostaria de redefini-la para voltar a entrar no sistema.",
        "Preciso restaurar minha conta pois esqueci a palavra-passe de acesso.",
        "Como faço para trocar a senha que perdi e recuperar meu perfil?"
    ],
    "orig_account_support_003": [
        "Mesmo digitando os dados de login e senha corretos, o sistema recusa a entrada.",
        "Tenho certeza de que a senha está certa, mas o painel não abre.",
        "Ocorre falha na autenticação da conta, embora o usuário e senha digitados estejam exatos."
    ],
    "orig_account_support_004": [
        "Como proceder para atualizar o endereço de correio eletrônico vinculado ao meu perfil?",
        "Desejo modificar o endereço de e-mail que está registrado no meu login.",
        "Gostaria de trocar o e-mail de cadastro da minha conta pessoal."
    ],
    "orig_account_support_005": [
        "Percebi que preenchi o número do meu documento de CPF de forma incorreta e quero alterá-lo.",
        "Gostaria de retificar o CPF informado no meu formulário de registro.",
        "Meu cadastro possui um erro no número de CPF e preciso realizar essa correção cadastral."
    ],
    "orig_account_support_006": [
        "Estou tentando trocar a senha, mas a mensagem com o link ou token de verificação não chega na caixa de entrada.",
        "Solicitei o código de verificação para alteração de senha, mas ele não foi enviado.",
        "O e-mail/SMS com o código de recuperação de login está demorando para chegar ou não veio."
    ],
    "orig_account_support_007": [
        "Meu perfil de usuário foi suspenso/bloqueado sem qualquer aviso ou justificativa aparente.",
        "Gostaria de entender por que o meu acesso à conta foi bloqueado de repente.",
        "Fui impedido de logar por conta de um bloqueio e gostaria de saber as razões."
    ],
    "orig_account_support_008": [
        "Gostaria de efetuar modificações nas minhas informações pessoais salvas no site.",
        "Como faço para alterar meus dados de contato e endereço no banco de dados?",
        "Preciso modificar algumas informações do meu perfil cadastrado."
    ],
    "orig_account_support_009": [
        "Toda vez que faço o login pelo app, a sessão cai e sou deslogado na mesma hora.",
        "O aplicativo fecha meu login automaticamente logo após eu conseguir acessar.",
        "Estou enfrentando um bug onde o app desloga sozinho logo depois da tela inicial."
    ],
    "orig_account_support_010": [
        "O formulário de registro está apresentando falhas e não consigo concluir meu cadastro no portal.",
        "Estou tentando me cadastrar no site como novo usuário, mas a criação de conta dá erro.",
        "Não é possível finalizar a inscrição de um perfil no site."
    ],

    # OTHER
    "orig_other_001": [
        "Agradeço muito pelo suporte prestado pela equipe de vocês.",
        "Gostaria de expressar meu agradecimento pela ajuda recebida hoje.",
        "Muito obrigado por terem sanado as minhas dúvidas."
    ],
    "orig_other_002": [
        "Gostaria de me inscrever para receber a newsletter e ofertas exclusivas no meu e-mail.",
        "Como faço para assinar os boletins informativos de descontos de vocês?",
        "Por favor, me incluam na lista de divulgação de novidades e liquidações."
    ],
    "orig_other_003": [
        "Fiquei impressionado com a agilidade com que o time de atendimento solucionou o meu caso.",
        "Parabenizo a empresa pelo tempo de resposta extremamente curto no chat.",
        "Excelente trabalho na rapidez para me dar uma resposta."
    ],
    "orig_other_004": [
        "Qual é o caminho para ler o documento que rege os termos de privacidade de dados do portal?",
        "Poderiam me apontar a página que detalha o tratamento e privacidade de dados pessoais?",
        "Em qual seção do site posso consultar a política de segurança e privacidade?"
    ],
    "orig_other_005": [
        "Tenho uma recomendação de melhoria de usabilidade para propor para a equipe de desenvolvimento do app.",
        "Como posso enviar um feedback com ideias para aperfeiçoar o app?",
        "Gostaria de compartilhar uma sugestão de recurso novo para o aplicativo móvel."
    ],
    "orig_other_006": [
        "A plataforma oferece soluções ou atendimento dedicado para estabelecimentos comerciais parceiros?",
        "Existe algum canal focado em dar suporte ou fazer negócios com lojas afiliadas?",
        "Gostaria de saber se vocês trabalham prestando serviço a empresas parceiras."
    ],
    "orig_other_007": [
        "Qual é o canal direto ou e-mail de contato do setor comercial de vendas de vocês?",
        "Desejo entrar em contato com o departamento de novos negócios e parcerias comerciais.",
        "Como faço para conseguir atendimento com a equipe de vendas corporativas."
    ],
    "orig_other_008": [
        "Esta mensagem é somente para testar o funcionamento do sistema de atendimento online.",
        "Podem desconsiderar este contato, estou apenas fazendo um teste do canal de conversa.",
        "Estou avaliando o chat para ver como a ferramenta se comporta."
    ],
    "orig_other_009": [
        "Em quais faixas de horário e dias da semana a central de atendimento fica disponível?",
        "Poderiam me informar o período de funcionamento para suporte ao cliente?",
        "Qual o expediente da empresa para contato direto com o suporte?"
    ],
    "orig_other_010": [
        "Olá, bom dia! Gostaria de falar com algum atendente do suporte online.",
        "Olá, tem algum consultor disponível para atendimento neste momento?",
        "Bom dia. Consigo ser atendido por alguém agora?"
    ],
}


def normalize_sentence(text: str) -> str:
    normalized = text.strip()
    while normalized.endswith((".", "?", "!")):
        normalized = normalized[:-1].strip()
    if not normalized:
        return text.strip()
    return normalized[0].lower() + normalized[1:]


def punctuation_variant(text: str) -> str:
    base = normalize_sentence(text)
    if text.strip().endswith("?"):
        return f"{base}?"
    return f"{base}..."


def capitalization_variant(text: str, row_index: int) -> str:
    if row_index % 3 == 0:
        return text.upper()
    if row_index % 3 == 1:
        return text.lower()
    words = text.split()
    return " ".join(word.upper() if index % 2 == 0 else word.lower() for index, word in enumerate(words))


def build_rows_v1() -> list[dict[str, str]]:
    with ORIGINAL_DATASET.open(newline="", encoding="utf-8") as source:
        original_rows = list(csv.DictReader(source))

    transformed_rows: list[dict[str, str]] = []

    for index, original in enumerate(original_rows):
        original_input_id = original["original_input_id"]
        expected_label = original["expected_label"]
        original_text = original["text"]

        base = normalize_sentence(original_text)
        prefixes = PARAPHRASE_PREFIXES_V1.get(expected_label, [])
        
        for paraphrase_index, prefix in enumerate(prefixes, start=1):
            transformed_rows.append(
                {
                    "case_id": f"{original_input_id}_paraphrase_{paraphrase_index:02d}",
                    "original_input_id": original_input_id,
                    "transformation_type": "paraphrase",
                    "original_text": original_text,
                    "transformed_text": f"{prefix}{base}.",
                    "expected_label": expected_label,
                    "manual_review_status": "pending",
                    "manual_review_notes": "",
                }
            )

        transformed_rows.append(
            {
                "case_id": f"{original_input_id}_punctuation_01",
                "original_input_id": original_input_id,
                "transformation_type": "punctuation",
                "original_text": original_text,
                "transformed_text": punctuation_variant(original_text),
                "expected_label": expected_label,
                "manual_review_status": "pending",
                "manual_review_notes": "",
            }
        )

        transformed_rows.append(
            {
                "case_id": f"{original_input_id}_capitalization_01",
                "original_input_id": original_input_id,
                "transformation_type": "capitalization",
                "original_text": original_text,
                "transformed_text": capitalization_variant(original_text, index),
                "expected_label": expected_label,
                "manual_review_status": "pending",
                "manual_review_notes": "",
            }
        )

    return transformed_rows


def build_rows_v2() -> list[dict[str, str]]:
    with ORIGINAL_DATASET.open(newline="", encoding="utf-8") as source:
        original_rows = list(csv.DictReader(source))

    transformed_rows: list[dict[str, str]] = []

    for index, original in enumerate(original_rows):
        original_input_id = original["original_input_id"]
        expected_label = original["expected_label"]
        original_text = original["text"]

        paraphrases = PARAPHRASES_V2.get(original_input_id, [])
        for paraphrase_index, transformed_text in enumerate(paraphrases, start=1):
            transformed_rows.append(
                {
                    "case_id": f"{original_input_id}_paraphrase_{paraphrase_index:02d}",
                    "original_input_id": original_input_id,
                    "transformation_type": "paraphrase",
                    "original_text": original_text,
                    "transformed_text": transformed_text,
                    "expected_label": expected_label,
                    "manual_review_status": "pending",
                    "manual_review_notes": "",
                }
            )

        transformed_rows.append(
            {
                "case_id": f"{original_input_id}_punctuation_01",
                "original_input_id": original_input_id,
                "transformation_type": "punctuation",
                "original_text": original_text,
                "transformed_text": punctuation_variant(original_text),
                "expected_label": expected_label,
                "manual_review_status": "pending",
                "manual_review_notes": "",
            }
        )

        transformed_rows.append(
            {
                "case_id": f"{original_input_id}_capitalization_01",
                "original_input_id": original_input_id,
                "transformation_type": "capitalization",
                "original_text": original_text,
                "transformed_text": capitalization_variant(original_text, index),
                "expected_label": expected_label,
                "manual_review_status": "pending",
                "manual_review_notes": "",
            }
        )

    return transformed_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate transformed datasets (v1 and/or v2).")
    parser.add_argument(
        "--version",
        choices=("v1", "v2", "all"),
        default="all",
        help="Which version of the transformed dataset to generate.",
    )
    return parser.parse_args()


def write_dataset(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote={path} (rows={len(rows)})")


def main() -> None:
    args = parse_args()
    
    if args.version in ("v1", "all"):
        rows_v1 = build_rows_v1()
        write_dataset(rows_v1, TRANSFORMED_DATASET_V1)

    if args.version in ("v2", "all"):
        rows_v2 = build_rows_v2()
        write_dataset(rows_v2, TRANSFORMED_DATASET_V2)


if __name__ == "__main__":
    main()
