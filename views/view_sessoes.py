import flet as ft
from database import db_core

LISTA_CRISTAIS = [
    "Shiny Venusaur", "Shiny Charizard", "Shiny Blastoise", "Shiny Pidgeot", 
    "Shiny Raichu", "Shiny Venomoth", "Shiny Machamp", "Shiny Tentacruel", 
    "Shiny Farfetch'd", "Shiny Muk", "Shiny Marowak", "Shiny Tangela", 
    "Shiny Jynx", "Shiny Pinsir", "Shiny Meganium", "Shiny Typhlosion", 
    "Shiny Feraligatr", "Shiny Lanturn", "Shiny Xatu", "Shiny Ampharos", 
    "Shiny Magcargo", "Mega Sceptile", "Mega Blaziken", "Mega Swampert", 
    "Mega Gardevoir", "Mega Sableye", "Mega Manectric"
]

def view(page: ft.Page):
    campos_itens_loots = {}

    # ==========================================
    # CABEÇALHO
    # ==========================================
    header = ft.Row([
        ft.Container(
            content=ft.Icon(ft.Icons.EXPLORE, color="white", size=28),
            bgcolor="#23A559", padding=10, border_radius=8
        ),
        ft.Column([
            ft.Text("Registrar Sessão", size=24, weight=ft.FontWeight.BOLD, color="white"),
            ft.Text("Salve os resultados, métricas e loots da sua última hunt.", color="#B5BAC1", size=14)
        ], spacing=2)
    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # ==========================================
    # INFORMAÇÕES GERAIS
    # ==========================================
    dropdown_hunt = ft.Dropdown(label="Selecione a Hunt", bgcolor="#2B2D31", border_color="#5865F2", color="white", expand=2)
    tempo_input = ft.TextField(label="Tempo (ex: 1h30m)", bgcolor="#2B2D31", border_color="#5865F2", color="white", expand=1)
    mobs_input = ft.TextField(label="Qtd. Mobs Mortos", value="0", bgcolor="#2B2D31", border_color="#5865F2", color="white", keyboard_type=ft.KeyboardType.NUMBER, expand=1)
    
    shinies_input = ft.TextField(label="Shinies", value="0", bgcolor="#2B2D31", border_color="#5865F2", color="white", keyboard_type=ft.KeyboardType.NUMBER, expand=1)
    angrys_input = ft.TextField(label="Angrys", value="0", bgcolor="#2B2D31", border_color="#5865F2", color="white", keyboard_type=ft.KeyboardType.NUMBER, expand=1)
    crystais_input = ft.TextField(label="Crystais", value="0", bgcolor="#2B2D31", border_color="#E2C62F", color="white", keyboard_type=ft.KeyboardType.NUMBER, expand=1)

    dropdown_crystal_1 = ft.Dropdown(label="1º Shiny/Mega do Crystal", bgcolor="#2B2D31", border_color="#E2C62F", color="white", expand=True, visible=False)
    dropdown_crystal_2 = ft.Dropdown(label="2º Shiny/Mega do Crystal (Opcional)", bgcolor="#2B2D31", border_color="#E2C62F", color="white", expand=True, visible=False)
    container_crystais = ft.Row([dropdown_crystal_1, dropdown_crystal_2], spacing=15, visible=False)

    for c_nome in LISTA_CRISTAIS:
        dropdown_crystal_1.options.append(ft.dropdown.Option(c_nome))
        dropdown_crystal_2.options.append(ft.dropdown.Option(c_nome))

    # ==========================================
    # LISTA DE LOOTS (A BASE DE TUDO)
    # ==========================================
    lista_loots = ft.ListView(height=350, spacing=10)
    lista_loots.controls.append(ft.Text("Aguardando seleção da Hunt...", color="#B5BAC1", italic=True))

    # ==========================================
    # LÓGICA DE SELEÇÃO DA HUNT
    # ==========================================
    def carregar_hunts():
        dropdown_hunt.options.clear()
        for h_id, h_nome in db_core.get_todas_hunts():
            dropdown_hunt.options.append(ft.dropdown.Option(key=str(h_id), text=h_nome))

    carregar_hunts()

    def ao_selecionar_hunt(e):
        try:
            if not e.control.value: return
            hunt_id = int(e.control.value)
            
            lista_loots.controls.clear()
            campos_itens_loots.clear()
            
            itens_da_hunt = db_core.get_itens_completos_da_hunt(hunt_id)
            
            if not itens_da_hunt:
                lista_loots.controls.append(ft.Text("Esta Hunt não tem itens registrados no banco.", color=ft.Colors.RED_400))
            else:
                for item_id, item_nome, item_foto in itens_da_hunt:
                    qtd_input = ft.TextField(
                        value="0", width=80, text_align=ft.TextAlign.CENTER, 
                        bgcolor="#111214", border_color="#23A559", color="white",
                        keyboard_type=ft.KeyboardType.NUMBER
                    )
                    campos_itens_loots[item_id] = qtd_input 
                    
                    linha_item = ft.Container(
                        content=ft.Row([
                            # ÍCONE SUBSTITUINDO A IMAGEM PARA BLINDAR CONTRA ERROS
                            ft.Icon(ft.Icons.CATCHING_POKEMON, color="#5865F2"), 
                            ft.Text(item_nome, color="white", size=15, weight=ft.FontWeight.BOLD, expand=True),
                            ft.Text("Qtd:", color="#B5BAC1", size=13),
                            qtd_input
                        ]),
                        bgcolor="#2B2D31", padding=10, border_radius=8
                    )
                    lista_loots.controls.append(linha_item)
            
            page.update()
        except Exception as erro:
            page.overlay.append(ft.SnackBar(ft.Text(f"CRASH: {str(erro)}"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()

    dropdown_hunt.on_change = ao_selecionar_hunt

    # ==========================================
    # LÓGICA DE CRISTAIS E SALVAR SESSÃO
    # ==========================================
    def ao_mudar_crystais(e):
        try:
            qtd_crystais = int(crystais_input.value) if crystais_input.value else 0
            if qtd_crystais > 0:
                container_crystais.visible = True
                dropdown_crystal_1.visible = True
                dropdown_crystal_2.visible = True
            else:
                container_crystais.visible = False
                dropdown_crystal_1.value = None
                dropdown_crystal_2.value = None
        except ValueError:
            container_crystais.visible = False
        page.update()

    crystais_input.on_change = ao_mudar_crystais

    def salvar_sessao(e):
        if not dropdown_hunt.value:
            page.overlay.append(ft.SnackBar(ft.Text("Selecione uma Hunt!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()
            return
        if not tempo_input.value:
            page.overlay.append(ft.SnackBar(ft.Text("O tempo caçado é obrigatório!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()
            return
            
        try:
            qtd_crystais = int(crystais_input.value) if crystais_input.value else 0
            
            if qtd_crystais > 0 and not dropdown_crystal_1.value:
                page.overlay.append(ft.SnackBar(ft.Text("Você registrou Crystais. Selecione pelo menos 1 Shiny/Mega!"), open=True, bgcolor=ft.Colors.ERROR))
                page.update()
                return

            hunt_id = int(dropdown_hunt.value)
            mobs = int(mobs_input.value) if mobs_input.value else 0
            shinies = int(shinies_input.value) if shinies_input.value else 0
            angrys = int(angrys_input.value) if angrys_input.value else 0
            c_shiny_1 = dropdown_crystal_1.value if qtd_crystais > 0 else None
            c_shiny_2 = dropdown_crystal_2.value if qtd_crystais > 0 else None
            
            itens_dropados = {}
            for item_id, textfield in campos_itens_loots.items():
                qtd = int(textfield.value) if textfield.value else 0
                if qtd > 0:
                    itens_dropados[item_id] = qtd

            db_core.adicionar_sessao(hunt_id, tempo_input.value, mobs, shinies, angrys, qtd_crystais, c_shiny_1, c_shiny_2, itens_dropados)
            
            page.overlay.append(ft.SnackBar(ft.Text("Sessão salva com sucesso!"), open=True, bgcolor="#23A559"))
            
            tempo_input.value = ""
            mobs_input.value = shinies_input.value = angrys_input.value = crystais_input.value = "0"
            dropdown_crystal_1.value = dropdown_crystal_2.value = None
            container_crystais.visible = False
            for tf in campos_itens_loots.values(): tf.value = "0"
            
            dropdown_hunt.value = None
            lista_loots.controls.clear()
            lista_loots.controls.append(ft.Text("Aguardando seleção da Hunt...", color="#B5BAC1", italic=True))
            
            page.update()

        except ValueError:
            page.overlay.append(ft.SnackBar(ft.Text("Campos numéricos preenchidos incorretamente!"), open=True, bgcolor=ft.Colors.ERROR))
            page.update()

    btn_salvar = ft.ElevatedButton("Finalizar e Registrar Sessão", bgcolor="#23A559", color="white", height=50, width=300, on_click=salvar_sessao)

    # ==========================================
    # MONTAGEM DOS CARDS DA TELA
    # ==========================================
    card_info_geral = ft.Container(
        content=ft.Column([
            ft.Text("Informações da Caçada", color="#5865F2", weight=ft.FontWeight.BOLD),
            ft.Row([dropdown_hunt, tempo_input, mobs_input], spacing=15),
            ft.Row([shinies_input, angrys_input, crystais_input], spacing=15),
            container_crystais
        ], spacing=15),
        bgcolor="#1E1F22", padding=20, border_radius=10
    )

    card_loots = ft.Container(
        content=ft.Column([
            ft.Text("Resumo do Loot", color="#5865F2", weight=ft.FontWeight.BOLD),
            ft.Text("Preencha a quantidade exata de cada item dropado:", color="#B5BAC1", size=13),
            lista_loots
        ], spacing=10), 
        bgcolor="#1E1F22", padding=20, border_radius=10
    )

    return ft.Container(
        content=ft.Column([
            header,
            ft.Divider(color="#1E1F22", height=20),
            card_info_geral,
            card_loots,
            ft.Row([btn_salvar], alignment=ft.MainAxisAlignment.END)
        ], spacing=15, scroll=ft.ScrollMode.AUTO),
        padding=20,
        width=850
    )