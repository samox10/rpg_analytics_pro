import flet as ft
from views import view_admin
from views import view_sessoes

def main(page: ft.Page):
    # ==========================================
    # 1. CONFIGURAÇÕES GERAIS DA JANELA
    # ==========================================
    page.title = "RPG Analytics Pro"
    page.window_width = 1280
    page.window_height = 720
    page.bgcolor = "#2B2D31"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # ==========================================
    # 2. ÁREA DE CONTEÚDO DINÂMICO
    # ==========================================
    main_content = ft.Container(
        content=ft.Text("Carregando...", size=20),
        expand=True,
        padding=20
    )

    # ==========================================
    # 3. LÓGICA DE ROTEAMENTO (NAVEGAÇÃO)
    # ==========================================
    def on_nav_change(e):
        index = e.control.selected_index
        main_content.content = None 
        
        if index == 0:
            main_content.content = ft.Text("Em breve: Visão Geral e Lucro Total", size=24, color="#5865F2", weight=ft.FontWeight.BOLD)
        elif index == 1:
            main_content.content = view_sessoes.view(page)
        elif index == 2:
            main_content.content = ft.Text("Em breve: Inventário e Patrimônio", size=24, color="#5865F2", weight=ft.FontWeight.BOLD)
        elif index == 3:
            main_content.content = ft.Text("Em breve: Quests Diárias e Mensais", size=24, color="#23A559", weight=ft.FontWeight.BOLD)
        elif index == 4:
            main_content.content = view_admin.view(page)
        
        page.update()

    # ==========================================
    # 4. COMPONENTE: MENU LATERAL (NavigationRail)
    # ==========================================
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        bgcolor="#1E1F22",
        indicator_color="#5865F2",
        group_alignment=-0.9,
        destinations=[
            # Note a correção: ft.Icons (com 'I' maiúsculo)
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.EXPLORE_OUTLINED,
                selected_icon=ft.Icons.EXPLORE,
                label="Hunts",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.INVENTORY_2_OUTLINED,
                selected_icon=ft.Icons.INVENTORY,
                label="Inventário",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ASSIGNMENT_OUTLINED,
                selected_icon=ft.Icons.ASSIGNMENT,
                label="Quests",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                selected_icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                label="Admin",
            ),
        ],
        on_change=on_nav_change,
    )

    on_nav_change(type('Event', (object,), {'control': nav_rail})())

    # ==========================================
    # 5. MONTAGEM DA TELA (LAYOUT FINAL)
    # ==========================================
    page.add(
        ft.Row(
            controls=[
                nav_rail,
                ft.VerticalDivider(width=1, color="#1E1F22"), 
                main_content
            ],
            expand=True,
            spacing=0
        )
    )

if __name__ == "__main__":
    # Informamos ao Flet onde buscar as imagens do projeto
    ft.run(main, assets_dir="assets")