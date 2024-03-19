import tkinter as tk
import customtkinter as ctk


def vincular_rolagem_textboxes(textbox1, textbox2):
    def rolar_textbox1(*args):
        fraction = textbox1.yview()[0]
        scrollbar_position.set(fraction)
        textbox2.yview_moveto(fraction)

    def rolar_textbox2(*args):
        fraction = textbox2.yview()[0]
        scrollbar_position.set(fraction)
        textbox1.yview_moveto(fraction)

    def rolar_textbox1_scrollbar(*args):
        fraction = scrollbar1.get()[0]
        scrollbar_position.set(fraction)
        textbox2.yview_moveto(fraction)

    def rolar_textbox2_scrollbar(*args):
        fraction = scrollbar2.get()[0]
        scrollbar_position.set(fraction)
        textbox1.yview_moveto(fraction)

    scrollbar_position = tk.DoubleVar()

    textbox1.bind("<MouseWheel>", rolar_textbox1)
    textbox1.bind("<Button-4>", rolar_textbox1)
    textbox1.bind("<Button-5>", rolar_textbox1)

    textbox2.bind("<MouseWheel>", rolar_textbox2)
    textbox2.bind("<Button-4>", rolar_textbox2)
    textbox2.bind("<Button-5>", rolar_textbox2)

    scrollbar1 = ctk.CTkScrollbar(textbox1, command=textbox1.yview)
    scrollbar1.grid(row=0, column=1, sticky="ns")
    textbox1.configure(yscrollcommand=scrollbar1.set)
    scrollbar1.bind("<B1-Motion>", rolar_textbox1_scrollbar)

    scrollbar2 = ctk.CTkScrollbar(textbox2, command=textbox2.yview)
    scrollbar2.grid(row=0, column=1, sticky="ns")
    textbox2.configure(yscrollcommand=scrollbar2.set)
    scrollbar2.bind("<B1-Motion>", rolar_textbox2_scrollbar)


def main():
    root = ctk.CTk()
    root.geometry("1200x500")
    root.title("Sincronização de Rolagem")

    frame = ctk.CTkFrame(root)
    frame.pack(fill="both", expand=True)

    # Configuração do redimensionamento das linhas e colunas do frame
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    textbox1 = ctk.CTkTextbox(frame, wrap="none")
    textbox1.grid(row=0, column=0, sticky="nsew")

    textbox2 = ctk.CTkTextbox(frame, wrap="none")
    textbox2.grid(row=0, column=1, sticky="nsew")

    vincular_rolagem_textboxes(textbox1, textbox2)

    root.mainloop()


if __name__ == "__main__":
    main()
