import platform
import tkinter as tk
import difflib as df

from customtkinter import *
from tkinter.messagebox import showerror

# Constantes
TIMEOUT = 10
SISTEMA = platform.system().lower()
TEMA = "clam"
PADDING = 5
LARGURA_WIDGET_QUESTAO = 694
DIMENSOES_JANELA = "1024x700"
FONTE_NATIVA = "Courier"

set_default_color_theme("blue")


class Verificador:
    """Janela principal do verificador."""

    def __init__(self, caminho_config: str):
        """Construtor.
        `caminho_config` é o caminho para o arquivo json de configuração da verificação.
        """
        super().__init__()
        janela = CTk()
        self.janela = janela

        # Configura a janela
        janela.title(f"Verificador de Código")
        janela.geometry(DIMENSOES_JANELA)

        # Montagem da interface
        # O frame principal contém todos os elementos da tela
        # Isso facilita o redimensionamento da janela sem alterar seu conteúdo
        frame_principal = CTkFrame(janela, fg_color="#3d3d3d")
        frame_principal.pack(expand=True, fill=tk.BOTH)
        self.frame_principal = frame_principal

        self._montar_frame_topo()
        self._montar_frame_resultado()
        self._montar_frame_textos()

    def _montar_frame_topo(self):
        """Monta o frame do topo da tela."""
        frame_topo = CTkFrame(self.frame_principal, fg_color="#3d3d3d")
        frame_topo.pack(fill=BOTH)
        self.botao_verificar_todos = CTkButton(
            frame_topo,
            text="Verificar Código",
            command=self._verificar_todos,
        )
        self.botao_verificar_todos.pack(padx=PADDING * 4, pady=(PADDING * 4, 0))

    def _montar_frame_textos(self):
        """Monta o frame com os dois campos de texto para validação"""
        frame_campos_de_texto = CTkFrame(self.frame_principal, fg_color="#3d3d3d")
        frame_campos_de_texto.pack(expand=True, fill=BOTH)

        # Adicionando campos de texto
        self.texto_esquerda = CTkTextbox(
            frame_campos_de_texto, width=40, height=10, font=(FONTE_NATIVA, 16)
        )
        self.texto_esquerda.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        self.texto_direita = CTkTextbox(
            frame_campos_de_texto, width=40, height=10, font=(FONTE_NATIVA, 16)
        )
        self.texto_direita.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

    def _montar_frame_resultado(self):
        """Monta o frame do topo da tela."""
        frame_resultado = CTkFrame(self.frame_principal, fg_color="#3d3d3d")
        frame_resultado.pack(fill=BOTH)
        self.label_resultado = CTkLabel(
            frame_resultado, text="Ratio: 0", font=("Arial", 20)
        )
        self.label_resultado.pack(fill=BOTH, padx=10, pady=10)

    def _verificar_todos(self):
        """Validando os dois textos"""
        print("Verificando diferenças ...")
        texto_esquerda = self.texto_esquerda.get(1.0, END)
        texto_direita = self.texto_direita.get(1.0, END)
        res = df.SequenceMatcher(None, texto_esquerda, texto_direita)
        seq = res.ratio() * 100
        resultado = f"Ratio: {seq:.2f}%"
        print(resultado)
        self.label_resultado.configure(text=resultado)

        if seq > 80:
            cor_texto = "#FF3232"
        elif seq < 50:
            cor_texto = "#6AA84F"
        else:
            cor_texto = "#F1C232"

        self.label_resultado.configure(text_color=cor_texto)


if __name__ == "__main__":
    app = Verificador("config.json")
    app.janela.mainloop()
