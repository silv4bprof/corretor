def vincular_rolagem_textbox(textbox_origem, textbox_destino):
    def rolar_textbox(*args):
        scrollbar_position = textbox_origem.yview()[0]
        textbox_destino.yview_moveto(scrollbar_position)

    textbox_origem.bind("<MouseWheel>", rolar_textbox)
    textbox_origem.bind("<Button-4>", rolar_textbox)
    textbox_origem.bind("<Button-5>", rolar_textbox)
