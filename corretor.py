import json
import os
import platform
import subprocess
import tkinter as tk

from tkinter import ttk
from tkinter.messagebox import showerror
from platform import system

# MODELO

# Constantes
TIMEOUT = 10
SISTEMA = platform.system().lower()
TEMA = "clam"

# Classes


class Questao:
    """Uma questão para corrigir."""

    def __init__(self, descricao: str, pontos: int, correcoes: list["Correcao"]):
        """Construtor.

        Parâmetros:
        - `descricao` é uma descrição da questão.
        - `pontos` são os pontos (nota) da questão.
        - `correcoes` são os argumentos e verificações da saída do script para corrigir a questão.
        """
        self.descricao = descricao
        self.correcoes = correcoes
        self.pontos = pontos

    @classmethod
    def ler_config(cls, config: dict) -> "Questao":
        """Cria uma instância a partir do dict obtido da leitura do arquivo de configuração.

        Parâmetros:
        - `config`  são as configurações de uma questão (um elemento da lista "questoes").
        """
        # Chaves obrigatórias, que devem estar definidas na questão
        desc = config["descricao"]
        pontos = config["pontos"]
        # Lista de correções
        correcoes: list[Correcao] = []
        for config_correcao in config["correcoes"]:
            # Adiciona valores padrão à correção que vieram da questão
            aux = config_correcao
            config_correcao = config.copy()
            # Valores definidos na questão prevalecem
            config_correcao.update(aux)
            c = Correcao.ler_config(config_correcao)
            correcoes += [c]
        q = cls(desc, pontos, correcoes)
        return q


class Correcao:
    """Uma correção de uma questão."""

    def __init__(
        self,
        script: str,
        msg_erro: str,
        comando: str,
        func_expect,
        args_expect: list = [],
        entrada: str = "",
        args: str = "",
        **kwargs,
    ):
        """Construtor.

        Parâmetros:
        - `script` é o script da resposta.
        - `msg_erro` mensagem de erro amigável ao usuário.
        - `comando` é o comando do terminal para executar o script da resposta.
        - `func_expect` é a função que verifica a saída do script.
        - `args_expect` são os argumentos da função que verifica a saída do script.
        - `entrada` é a entrada do teclado.
        - `args` são os argumentos da linha de comando.
        """
        self.comando: str = comando
        self.script: str = script
        self.entrada: str = entrada
        self.args: str = args
        # TODO: Unificar func_expect e args_expect num argumento só.
        # Isso ajuda a não esquecer um ou outro.
        self.func_expect: str = func_expect
        self.args_expect: list = args_expect
        self.msg_erro: str = msg_erro

    @classmethod
    def ler_config(cls, config: dict) -> "Correcao":
        """Cria uma instância a partir do dict obtido da leitura do arquivo config.json.

        Parâmetros:
        - `config` são as configurações de uma correção (um elemento da lista "correcoes").
        """
        correcao = cls(**config)
        return correcao

    @property
    def comando_completo(self) -> str:
        """Retorna o comando para executar o script, incluindo o comando do terminal, script e argumentos."""
        c = f"{self.comando} {self.script}"
        if self.args:
            c += f" {self.args}"
        return c

    def corrigir(self) -> tuple[int, str, str]:
        """Executa a correcao e retorna o código de saída, a saída e o erro."""
        codigo = -1
        resposta = "Não executado\n"
        erro = "Não executado\n"
        try:
            processo = subprocess.run(
                [self.comando, self.script, self.args],
                capture_output=True,
                input=self.entrada,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=TIMEOUT,
            )
            codigo = processo.returncode
            resposta = processo.stdout
            erro = processo.stderr
        except subprocess.TimeoutExpired as e:
            codigo = 1
            resposta = e.stdout.decode() if e.stdout else "\n"
            erro = f"Timeout de {TIMEOUT}s expirado."
        # TODO: Revisar os códigos de erro no Windows e Linux
        # TODO: Revisar os códigos de erro do PHP e Python
        if codigo == 0:  # O script funcionou
            # Verifica a resposta
            ok, erro = eval(self.func_expect)(resposta, self.args_expect)
            if not ok and self.msg_erro:
                erro = self.msg_erro
        elif codigo == 2:  # File not found
            erro = f"Arquivo {self.script} não encontrado."
        else:
            erro = f"(Código {codigo})\n" + erro
        return codigo, resposta, erro


class Atividade:
    """Uma atividade, com questões para corrigir."""

    def __init__(self, titulo: str, questoes: list[Questao]):
        self.titulo: str = titulo
        self.questoes: list[Questao] = questoes

    @classmethod
    def ler_config(cls, config: dict) -> "Atividade":
        """Lê uma arquivo de configuração recursivamente.

        Parâmetros:
        - `config` é o dicionário lido do arquivo de configuração.
        """
        titulo = config["titulo"]
        questoes: list[Questao] = []
        for config_questao in config["questoes"]:
            # Adiciona valores padrão à questão que vieram da atividade
            aux = config_questao
            config_questao = config.copy()
            # Valores definidos na questão prevalecem
            config_questao.update(aux)
            questoes += [Questao.ler_config(config_questao)]
        return cls(titulo, questoes)


# Funções de correcao


def testar_igual(resultado: str, esperado: str) -> tuple[bool, str]:
    """Verifica se o `resultado` é igual ao `esperado`."""
    resultado = resultado.strip("\n\r\t ")
    esperado = esperado.strip("\n\r\t ")
    if resultado != esperado:
        erro = f"Esperava '{esperado}', recebeu '{resultado}'"
        return False, erro
    return True, ""


def testar_regex(resultado: str, regex: str) -> tuple[bool, str]:
    """Verifica se `regex` casa em `resultado`."""
    import re

    resultado = resultado.strip("\n\r\t ")
    padrao = re.compile(regex)
    if padrao.search(resultado) is None:
        erro = f'Esperava encontrar o padrão "{regex}".'
        return False, erro
    return True, ""


# INTERFACE GRÁFICA

# Constantes
PADDING = 5
LARGURA_WIDGET_QUESTAO = 694
DIMENSOES_JANELA = "1024x600"

# Classes


class ScrolledText(tk.Text):
    """ScrolledText do tk.scrolledtext reimplementado com ttk.
    (Copiado de https://github.com/python/cpython/blob/3.12/Lib/tkinter/scrolledtext.py)
    """

    def __init__(self, parent=None, **kw):
        self.frame = ttk.Frame(parent)
        self.vbar = ttk.Scrollbar(self.frame)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)

        kw.update({"yscrollcommand": self.vbar.set})
        tk.Text.__init__(self, self.frame, **kw)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vbar["command"] = self.yview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != "_" and m != "config" and m != "configure":
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


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


class Corretor:
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
        self.atividade = Atividade.ler_config(config)

        # Configura a janela
        janela.title(f"Corretor Automático - {self.atividade.titulo}")
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
        self._montar_questoes()

    def _montar_frame_topo(self):
        """Monta o frame do topo da tela."""
        frame_topo = ttk.Frame(self.frame_principal, borderwidth=2, relief=tk.GROOVE)
        frame_topo.pack(fill=tk.BOTH)
        self.botao_corrigir_todas = ttk.Button(
            frame_topo,
            text="Corrigir Todas",
            command=self._corrigir_todas,
            padding=PADDING * 3,
        )
        self.botao_corrigir_todas.pack(padx=PADDING * 4, pady=(PADDING * 4, 0))
        self.label_corretas = ttk.Label(frame_topo)
        self.label_corretas.pack(pady=(0, PADDING * 4))

    def _montar_questoes(self):
        """Monta os widgets das questões."""
        self.widgets_questoes: list[QuestaoWidget] = []
        for questao in self.atividade.questoes:
            qw = QuestaoWidget(self.frame_questoes.conteudo, self, questao)
            qw.pack(pady=PADDING * 2)
            self.widgets_questoes += [qw]

    def _corrigir_todas(self):
        """Testa todas as questões."""
        for qw in self.widgets_questoes:
            qw._corrigir_questao()

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
        if contador_corretas == total:
            self.botao_corrigir_todas.configure(style="Verde.TButton")
        elif contador_corretas == 0:
            self.botao_corrigir_todas.configure(style="Vermelho.TButton")
        else:
            self.botao_corrigir_todas.configure(style="Amarelo.TButton")
        # Redesenha a interface
        self.janela.update()
        self.janela.update_idletasks()


class QuestaoWidget(ttk.Frame):
    """Widget de Questões."""

    contador_corretas: int = 0

    def __init__(self, parent, janela_corretor: Corretor, questao: Questao):
        """Construtor.
        Parâmetros:
        - `parent` é o widget pai que conterá este.
        - `questao` é a questão correspondente.
        - `janela_corretor` é uma referência à aplicação do corretor."""
        super().__init__(parent)
        self.janela_corretor = janela_corretor
        self.frame_questoes: ScrolledFrame = parent
        self.questao: Questao = questao
        self.widgets_correcoes: list[CorrecaoWidget] = []
        # Personalização
        self.configure(borderwidth=2, relief=tk.GROOVE)
        # Montagem
        self._montar_primeira_linha()
        self._montar_correcoes()

    def _montar_primeira_linha(self):
        """Monta a primeira linha deste widget, que contém a descrição da questão, o botão para corrigir e o label do resultado."""
        frame1 = ttk.Frame(self)
        frame1.grid(columnspan=2, sticky="news")
        desc = self.questao.descricao
        if self.questao.pontos >= 0:
            desc += f" ({self.questao.pontos} pts)"
        self.label_decricao = ttk.Label(frame1, text=desc, style="H1.TLabel")
        self.label_decricao.pack(
            side=tk.LEFT,
            fill="x",
            expand=True,
            anchor="n",
            padx=(PADDING * 3, 0),
            pady=(PADDING * 3, 0),
        )

        frame2 = ttk.Frame(frame1)
        frame2.pack(side=tk.RIGHT)
        self.botao_corrigir = ttk.Button(
            frame2,
            text="Corrigir Questão",
            command=self._corrigir_questao,
            padding=PADDING * 2,
        )
        self.botao_corrigir.pack(
            side=tk.TOP, anchor="e", padx=(0, PADDING * 3), pady=(PADDING * 3, 0)
        )
        self.label_resultado = ttk.Label(frame2, text=f"")
        self.label_resultado.pack(
            side=tk.BOTTOM, anchor="e", padx=(0, PADDING * 3), pady=(0, PADDING)
        )

    def _montar_correcoes(self):
        """Monta o widget de cada correção."""
        for i, p in enumerate(self.questao.correcoes):
            tw = CorrecaoWidget(self, p)
            tw.grid(padx=PADDING * 3, pady=(0, PADDING * 3), row=i + 1)
            self.widgets_correcoes += [tw]

    def _corrigir_questao(self):
        """Executa todas as correcoes da questão."""
        for tw in self.widgets_correcoes:
            tw._corrigir()

    def atualizar(self):
        """Atualiza este widget."""
        self.contador_corretas = 0
        for c in self.widgets_correcoes:
            if c.resultado == "Correta":
                self.contador_corretas += 1
        texto_corretas = (
            f"Corretas: {self.contador_corretas} de {len(self.widgets_correcoes)}"
        )
        if self.contador_corretas == len(self.widgets_correcoes):
            texto_corretas += f" (+{self.questao.pontos} pts)"
        self.label_resultado.configure(text=f"{texto_corretas}")
        estilo = "TButton"
        if self.contador_corretas == len(self.widgets_correcoes):
            estilo = "Verde." + estilo
        elif self.contador_corretas == 0:
            estilo = "Vermelho." + estilo
        else:
            estilo = "Amarelo." + estilo
        self.botao_corrigir.configure(style=estilo)
        self.janela_corretor.atualizar()

    @property
    def correta(self) -> bool:
        """Retorna True se todas as correções estão corretas e False, caso contrário."""
        return self.contador_corretas == len(self.widgets_correcoes)


class CorrecaoWidget(ttk.Frame):
    """Widget da Correcao."""

    resultado = "Não executada"

    def __init__(self, parent, correcao: Correcao):
        """Construtor.
        Parâmetros:
        - `parent` é o widget pai que conterá este.
        - `correcao` é a correcao correspondente."""
        super().__init__(parent)
        self.widget_questao: QuestaoWidget = parent
        self.correcao: Correcao = correcao

        # Montagem
        self._montar_primeira_linha()
        self._montar_entrada()
        self._montar_resultado()

    def _corrigir(self):
        """Executa a correcao e atualiza a interface com o resultado."""
        _, saida, erro = self.correcao.corrigir()
        # Atualiza a interface
        text = self.text_resultado
        res = ""  # Guarda o resultado da correção
        if saida:
            saida = saida  # Remove a linha extra que sempre vem
            res += f"Saída:\n{saida}"
        if erro:
            # Adiciona quebra de linha antes do erro
            if len(res) > 0 and not res.endswith("\n"):
                res += "\n"
            res += f"Erro:\n{erro}"
        # Habilita a caixa de texto para edição
        text.configure(state=tk.NORMAL)
        text.delete(0.0, "end")  # Limpa o texto
        text.insert("end", res)  # Insere o resultado
        altura = min(len(res.split("\n")), 20)  # Ajusta a altura
        text.configure(height=altura, state=tk.DISABLED)  # Desabilita a edição
        # Atualiza o label do resultado e a cor do botão
        estilo = "TButton"  # Começa com botão comum
        # Mesmo o código sendo 0, a saída precisa ser a esperada, então é necessário que erro seja None
        if erro:
            self.resultado = "Incorreta"
            estilo = "Vermelho." + estilo
        else:
            self.resultado = "Correta"
            estilo = "Verde." + estilo
        self.label_resultado.configure(text=self.resultado)
        self.botao_corrigir.configure(style=estilo)
        # Atualiza o widget da questão
        self.widget_questao.atualizar()

    def _montar_primeira_linha(self):
        label = ttk.Label(self, text=f"Comando", style="H2.TLabel")
        label.grid(column=0, sticky="w", pady=(0, PADDING))
        label = ttk.Label(self, text=f"{self.correcao.comando_completo}")
        label.grid(row=1, column=0, sticky="w", pady=(0, PADDING))
        self.botao_corrigir = ttk.Button(
            self, text="Testar", width=8, command=self._corrigir
        )
        self.botao_corrigir.grid(column=1, row=0, sticky="e")
        self.label_resultado = ttk.Label(self, text=f"")
        self.label_resultado.grid(column=1, row=1, sticky="e", pady=(0, PADDING))

    def _montar_entrada(self):
        row = 2
        ttk.Label(self, text=f"Entrada", style="H2.TLabel").grid(
            column=0, row=row, sticky="w", pady=(0, PADDING)
        )
        row += 1
        text_entrada = ScrolledText(self, wrap=tk.WORD, width=80, height=1)
        text_entrada.grid(
            column=0, row=row, sticky="w", columnspan=2, pady=(0, PADDING)
        )
        text_entrada.delete(0.0, "end")  # Limpa o texto
        if self.correcao.entrada:
            entrada: str = self.correcao.entrada
            text_entrada.insert("end", entrada)  # Insere a entrada
            # Ajusta a altura
            altura = len(entrada.split("\n"))
            text_entrada.configure(height=altura)
        # Desabilita a edição
        text_entrada.configure(state=tk.DISABLED)
        self.text_entrada = text_entrada

    def _montar_resultado(self):
        row = 4
        ttk.Label(self, text=f"Resultado", style="H2.TLabel").grid(
            column=0, row=row, sticky="w", pady=(0, PADDING)
        )
        row += 1
        self.text_resultado = ScrolledText(
            self, wrap=tk.WORD, width=80, height=1, state=tk.DISABLED
        )
        self.text_resultado.grid(
            column=0, row=row, sticky="w", columnspan=2, pady=(0, PADDING)
        )


# PROGRAMA PRINCIPAL

if __name__ == "__main__":
    app = Corretor("config.json")
    app.janela.mainloop()
