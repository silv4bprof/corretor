import tkinter as tk


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

    def rolar_textbox1_xscrollbar(*args):
        fraction = scrollbar_x1.get()[0]
        textbox2.xview_moveto(fraction)

    def rolar_textbox2_xscrollbar(*args):
        fraction = scrollbar_x2.get()[0]
        textbox1.xview_moveto(fraction)

    scrollbar_position = tk.DoubleVar()

    textbox1.bind("<MouseWheel>", rolar_textbox1)
    textbox1.bind("<Button-4>", rolar_textbox1)
    textbox1.bind("<Button-5>", rolar_textbox1)

    textbox2.bind("<MouseWheel>", rolar_textbox2)
    textbox2.bind("<Button-4>", rolar_textbox2)
    textbox2.bind("<Button-5>", rolar_textbox2)

    scrollbar1 = tk.Scrollbar(textbox1, command=textbox1.yview)
    scrollbar1.pack(side="right", fill="y")
    textbox1.config(yscrollcommand=scrollbar1.set)
    scrollbar1.bind("<B1-Motion>", rolar_textbox1_scrollbar)

    scrollbar2 = tk.Scrollbar(textbox2, command=textbox2.yview)
    scrollbar2.pack(side="right", fill="y")
    textbox2.config(yscrollcommand=scrollbar2.set)
    scrollbar2.bind("<B1-Motion>", rolar_textbox2_scrollbar)

    scrollbar_x1 = tk.Scrollbar(textbox1, command=textbox1.xview, orient="horizontal")
    scrollbar_x1.pack(side="bottom", fill="x")
    textbox1.config(xscrollcommand=scrollbar_x1.set)
    scrollbar_x1.bind("<B1-Motion>", rolar_textbox1_xscrollbar)

    scrollbar_x2 = tk.Scrollbar(textbox2, command=textbox2.xview, orient="horizontal")
    scrollbar_x2.pack(side="bottom", fill="x")
    textbox2.config(xscrollcommand=scrollbar_x2.set)
    scrollbar_x2.bind("<B1-Motion>", rolar_textbox2_xscrollbar)


def main():
    root = tk.Tk()
    root.geometry("1200x500")
    root.title("Sincronização de Rolagem")

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    textbox1 = tk.Text(frame, wrap="none")
    textbox1.pack(side="left", fill="both", expand=True)

    textbox2 = tk.Text(frame, wrap="none")
    textbox2.pack(side="right", fill="both", expand=True)

    vincular_rolagem_textboxes(textbox1, textbox2)

    root.mainloop()


if __name__ == "__main__":
    main()
