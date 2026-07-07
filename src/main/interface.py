import os
import customtkinter as ctk
from PIL import Image, ImageTk

from filtros import (
    Imagem,
    FiltroBlurred,
    FiltroContorno,
    FiltroEscalaDeCinza,
    FiltroNegativo,
    FiltroPretoEBranco,
)


class CaixaDeMensagem(ctk.CTkToplevel):
    def __init__(self, master, titulo, mensagem, tipo="info"):
        super().__init__(master)
        self.title(titulo)
        self.geometry("360x180")
        self.configure(fg_color="#F5F7FB")
        self.transient(master)
        self.grab_set()

        cor_titulo = "#1F3A5F"
        cor_botao = "#4A90E2"
        if tipo == "erro":
            cor_titulo = "#B23A48"
            cor_botao = "#E76F51"
        elif tipo == "aviso":
            cor_titulo = "#A66A00"
            cor_botao = "#E2A44D"

        ctk.CTkLabel(
            self,
            text=titulo,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=cor_titulo,
        ).pack(pady=(18, 8))

        ctk.CTkLabel(
            self,
            text=mensagem,
            wraplength=320,
            justify="center",
            text_color="#4A5A6A",
        ).pack(padx=18, pady=(4, 12))

        ctk.CTkButton(
            self,
            text="OK",
            width=120,
            height=38,
            corner_radius=18,
            fg_color=cor_botao,
            hover_color="#3B7CCB" if tipo != "erro" else "#D95D42",
            text_color="white",
            command=self.destroy,
        ).pack(pady=(0, 12))

        self.after(100, self.lift)


class FilePicker(ctk.CTkToplevel):
    def __init__(self, master, pasta_inicial, callback):
        super().__init__(master)
        self.title("Selecionar imagem")
        self.geometry("560x500")
        self.configure(fg_color="#F5F7FB")
        self.transient(master)
        self.grab_set()
        self.callback = callback
        self.pasta_atual = os.path.abspath(pasta_inicial)
        self.caminho_selecionado = None
        self._criar_widgets()
        self._atualizar_lista()

    def _criar_widgets(self):
        ctk.CTkLabel(
            self,
            text="Selecionar imagem",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1F3A5F",
        ).pack(pady=(16, 8))

        ctk.CTkLabel(
            self,
            text="Navegue pelos diretórios e escolha uma imagem para carregar.",
            text_color="#4A5A6A",
        ).pack(pady=(0, 10))

        self.caminho_entry = ctk.CTkEntry(
            self,
            width=500,
            border_width=1,
            fg_color="#FFFFFF",
            text_color="#1F3A5F",
        )
        self.caminho_entry.pack(pady=(0, 10))
        self.caminho_entry.insert(0, self.pasta_atual)

        self.lista_frame = ctk.CTkScrollableFrame(
            self,
            width=500,
            height=260,
            fg_color="#FFFFFF",
            corner_radius=16,
        )
        self.lista_frame.pack(pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            self,
            text="Selecione um arquivo de imagem.",
            text_color="#4A5A6A",
        )
        self.status_label.pack(pady=(0, 8))

        botoes_frame = ctk.CTkFrame(self, fg_color="transparent")
        botoes_frame.pack(pady=(0, 12))

        ctk.CTkButton(
            botoes_frame,
            text="Cancelar",
            width=120,
            height=38,
            corner_radius=18,
            fg_color="#E76F51",
            hover_color="#D95D42",
            text_color="white",
            command=self.destroy,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            botoes_frame,
            text="Abrir",
            width=120,
            height=38,
            corner_radius=18,
            fg_color="#4A90E2",
            hover_color="#3B7CCB",
            text_color="white",
            command=self._confirmar_selecao,
        ).pack(side="left", padx=8)

    def _atualizar_lista(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        self.caminho_entry.delete(0, "end")
        self.caminho_entry.insert(0, self.pasta_atual)

        if os.path.dirname(self.pasta_atual) and os.path.abspath(self.pasta_atual) != os.path.abspath(os.path.dirname(self.pasta_atual)):
            ctk.CTkButton(
                self.lista_frame,
                text="⬆️ Voltar para o diretório anterior",
                width=460,
                height=36,
                corner_radius=12,
                fg_color="#EEF3F9",
                hover_color="#DCE8F8",
                text_color="#1F3A5F",
                anchor="w",
                command=self._voltar_pasta,
            ).pack(fill="x", pady=4)

        try:
            itens = sorted(os.listdir(self.pasta_atual))
        except OSError:
            self.status_label.configure(text="Não foi possível acessar este diretório.")
            return

        for nome in itens:
            caminho_completo = os.path.join(self.pasta_atual, nome)
            if os.path.isdir(caminho_completo):
                ctk.CTkButton(
                    self.lista_frame,
                    text=f"📁 {nome}",
                    width=460,
                    height=36,
                    corner_radius=12,
                    fg_color="#EEF3F9",
                    hover_color="#DCE8F8",
                    text_color="#1F3A5F",
                    anchor="w",
                    command=lambda caminho=caminho_completo: self._abrir_pasta(caminho),
                ).pack(fill="x", pady=4)
            else:
                extensao = os.path.splitext(nome)[1].lower()
                if extensao in {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}:
                    ctk.CTkButton(
                        self.lista_frame,
                        text=f"🖼️ {nome}",
                        width=460,
                        height=36,
                        corner_radius=12,
                        fg_color="#F7FBFF",
                        hover_color="#E6F2FF",
                        text_color="#1F3A5F",
                        anchor="w",
                        command=lambda caminho=caminho_completo: self._selecionar_arquivo(caminho),
                    ).pack(fill="x", pady=4)

    def _voltar_pasta(self):
        pai = os.path.dirname(self.pasta_atual)
        if pai and os.path.isdir(pai):
            self.pasta_atual = pai
            self._atualizar_lista()

    def _abrir_pasta(self, caminho):
        if os.path.isdir(caminho):
            self.pasta_atual = caminho
            self._atualizar_lista()

    def _selecionar_arquivo(self, caminho):
        self.caminho_selecionado = caminho
        self.status_label.configure(text=f"Arquivo selecionado: {os.path.basename(caminho)}")

    def _confirmar_selecao(self):
        if self.caminho_selecionado and os.path.exists(self.caminho_selecionado):
            self.callback(self.caminho_selecionado)
            self.destroy()
        else:
            self.status_label.configure(text="Selecione um arquivo de imagem válido.")


class FilePickerSalvar(ctk.CTkToplevel):
    def __init__(self, master, pasta_inicial, nome_inicial, callback):
        super().__init__(master)
        self.title("Salvar imagem")
        self.geometry("560x500")
        self.configure(fg_color="#F5F7FB")
        self.transient(master)
        self.grab_set()
        self.callback = callback
        self.pasta_atual = os.path.abspath(pasta_inicial)
        self.nome_inicial = nome_inicial
        self._criar_widgets()
        self._atualizar_lista()

    def _criar_widgets(self):
        ctk.CTkLabel(
            self,
            text="Salvar imagem",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1F3A5F",
        ).pack(pady=(16, 8))

        ctk.CTkLabel(
            self,
            text="Escolha a pasta e defina o nome do arquivo para salvar a imagem filtrada.",
            text_color="#4A5A6A",
        ).pack(pady=(0, 10))

        self.caminho_entry = ctk.CTkEntry(
            self,
            width=500,
            border_width=1,
            fg_color="#FFFFFF",
            text_color="#1F3A5F",
        )
        self.caminho_entry.pack(pady=(0, 10))
        self.caminho_entry.insert(0, os.path.join(self.pasta_atual, self.nome_inicial))

        self.lista_frame = ctk.CTkScrollableFrame(
            self,
            width=500,
            height=260,
            fg_color="#FFFFFF",
            corner_radius=16,
        )
        self.lista_frame.pack(pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            self,
            text="Escolha uma pasta ou um nome de arquivo.",
            text_color="#4A5A6A",
        )
        self.status_label.pack(pady=(0, 8))

        botoes_frame = ctk.CTkFrame(self, fg_color="transparent")
        botoes_frame.pack(pady=(0, 12))

        ctk.CTkButton(
            botoes_frame,
            text="Cancelar",
            width=120,
            height=38,
            corner_radius=18,
            fg_color="#E76F51",
            hover_color="#D95D42",
            text_color="white",
            command=self.destroy,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            botoes_frame,
            text="Salvar",
            width=120,
            height=38,
            corner_radius=18,
            fg_color="#2F9E44",
            hover_color="#24863A",
            text_color="white",
            command=self._confirmar_salvamento,
        ).pack(side="left", padx=8)

    def _atualizar_lista(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        self.caminho_entry.delete(0, "end")
        self.caminho_entry.insert(0, os.path.join(self.pasta_atual, self.nome_inicial))

        if os.path.dirname(self.pasta_atual) and os.path.abspath(self.pasta_atual) != os.path.abspath(os.path.dirname(self.pasta_atual)):
            ctk.CTkButton(
                self.lista_frame,
                text="⬆️ Voltar para o diretório anterior",
                width=460,
                height=36,
                corner_radius=12,
                fg_color="#EEF3F9",
                hover_color="#DCE8F8",
                text_color="#1F3A5F",
                anchor="w",
                command=self._voltar_pasta,
            ).pack(fill="x", pady=4)

        try:
            itens = sorted(os.listdir(self.pasta_atual))
        except OSError:
            self.status_label.configure(text="Não foi possível acessar este diretório.")
            return

        for nome in itens:
            caminho_completo = os.path.join(self.pasta_atual, nome)
            if os.path.isdir(caminho_completo):
                ctk.CTkButton(
                    self.lista_frame,
                    text=f"📁 {nome}",
                    width=460,
                    height=36,
                    corner_radius=12,
                    fg_color="#EEF3F9",
                    hover_color="#DCE8F8",
                    text_color="#1F3A5F",
                    anchor="w",
                    command=lambda caminho=caminho_completo: self._abrir_pasta(caminho),
                ).pack(fill="x", pady=4)
            else:
                extensao = os.path.splitext(nome)[1].lower()
                if extensao in {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}:
                    ctk.CTkButton(
                        self.lista_frame,
                        text=f"🖼️ {nome}",
                        width=460,
                        height=36,
                        corner_radius=12,
                        fg_color="#F7FBFF",
                        hover_color="#E6F2FF",
                        text_color="#1F3A5F",
                        anchor="w",
                        command=lambda caminho=caminho_completo: self._selecionar_arquivo(caminho),
                    ).pack(fill="x", pady=4)

    def _voltar_pasta(self):
        pai = os.path.dirname(self.pasta_atual)
        if pai and os.path.isdir(pai):
            self.pasta_atual = pai
            self._atualizar_lista()

    def _abrir_pasta(self, caminho):
        if os.path.isdir(caminho):
            self.pasta_atual = caminho
            self._atualizar_lista()

    def _selecionar_arquivo(self, caminho):
        self.caminho_entry.delete(0, "end")
        self.caminho_entry.insert(0, caminho)
        self.status_label.configure(text=f"Arquivo selecionado: {os.path.basename(caminho)}")

    def _confirmar_salvamento(self):
        caminho = self.caminho_entry.get().strip()
        if not caminho:
            self.status_label.configure(text="Informe um nome de arquivo para salvar.")
            return

        if not os.path.isabs(caminho):
            caminho = os.path.join(self.pasta_atual, caminho)

        if os.path.splitext(caminho)[1].lower() == "":
            caminho = f"{caminho}.png"

        self.callback(caminho)
        self.destroy()


class JanelaPrincipal(ctk.CTkFrame):
    def __init__(self, master, controlador, **kwargs):
        super().__init__(master, fg_color="#F5F7FB", corner_radius=24, **kwargs)
        self.controlador = controlador
        self.pack(fill="both", expand=True)
        self._criar_widgets()

    def _criar_widgets(self):
        titulo = ctk.CTkLabel(
            self,
            text="Filtros de Imagem",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1F3A5F",
        )
        titulo.pack(pady=(40, 24))

        abrir_button = ctk.CTkButton(
            self,
            text="Abrir Imagem",
            width=220,
            height=48,
            corner_radius=22,
            fg_color="#4A90E2",
            hover_color="#3B7CCB",
            text_color="white",
            command=self.controlador.mostrar_janela_visualizar,
        )
        abrir_button.pack(pady=10)

        sair_button = ctk.CTkButton(
            self,
            text="Sair",
            width=220,
            height=48,
            corner_radius=22,
            fg_color="#E76F51",
            hover_color="#D95D42",
            text_color="white",
            command=self.winfo_toplevel().destroy,
        )
        sair_button.pack(pady=10)


class VisualizarImagem(ctk.CTkFrame):
    def __init__(self, master, controlador, **kwargs):
        super().__init__(master, fg_color="#F5F7FB", corner_radius=24, **kwargs)
        self.controlador = controlador
        self.pack(fill="both", expand=True, padx=18, pady=18)
        self._photo_image = None
        self._criar_widgets()
        if self.controlador.imagem_atual_pil is not None:
            self._mostrar_imagem(self.controlador.imagem_atual_pil)

    def _criar_widgets(self):
        titulo = ctk.CTkLabel(
            self,
            text="Selecione uma imagem",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#1F3A5F",
        )
        titulo.pack(pady=(10, 16))

        self.preview_frame = ctk.CTkFrame(
            self,
            width=520,
            height=280,
            fg_color="#23374D",
            corner_radius=18,
        )
        self.preview_frame.pack(pady=(0, 16))
        self.preview_frame.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Nenhuma imagem selecionada",
            font=ctk.CTkFont(size=16),
            text_color="#E8EEF7",
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        instrucao = ctk.CTkLabel(
            self,
            text="Informe um caminho local ou uma URL da imagem:",
            text_color="#4A5A6A",
        )
        instrucao.pack(pady=(0, 8))

        entrada_frame = ctk.CTkFrame(self, fg_color="transparent")
        entrada_frame.pack(pady=(0, 12))

        self.entrada = ctk.CTkEntry(
            entrada_frame,
            width=360,
            placeholder_text="Ex.: /home/user/imagem.png ou https://exemplo.com/imagem.jpg",
            border_width=1,
            fg_color="#FFFFFF",
            text_color="#1F3A5F",
        )
        self.entrada.pack(side="left", padx=(0, 8))
        self.entrada.bind("<Return>", lambda event: self._carregar_imagem())

        procurar_button = ctk.CTkButton(
            entrada_frame,
            text="Procurar",
            width=110,
            height=38,
            corner_radius=18,
            fg_color="#4A90E2",
            hover_color="#3B7CCB",
            text_color="white",
            command=self._procurar_imagem,
        )
        procurar_button.pack(side="left")

        botoes_frame = ctk.CTkFrame(self, fg_color="transparent")
        botoes_frame.pack(pady=(0, 8))

        carregar_button = ctk.CTkButton(
            botoes_frame,
            text="Carregar",
            width=140,
            height=42,
            corner_radius=20,
            fg_color="#4A90E2",
            hover_color="#3B7CCB",
            text_color="white",
            command=self._carregar_imagem,
        )
        carregar_button.pack(side="left", padx=8)

        self.aplicar_button = ctk.CTkButton(
            botoes_frame,
            text="Aplicar Filtro",
            width=140,
            height=42,
            corner_radius=20,
            fg_color="#6C8CD5",
            hover_color="#5A7BC1",
            text_color="white",
            command=self._aplicar_filtro,
            state="disabled",
        )
        self.aplicar_button.pack(side="left", padx=8)

        voltar_button = ctk.CTkButton(
            botoes_frame,
            text="Voltar",
            width=140,
            height=42,
            corner_radius=20,
            fg_color="#E76F51",
            hover_color="#D95D42",
            text_color="white",
            command=self.controlador.mostrar_janela_principal,
        )
        voltar_button.pack(side="left", padx=8)

    def _aplicar_filtro(self):
        if self.controlador.imagem_atual_pil is None:
            CaixaDeMensagem(self.winfo_toplevel(), "Aviso", "Carregue uma imagem antes de aplicar filtros.", tipo="aviso")
            return
        self.controlador.mostrar_janela_filtrar()

    def _procurar_imagem(self):
        diretorio_inicial = self.controlador.imagem_atual_caminho or os.getcwd()
        if os.path.isdir(diretorio_inicial):
            pasta_inicial = diretorio_inicial
        else:
            pasta_inicial = os.path.dirname(diretorio_inicial) or os.getcwd()

        FilePicker(
            self.winfo_toplevel(),
            pasta_inicial,
            callback=self._aplicar_caminho_selecionado,
        )

    def _aplicar_caminho_selecionado(self, caminho):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, caminho)
        self._carregar_imagem()

    def _carregar_imagem(self):
        texto = self.entrada.get().strip()
        if not texto:
            CaixaDeMensagem(self.winfo_toplevel(), "Aviso", "Digite um caminho ou uma URL para carregar uma imagem.", tipo="aviso")
            return

        try:
            imagem_objeto = Imagem(texto)
            caminho_local = imagem_objeto.get_caminho()
            if not os.path.exists(caminho_local):
                raise FileNotFoundError(f"O arquivo '{caminho_local}' não foi encontrado.")

            imagem_pil = Image.open(caminho_local)
            self.controlador.definir_imagem_atual(caminho_local, imagem_pil)
            self._mostrar_imagem(imagem_pil)
            self.aplicar_button.configure(state="normal")
        except Exception as erro:
            self.preview_label.configure(text="Nenhuma imagem selecionada")
            self.preview_label.configure(image=None)
            self._photo_image = None
            self.aplicar_button.configure(state="disabled")
            CaixaDeMensagem(self.winfo_toplevel(), "Erro", str(erro), tipo="erro")

    def _mostrar_imagem(self, imagem_pil):
        imagem_convertida = imagem_pil.convert("RGB")
        imagem_convertida.thumbnail((500, 260), Image.Resampling.LANCZOS)
        imagem_tk = ImageTk.PhotoImage(imagem_convertida)

        self.preview_label.configure(text="")
        self.preview_label.configure(image=imagem_tk)
        self._photo_image = imagem_tk


class FiltrarImagem(ctk.CTkFrame):
    def __init__(self, master, controlador, **kwargs):
        super().__init__(master, fg_color="#F5F7FB", corner_radius=24, **kwargs)
        self.controlador = controlador
        self.pack(fill="both", expand=True, padx=18, pady=18)
        self._photo_image = None
        self.imagem_original = self.controlador.imagem_atual_pil
        self.imagem_resultado = self.imagem_original.copy() if self.imagem_original is not None else None
        self._criar_widgets()
        if self.imagem_original is not None:
            self._mostrar_imagem(self.imagem_original)

    def _criar_widgets(self):
        titulo = ctk.CTkLabel(
            self,
            text="Aplicar filtros",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#1F3A5F",
        )
        titulo.pack(pady=(8, 16))

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(content_frame, fg_color="#EEF3F9", corner_radius=18)
        sidebar.pack(side="left", fill="y", padx=(0, 16))
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="Filtros",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1F3A5F",
        ).pack(pady=(14, 12))

        for classe_filtro, nome_filtro in FILTROS:
            ctk.CTkButton(
                sidebar,
                text=nome_filtro,
                width=180,
                height=40,
                corner_radius=18,
                fg_color="#4A90E2",
                hover_color="#3B7CCB",
                text_color="white",
                command=lambda cls=classe_filtro: self._aplicar_filtro(cls),
            ).pack(pady=6)

        ctk.CTkButton(
            sidebar,
            text="Original",
            width=180,
            height=40,
            corner_radius=18,
            fg_color="#6C8CD5",
            hover_color="#5A7BC1",
            text_color="white",
            command=self._mostrar_original,
        ).pack(pady=(12, 6))

        ctk.CTkButton(
            sidebar,
            text="Baixar",
            width=180,
            height=40,
            corner_radius=18,
            fg_color="#2F9E44",
            hover_color="#24863A",
            text_color="white",
            command=self._baixar_imagem,
        ).pack(pady=6)

        ctk.CTkButton(
            sidebar,
            text="Voltar",
            width=180,
            height=40,
            corner_radius=18,
            fg_color="#E76F51",
            hover_color="#D95D42",
            text_color="white",
            command=self._voltar,
        ).pack(pady=6)

        preview_frame = ctk.CTkFrame(content_frame, width=520, height=320, fg_color="#23374D", corner_radius=18)
        preview_frame.pack(side="left", fill="both", expand=True)
        preview_frame.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="Nenhuma imagem selecionada",
            font=ctk.CTkFont(size=16),
            text_color="#E8EEF7",
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

    def _aplicar_filtro(self, classe_filtro):
        if self.imagem_original is None:
            CaixaDeMensagem(self.winfo_toplevel(), "Aviso", "Carregue uma imagem antes de aplicar filtros.", tipo="aviso")
            return

        filtro = classe_filtro()
        imagem_filtrada = filtro.aplicar(self.imagem_original.copy())
        self.imagem_resultado = imagem_filtrada
        self._mostrar_imagem(imagem_filtrada)

    def _mostrar_original(self):
        if self.imagem_original is None:
            CaixaDeMensagem(self.winfo_toplevel(), "Aviso", "Carregue uma imagem antes de visualizar o original.", tipo="aviso")
            return

        self.imagem_resultado = self.imagem_original.copy()
        self._mostrar_imagem(self.imagem_original)

    def _voltar(self):
        self.controlador.limpar_imagem_atual()
        self.controlador.mostrar_janela_visualizar()

    def _baixar_imagem(self):
        if self.imagem_resultado is None:
            CaixaDeMensagem(self.winfo_toplevel(), "Aviso", "Nenhuma imagem filtrada para baixar.", tipo="aviso")
            return

        pasta_inicial = self.controlador.imagem_atual_caminho or os.getcwd()
        if os.path.isfile(pasta_inicial):
            pasta_inicial = os.path.dirname(pasta_inicial)

        FilePickerSalvar(
            self.winfo_toplevel(),
            pasta_inicial,
            "imagem_filtrada.png",
            callback=self._salvar_imagem_em_caminho,
        )

    def _salvar_imagem_em_caminho(self, caminho):
        try:
            self.imagem_resultado.save(caminho)
            CaixaDeMensagem(self.winfo_toplevel(), "Sucesso", f"Imagem salva em:\n{caminho}", tipo="info")
        except Exception as erro:
            CaixaDeMensagem(self.winfo_toplevel(), "Erro", str(erro), tipo="erro")

    def _mostrar_imagem(self, imagem_pil):
        imagem_convertida = imagem_pil.convert("RGB")
        imagem_convertida.thumbnail((500, 300), Image.Resampling.LANCZOS)
        imagem_tk = ImageTk.PhotoImage(imagem_convertida)

        self.preview_label.configure(text="")
        self.preview_label.configure(image=imagem_tk)
        self._photo_image = imagem_tk


class Aplicacao(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Programa de Filtros de Imagem")
        self.geometry("900x620")
        self.minsize(800, 500)
        self.configure(fg_color="#F5F7FB")

        self.imagem_atual_pil = None
        self.imagem_atual_caminho = None

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.mostrar_janela_principal()

    def definir_imagem_atual(self, caminho, imagem_pil):
        self.imagem_atual_caminho = caminho
        self.imagem_atual_pil = imagem_pil.copy()

    def limpar_imagem_atual(self):
        self.imagem_atual_caminho = None
        self.imagem_atual_pil = None

    def mostrar_janela_principal(self):
        self._limpar_container()
        JanelaPrincipal(self.container, self).pack(fill="both", expand=True)

    def mostrar_janela_visualizar(self):
        self._limpar_container()
        VisualizarImagem(self.container, self).pack(fill="both", expand=True)

    def mostrar_janela_filtrar(self):
        self._limpar_container()
        FiltrarImagem(self.container, self).pack(fill="both", expand=True)

    def _limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()


FILTROS = [
    (FiltroEscalaDeCinza, "Escala de Cinza"),
    (FiltroPretoEBranco, "Preto e Branco"),
    (FiltroNegativo, "Negativo"),
    (FiltroBlurred, "Desfoque"),
    (FiltroContorno, "Contorno"),
]


if __name__ == "__main__":
    app = Aplicacao()
    app.mainloop()

