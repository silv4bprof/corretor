import json
import os
import platform
import tkinter as tk

from customtkinter import *
from tkinter.messagebox import showerror

# Constantes
TIMEOUT = 10
SISTEMA = platform.system().lower()
TEMA = "clam"
PADDING = 5
LARGURA_WIDGET_QUESTAO = 694
DIMENSOES_JANELA = "1024x600"

set_default_color_theme("green")


class Verificador:
    """Janela principal do corretor."""

    def __init__(self, caminho_config: str):
        """Construtor.
        `caminho_config` é o caminho para o arquivo json de configuração da correção."""
        super().__init__()
        janela = CTk()
        self.janela = janela

        # Lê o arquivo de configuração para criar a Atividade
        if not os.path.isfile(caminho_config):
            janela.title(f"Verificador de Código")
            janela.geometry(DIMENSOES_JANELA)
            showerror(
                "Erro",
                "Arquivo de configuração" + f' "{caminho_config}" não encontrado.',
            )
            exit()
        config = json.load(open(caminho_config, encoding="utf-8"))

        # Configura a janela
        janela.title(f"Verificador de Código")
        janela.geometry(DIMENSOES_JANELA)

        # Montagem da interface
        # O frame principal contém todos os elementos da tela
        # Isso facilita o redimensionamento da janela sem alterar seu conteúdo
        frame_principal = CTkFrame(janela)
        self.frame_principal = frame_principal
        frame_principal.pack(expand=True, fill=tk.BOTH)
        self._montar_frame_topo()

        # Adicionando campos de texto
        self.texto_esquerda = CTkTextbox(
            frame_principal,
            width=40,
            height=10,
        )
        self.texto_esquerda.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        self.texto_direita = CTkTextbox(
            frame_principal,
            width=40,
            height=10,
        )
        self.texto_direita.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

    def _montar_frame_topo(self):
        """Monta o frame do topo da tela."""
        frame_topo = CTkFrame(self.frame_principal, fg_color="#2b2b2b")
        frame_topo.pack(fill=BOTH)
        self.botao_verificar_todos = CTkButton(
            frame_topo,
            text="Verificar Código",
            command=self._verificar_todos,
        )
        self.botao_verificar_todos.pack(padx=PADDING * 4, pady=(PADDING * 4, 0))

    def _verificar_todos(self):
        """Testa todas as questões."""
        print("Verificando diferenças ...")

    def atualizar(self):
        """Atualiza este widget."""
        contador_corretas = 0
        nota = 0
        for qw in self.widgets_questoes:
            if qw.correta:
                contador_corretas += 1
                nota += qw.questao.pontos
        total = len(self.widgets_questoes)
        texto_resultado = f"Corretas: {contador_corretas} de {total}" + f" ({nota} pts)"
        self.label_corretas.configure(text=texto_resultado)

        # Redesenha a interface
        self.janela.update()
        self.janela.update_idletasks()


if __name__ == "__main__":
    app = Verificador("config.json")
    app.janela.mainloop()
