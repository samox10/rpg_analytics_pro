import flet as ft
from database import db_core

def formatar_moeda(valor):
    if valor.is_integer(): return f"{int(valor):,}".replace(",", ".")
    else:
        partes = f"{valor:,.2f}".split(".")
        return f"{partes[0].replace(',', '.')},{partes[1]}"

def limpar_moeda(texto):
    return float(texto.replace(".", "").replace(",", "."))

def view(page: ft.Page):
    # ==========================================
    # GERENCIAMENTO DE ESTADO DAS ABAS
    # ==========================================
    estado = {
        "item_edit_id": None,
        "cad_hunt_itens": set(), # IDs dos itens selecionados no Cadastro de Hunt
        "edit_hunt_id": None,
        "edit_hunt_itens": set() # IDs dos itens selecionados na Edição de Hunt
    }

    # ==========================================
    # COMPONENTES VISUAIS REUTILIZÁVEIS
    # ==========================================
    def criar_card_item_transfer(item_id, item_nome, item_foto, acao, is_add):
        """Cria os cards com botão + ou - para as listas duplas."""
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Image(src=f"items/{item_foto}", width=24, height=24, fit="contain"), bgcolor="#1E1F22", padding=4, border_radius=6),
                ft.Text(item_nome, color="white", size=14, expand=True, weight=ft.FontWeight.BOLD),
                ft.Icon(
                    ft.Icons.ADD_CIRCLE if is_add else ft.Icons.REMOVE_CIRCLE, 
                    color=ft.Colors.GREEN_400 if is_add else ft.Colors.RED_400,
                    size=20
                )
            ]),
            bgcolor="#2B2D31" if is_add else "#404249",
            padding=8,
            border_radius=8,
            data=item_id,
            on_click=acao,
            ink=True
        )

    # ==========================================
    # ABA 1: REGISTRO DE ITENS
    # ==========================================
    nome_input = ft.TextField(label="Nome do Item", bgcolor="#1E1F22", border_color="#5865F2", color="white")
    foto_input = ft.TextField(label="Nome do Arquivo (ex: item.png)", bgcolor="#1E1F22", border_color="#5865F2", color="white")
    valor_input = ft.TextField(label="Valor NPC", bgcolor="#1E1F22", border_color="#5865F2", color="white", keyboard_type=ft.KeyboardType.NUMBER)

    def salvar_item_novo(e):
        if not nome_input.value or not foto_input.value or not valor_input.value:
            page.overlay.append(ft.SnackBar(ft.Text("Preencha todos os campos!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()
            return
        try:
            sucesso = db_core.adicionar_item(nome_input.value, foto_input.value, limpar_moeda(valor_input.value))
            if sucesso:
                page.overlay.append(ft.SnackBar(ft.Text("Item salvo!"), open=True, bgcolor="#23A559"))
                nome_input.value = foto_input.value = valor_input.value = ""
                carregar_dados_globais() 
            else:
                page.overlay.append(ft.SnackBar(ft.Text("Item já existe!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()
        except ValueError:
            page.overlay.append(ft.SnackBar(ft.Text("Número inválido!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()

    aba_itens = ft.Column([nome_input, foto_input, valor_input, ft.ElevatedButton("Registrar Item", bgcolor="#23A559", color="white", height=50, on_click=salvar_item_novo)], spacing=20)

    # ==========================================
    # ABA 2: REGISTRO DE HUNTS (DUAS COLUNAS)
    # ==========================================
    nome_hunt_input = ft.TextField(label="Nome da Hunt", bgcolor="#1E1F22", border_color="#5865F2", color="white")
    shiny_hunt_input = ft.TextField(label="Shiny (Opcional)", bgcolor="#1E1F22", border_color="#5865F2", color="white", expand=True)
    angry_hunt_input = ft.TextField(label="Angry (Opcional)", bgcolor="#1E1F22", border_color="#5865F2", color="white", expand=True)
    
    busca_cad_hunt = ft.TextField(label="🔍 Buscar item para adicionar...", bgcolor="#1E1F22", border_color="#23A559", color="white", height=45)
    lista_disp_cad_hunt = ft.ListView(height=250, spacing=8)
    lista_sel_cad_hunt = ft.ListView(height=250, spacing=8)

    def atualizar_listas_cad_hunt(e=None):
        termo = busca_cad_hunt.value.lower() if busca_cad_hunt.value else ""
        lista_disp_cad_hunt.controls.clear()
        lista_sel_cad_hunt.controls.clear()
        
        for item_id, item_nome, item_foto in db_core.get_todos_itens():
            if item_id in estado["cad_hunt_itens"]:
                # Vai para a lista da DIREITA (Selecionados)
                lista_sel_cad_hunt.controls.append(criar_card_item_transfer(item_id, item_nome, item_foto, remover_item_cad_hunt, False))
            else:
                # Vai para a lista da ESQUERDA (Disponíveis), respeitando o filtro
                if termo in item_nome.lower():
                    lista_disp_cad_hunt.controls.append(criar_card_item_transfer(item_id, item_nome, item_foto, add_item_cad_hunt, True))
        page.update()

    def add_item_cad_hunt(e):
        estado["cad_hunt_itens"].add(e.control.data)
        atualizar_listas_cad_hunt()

    def remover_item_cad_hunt(e):
        estado["cad_hunt_itens"].discard(e.control.data)
        atualizar_listas_cad_hunt()

    busca_cad_hunt.on_change = atualizar_listas_cad_hunt

    def salvar_hunt(e):
        if not nome_hunt_input.value:
            page.overlay.append(ft.SnackBar(ft.Text("Preencha o nome da Hunt!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()
            return
        if not estado["cad_hunt_itens"]:
            page.overlay.append(ft.SnackBar(ft.Text("Adicione pelo menos 1 item na Hunt!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()
            return
        
        db_core.adicionar_hunt(nome_hunt_input.value, shiny_hunt_input.value, angry_hunt_input.value, list(estado["cad_hunt_itens"]))
        page.overlay.append(ft.SnackBar(ft.Text("Hunt salva!"), open=True, bgcolor="#23A559"))
        
        nome_hunt_input.value = shiny_hunt_input.value = angry_hunt_input.value = busca_cad_hunt.value = ""
        estado["cad_hunt_itens"].clear()
        carregar_dados_globais() 
        page.update()

    aba_hunts = ft.Column([
        nome_hunt_input,
        ft.Row([shiny_hunt_input, angry_hunt_input], spacing=15),
        ft.Divider(color="#1E1F22"),
        ft.Row([
            # Coluna Esquerda: Itens Disponíveis
            ft.Column([
                ft.Text("Itens Disponíveis", color="#23A559", weight=ft.FontWeight.BOLD),
                busca_cad_hunt,
                ft.Container(content=lista_disp_cad_hunt, padding=8, border_radius=8, bgcolor="#111214")
            ], expand=True),
            # Coluna Direita: Itens Selecionados
            ft.Column([
                ft.Text(f"Itens na Hunt", color="#5865F2", weight=ft.FontWeight.BOLD),
                ft.Container(height=45), # Espaçador para alinhar com a busca
                ft.Container(content=lista_sel_cad_hunt, padding=8, border_radius=8, bgcolor="#111214")
            ], expand=True),
        ], spacing=20, alignment=ft.MainAxisAlignment.START),
        ft.ElevatedButton("Registrar Hunt", bgcolor="#23A559", color="white", height=50, on_click=salvar_hunt)
    ], spacing=15)

    # ==========================================
    # ABA 3: EDIÇÃO DE ITENS
    # ==========================================
    busca_edit_item = ft.TextField(label="🔍 Pesquisar item pelo nome...", bgcolor="#1E1F22", border_color="#23A559", color="white")
    lista_edit_itens = ft.ListView(height=180, spacing=8)
    
    edit_nome_input = ft.TextField(label="Nome", bgcolor="#1E1F22", border_color="#5865F2", color="white", disabled=True)
    edit_foto_input = ft.TextField(label="Foto", bgcolor="#1E1F22", border_color="#5865F2", color="white", disabled=True)
    edit_valor_input = ft.TextField(label="Valor NPC", bgcolor="#1E1F22", border_color="#5865F2", color="white", keyboard_type=ft.KeyboardType.NUMBER, disabled=True)
    btn_atualizar_item = ft.ElevatedButton("Atualizar Item", bgcolor="#5865F2", color="white", height=50, disabled=True)

    def selecionar_item_edicao(e):
        item_id = e.control.data
        item = db_core.get_item_por_id(item_id)
        if item:
            estado["item_edit_id"] = item_id
            edit_nome_input.value = item[1]
            edit_foto_input.value = item[2]
            edit_valor_input.value = formatar_moeda(item[3])
            edit_nome_input.disabled = edit_foto_input.disabled = edit_valor_input.disabled = btn_atualizar_item.disabled = False
            atualizar_lista_edit_itens()

    def atualizar_lista_edit_itens(e=None):
        termo = busca_edit_item.value.lower() if busca_edit_item.value else ""
        lista_edit_itens.controls.clear()
        for item_id, item_nome, item_foto in db_core.get_todos_itens():
            if termo in item_nome.lower():
                is_selected = (estado["item_edit_id"] == item_id)
                card = ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Image(src=f"items/{item_foto}", width=24, height=24, fit="contain"), bgcolor="#5865F2" if is_selected else "#1E1F22", padding=4, border_radius=6),
                        ft.Text(item_nome, color="white" if is_selected else "#DBDEE1", weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL, size=15, expand=True),
                        ft.Icon(ft.Icons.EDIT, color="white", size=18, visible=is_selected)
                    ]),
                    bgcolor="#404249" if is_selected else "#2B2D31", padding=10, border_radius=8, data=item_id, on_click=selecionar_item_edicao, ink=True
                )
                lista_edit_itens.controls.append(card)
        page.update()

    busca_edit_item.on_change = atualizar_lista_edit_itens

    def acao_salvar_edicao_item(e):
        if not estado["item_edit_id"]: return
        try:
            sucesso = db_core.atualizar_item(estado["item_edit_id"], edit_nome_input.value, edit_foto_input.value, limpar_moeda(edit_valor_input.value))
            if sucesso:
                page.overlay.append(ft.SnackBar(ft.Text("Item atualizado!"), open=True, bgcolor="#23A559"))
                estado["item_edit_id"] = None
                edit_nome_input.value = edit_foto_input.value = edit_valor_input.value = busca_edit_item.value = ""
                edit_nome_input.disabled = edit_foto_input.disabled = edit_valor_input.disabled = btn_atualizar_item.disabled = True
                carregar_dados_globais()
            else:
                page.overlay.append(ft.SnackBar(ft.Text("Item já existe!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()
        except ValueError:
            page.overlay.append(ft.SnackBar(ft.Text("Número inválido!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()

    btn_atualizar_item.on_click = acao_salvar_edicao_item

    aba_editar_itens = ft.Column([
        busca_edit_item,
        ft.Container(content=lista_edit_itens, padding=8, border_radius=8, bgcolor="#111214"),
        ft.Text("Dados do Item Selecionado:", color="#5865F2", weight=ft.FontWeight.BOLD),
        edit_nome_input, edit_foto_input, edit_valor_input, btn_atualizar_item
    ], spacing=15, scroll=ft.ScrollMode.AUTO)

    # ==========================================
    # ABA 4: EDIÇÃO DE HUNTS
    # ==========================================
    busca_edit_hunt_input = ft.TextField(label="🔍 Buscar Hunt...", bgcolor="#1E1F22", border_color="#23A559", color="white")
    lista_edit_hunts = ft.ListView(height=120, spacing=8)
    
    edit_nome_hunt = ft.TextField(label="Nome", bgcolor="#1E1F22", border_color="#5865F2", color="white", disabled=True)
    edit_shiny_hunt = ft.TextField(label="Shiny", bgcolor="#1E1F22", border_color="#5865F2", color="white", expand=True, disabled=True)
    edit_angry_hunt = ft.TextField(label="Angry", bgcolor="#1E1F22", border_color="#5865F2", color="white", expand=True, disabled=True)
    
    busca_edit_hunt_item = ft.TextField(label="🔍 Buscar item...", bgcolor="#1E1F22", border_color="#23A559", color="white", disabled=True, height=45)
    lista_disp_edit_hunt = ft.ListView(height=150, spacing=8)
    lista_sel_edit_hunt = ft.ListView(height=150, spacing=8)
    btn_atualizar_hunt = ft.ElevatedButton("Atualizar Hunt", bgcolor="#5865F2", color="white", height=50, disabled=True)

    def selecionar_hunt_edicao(e):
        hunt_id = e.control.data
        hunt = db_core.get_hunt_por_id(hunt_id)
        if hunt:
            estado["edit_hunt_id"] = hunt_id
            edit_nome_hunt.value = hunt[1]
            edit_shiny_hunt.value = hunt[2]
            edit_angry_hunt.value = hunt[3]
            
            # Carrega os itens salvos nesta hunt pro Set
            estado["edit_hunt_itens"] = db_core.get_itens_da_hunt(hunt_id)
            
            edit_nome_hunt.disabled = edit_shiny_hunt.disabled = edit_angry_hunt.disabled = busca_edit_hunt_item.disabled = btn_atualizar_hunt.disabled = False
            
            atualizar_lista_edit_hunts()
            atualizar_listas_itens_edit_hunt()

    def atualizar_lista_edit_hunts(e=None):
        termo = busca_edit_hunt_input.value.lower() if busca_edit_hunt_input.value else ""
        lista_edit_hunts.controls.clear()
        for h_id, h_nome in db_core.get_todas_hunts():
            if termo in h_nome.lower():
                is_selected = (estado["edit_hunt_id"] == h_id)
                card = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.EXPLORE, color="#5865F2" if is_selected else "#B5BAC1"),
                        ft.Text(h_nome, color="white" if is_selected else "#DBDEE1", weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL, expand=True)
                    ]),
                    bgcolor="#404249" if is_selected else "#2B2D31", padding=10, border_radius=8, data=h_id, on_click=selecionar_hunt_edicao, ink=True
                )
                lista_edit_hunts.controls.append(card)
        page.update()

    def atualizar_listas_itens_edit_hunt(e=None):
        termo = busca_edit_hunt_item.value.lower() if busca_edit_hunt_item.value else ""
        lista_disp_edit_hunt.controls.clear()
        lista_sel_edit_hunt.controls.clear()
        
        for item_id, item_nome, item_foto in db_core.get_todos_itens():
            if item_id in estado["edit_hunt_itens"]:
                lista_sel_edit_hunt.controls.append(criar_card_item_transfer(item_id, item_nome, item_foto, remover_item_edit_hunt, False))
            else:
                if termo in item_nome.lower():
                    lista_disp_edit_hunt.controls.append(criar_card_item_transfer(item_id, item_nome, item_foto, add_item_edit_hunt, True))
        page.update()

    def add_item_edit_hunt(e):
        estado["edit_hunt_itens"].add(e.control.data)
        atualizar_listas_itens_edit_hunt()

    def remover_item_edit_hunt(e):
        estado["edit_hunt_itens"].discard(e.control.data)
        atualizar_listas_itens_edit_hunt()

    busca_edit_hunt_input.on_change = atualizar_lista_edit_hunts
    busca_edit_hunt_item.on_change = atualizar_listas_itens_edit_hunt

    def acao_salvar_edicao_hunt(e):
        if not estado["edit_hunt_id"]: return
        if not edit_nome_hunt.value:
            page.overlay.append(ft.SnackBar(ft.Text("Nome da hunt obrigatório!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()
            return
        if not estado["edit_hunt_itens"]:
            page.overlay.append(ft.SnackBar(ft.Text("Adicione pelo menos 1 item!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()
            return
            
        db_core.atualizar_hunt(estado["edit_hunt_id"], edit_nome_hunt.value, edit_shiny_hunt.value, edit_angry_hunt.value, list(estado["edit_hunt_itens"]))
        page.overlay.append(ft.SnackBar(ft.Text("Hunt atualizada!"), open=True, bgcolor="#23A559"))
        
        estado["edit_hunt_id"] = None
        estado["edit_hunt_itens"].clear()
        edit_nome_hunt.value = edit_shiny_hunt.value = edit_angry_hunt.value = busca_edit_hunt_item.value = busca_edit_hunt_input.value = ""
        edit_nome_hunt.disabled = edit_shiny_hunt.disabled = edit_angry_hunt.disabled = busca_edit_hunt_item.disabled = btn_atualizar_hunt.disabled = True
        
        carregar_dados_globais()
        page.update()

    btn_atualizar_hunt.on_click = acao_salvar_edicao_hunt

    aba_editar_hunts = ft.Column([
        busca_edit_hunt_input,
        ft.Container(content=lista_edit_hunts, padding=8, border_radius=8, bgcolor="#111214"),
        ft.Divider(color="#1E1F22"),
        edit_nome_hunt,
        ft.Row([edit_shiny_hunt, edit_angry_hunt], spacing=15),
        ft.Row([
            ft.Column([ft.Text("Disponíveis", color="#23A559", weight=ft.FontWeight.BOLD), busca_edit_hunt_item, ft.Container(content=lista_disp_edit_hunt, padding=8, border_radius=8, bgcolor="#111214")], expand=True),
            ft.Column([ft.Text("Na Hunt", color="#5865F2", weight=ft.FontWeight.BOLD), ft.Container(height=45), ft.Container(content=lista_sel_edit_hunt, padding=8, border_radius=8, bgcolor="#111214")], expand=True),
        ], spacing=20, alignment=ft.MainAxisAlignment.START),
        btn_atualizar_hunt
    ], spacing=15, scroll=ft.ScrollMode.AUTO)


    # ==========================================
    # ATUALIZADOR GLOBAL DE TELA
    # ==========================================
    def carregar_dados_globais():
        atualizar_listas_cad_hunt()
        atualizar_lista_edit_itens()
        atualizar_lista_edit_hunts()

    carregar_dados_globais()

    # ==========================================
    # RETORNO DA TELA PRINCIPAL
    # ==========================================
    return ft.Container(
        content=ft.Column([
            ft.Text("Painel Administrativo", size=28, weight=ft.FontWeight.BOLD, color="#5865F2"),
            ft.Divider(color="#1E1F22"),
            ft.Tabs(
                selected_index=0,
                length=4,
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.TabBar(
                            tabs=[
                                ft.Tab(label="1. Cadastrar Itens"),
                                ft.Tab(label="2. Cadastrar Hunts"),
                                ft.Tab(label="3. Editar Itens"),
                                ft.Tab(label="4. Editar Hunts"),
                            ]
                        ),
                        ft.TabBarView(
                            expand=True,
                            controls=[
                                ft.Container(content=aba_itens, padding=20),
                                ft.Container(content=aba_hunts, padding=20),
                                ft.Container(content=aba_editar_itens, padding=20),
                                ft.Container(content=aba_editar_hunts, padding=20),
                            ]
                        )
                    ]
                )
            )
        ], expand=True),
        padding=20,
        width=850 # Aumentado um pouco para acomodar bem as duas colunas
    )