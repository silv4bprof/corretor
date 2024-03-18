import json
import os
import platform
import tkinter as tk

from tkinter import ttk
from tkinter.messagebox import showerror
from platform import system
from tkinter import Text

# Constantes
TIMEOUT = 10
SISTEMA = platform.system().lower()
TEMA = "clam"
PADDING = 5
LARGURA_WIDGET_QUESTAO = 694
DIMENSOES_JANELA = "1024x600"


class ScrolledFrame(ttk.Frame):
    """Frame com scrollbar.
    *ATENÇÃO:* para colocar widgets dentro deste, passe o `.conteudo` deste como `parent` do widget filho.
    """

    def __init__(self, parent, width, conteudo_kwargs, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Na raiz, é necessário um Canvas
        canvas = tk.Canvas(self, width=width, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(anchor="center", side="left", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Dentro do canvas, é necessário um Frame
        conteudo = ttk.Frame(canvas, **conteudo_kwargs)
        posx = parent.winfo_width() / 2
        canvas.create_window((posx, 0), width=width, window=conteudo, anchor="nw")

        # Configura o Canvas para atualizar a scrollbar quando o tamanho muda
        conteudo.bind("<Configure>", self._on_resize)
        # Habilita o mouse wheel
        if SISTEMA == "windows":
            canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        else:  # Linux
            canvas.bind_all("<Button-4>", self._on_mousewheel_up_linux)
            canvas.bind_all("<Button-5>", self._on_mousewheel_down_linux)

        # Guarda as referências no self
        self.canvas = canvas
        self.conteudo = conteudo
        self.parent = parent

    def _on_mousewheel_windows(self, event):
        """Controla a view do `canvas` no Windows."""
        delta = event.delta
        self.canvas.yview_scroll(delta // -120, "units")

    def _on_mousewheel_up_linux(self, event):
        """Sobe a view do `canvas` no Linux."""
        # TODO: Considerar o delta
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_down_linux(self, event):
        """Desce a view do `canvas` no Linux."""
        self.canvas.yview_scroll(1, "units")

    def _on_resize(self, event):
        """Redimensiona o `canvas`."""
        # Atualiza os widgets para pegar o tamanho atual
        self.conteudo.update()
        # bbox é uma tupla (x, y, largura, altura) que engloba todo o conteúdo do canvas
        bbox = self.canvas.bbox("all")
        # Existe algum problema que ela pega além do tamanho do que é visível,
        # então consertamos isso copiando os demais valores e recalculando a altura
        altura = self.conteudo.winfo_height()
        nova_bbox = *bbox[:3], altura
        self.canvas.configure(
            scrollregion=nova_bbox,
            height=altura,
        )


class Verificador:
    """Janela principal do corretor."""

    def __init__(self, caminho_config: str):
        """Construtor.
        `caminho_config` é o caminho para o arquivo json de configuração da correção."""
        super().__init__()
        # Tk lança erros em vez de exibir no terminal
        tk.Tk.report_callback_exception = lambda root, _, val, tb: showerror(
            "Error", message=str(val)
        )
        janela = tk.Tk()
        self.janela = janela

        # Tema e estilos
        style = ttk.Style()
        style.theme_use(TEMA)
        style.configure("H2.TLabel", font="Arial 14")
        style.configure("H1.TLabel", font="Arial 16")
        style.configure("TButton", font="Arial 10")
        style.configure("Fundo.TFrame", background="#bba")
        style.configure(
            "Verde.TButton",
            background="#9e9",
            bordercolor="#6b6",
            lightcolor="#beb",
            darkroom="#393",
        )
        style.configure(
            "Vermelho.TButton",
            background="#e99",
            bordercolor="#b66",
            lightcolor="#ebb",
            darkroom="#933",
        )
        style.configure(
            "Amarelo.TButton",
            background="#ee9",
            bordercolor="#bb6",
            lightcolor="#eeb",
            darkcolor="#993",
        )

        # Lê o arquivo de configuração para criar a Atividade
        if not os.path.isfile(caminho_config):
            janela.title(f"Corretor Automático")
            janela.geometry(DIMENSOES_JANELA)
            showerror(
                "Erro",
                "Arquivo de configuração" + f' "{caminho_config}" não encontrado.',
            )
            exit()
        config = json.load(open(caminho_config, encoding="utf-8"))
        # self.atividade = Atividade.ler_config(config)

        # Configura a janela
        janela.title(f"Corretor Automático")
        janela.geometry(DIMENSOES_JANELA)

        if system() == "Windows":
            janela.state("zoomed")

        # Montagem da interface
        # O frame principal contém todos os elementos da tela
        # Isso facilita o redimensionamento da janela sem alterar seu conteúdo
        frame_principal = ttk.Frame(janela)
        self.frame_principal = frame_principal
        frame_principal.pack(expand=True, fill=tk.BOTH)
        self._montar_frame_topo()
        self.frame_questoes = ScrolledFrame(
            frame_principal,
            width=LARGURA_WIDGET_QUESTAO,
            conteudo_kwargs=dict(style="Fundo.TFrame"),
            style="Fundo.TFrame",
        )
        self.frame_questoes.pack(fill=tk.BOTH)

        # Adicionando campos de texto
        self.texto_esquerda = Text(
            frame_principal, wrap=tk.WORD, width=40, height=10, padx=5, pady=5
        )
        self.texto_esquerda.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.texto_direita = Text(
            frame_principal, wrap=tk.WORD, width=40, height=10, padx=5, pady=5
        )
        self.texto_direita.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _montar_frame_topo(self):
        """Monta o frame do topo da tela."""
        frame_topo = ttk.Frame(self.frame_principal, borderwidth=2, relief=tk.GROOVE)
        frame_topo.pack(fill=tk.BOTH)
        self.botao_corrigir_todas = ttk.Button(
            frame_topo,
            text="Verificar Código",
            command=self._verificar_todos,
            padding=PADDING * 3,
        )
        self.botao_corrigir_todas.pack(padx=PADDING * 4, pady=(PADDING * 4, 0))
        self.label_corretas = ttk.Label(frame_topo)
        self.label_corretas.pack(pady=(0, PADDING * 4))

    def _verificar_todos(self):
        """Testa todas as questões."""
        print("Verificar diferenças")

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

