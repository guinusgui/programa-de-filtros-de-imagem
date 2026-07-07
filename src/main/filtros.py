import tkinter as tk
import numpy as np
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps,ImageFilter
from abc import ABC, abstractmethod

class FiltroBase(ABC):
    #CLasse Abstrata para indicar o método "aplicar", presente em todas as classes filtro.
    @abstractmethod
    def aplicar(self, imagem: Image.Image) -> Image.Image:
        pass
    def converter(self, imagem: Image.Image) -> ImageTk.PhotoImage:
        return ImageTk.PhotoImage(imagem)
    def salvar(self, imagem: Image.Image, caminho: str) -> None:
        try:
            if caminho.lower().endswith(('.jpg', '.jpeg')):
                if (imagem.mode in ('RGBA', 'LA')) or (imagem.mode == 'P' and 'transparency' in imagem.info):
                    imagem_rgba = imagem.convert('RGBA')
                    fundo_branco = Image.new("RGB", imagem_rgba.size, (255, 255, 255))
                    #Fundo branco para completar as regiões em que a imagem está transparente.
                    fundo_branco.paste(imagem, mask=imagem_rgba.split()[-1])
                    imagem = fundo_branco
                else:
                    # Garante que a imagem está em modo RGB para salvar em JPG
                    imagem = imagem.convert("RGB")


            imagem.save(caminho)
        except FileNotFoundError:
            raise FileNotFoundError("A pasta informada não existe ou não foi encontrada.") from None
        except PermissionError:
            raise PermissionError("Você não tem permissão para salvar nesse local.") from None
        except ValueError:
            raise ValueError("Formato de arquivo inválido.") from None
        except OSError as erro:
            raise OSError(f"Não foi possivel salvar a imagem. Detalhes: {erro}") from erro

    

class FiltroEscalaDeCinza(FiltroBase):
    def aplicar(self, imagem: Image.Image) -> Image.Image:
        return ImageOps.grayscale(imagem)
    
class FiltroPretoEBranco(FiltroBase):
    def aplicar(self, imagem: Image.Image) -> Image.Image:
        imagem_cinza = ImageOps.grayscale(imagem) 
        #Transformando imagem em escala de cinza para poder, após, transforma-la em preto e branco usando um ponto de corte ( Metade da escala)
        return imagem_cinza.point(
            lambda pixel: 255 if pixel >= 128 else 0
        ) #.point aplica essa função em todos os pixels da imagem, conforme seus valores na escala de cinza
    
class FiltroNegativo(FiltroBase):
     def aplicar(self, imagem: Image.Image) -> Image.Image:
        tem_alpha = imagem.mode in ('RGBA', 'LA') or (
            imagem.mode == 'P' and 'transparency' in imagem.info
        )

        if tem_alpha:
            imagem_rgba = imagem.convert('RGBA')
            r, g, b, a = imagem_rgba.split()
            rgb_invertido = ImageOps.invert(Image.merge('RGB', (r, g, b)))
            r2, g2, b2 = rgb_invertido.split()
            return Image.merge('RGBA', (r2, g2, b2, a))
            """
            Caso a imagem tenha o canal alpha ou seja do modo 'Pallete' com transparência guardada em info['transparency'], 
            ela irá fazer uma imagem com filtro negativo usando apenas o RGB e depois unindo novamente com o canal alpha.
            Assim, as cores ficam negativadas, mas a transparência se mantém."""
        else:
            return ImageOps.invert(imagem.convert('RGB'))

class FiltroBlurred(FiltroBase):
    def aplicar(self, imagem: Image.Image) -> Image.Image:
        """
        Aplica um desfoque na imagem usando uma Matriz de Convolução
        """
        imagem_rgb = imagem.convert("RGB")

        # O Kernel é uma matriz 3x3 que vai deslizar por toda a imagem.
        # Aqui, colocamos o peso 1 para o pixel central e todos os seus 8 vizinhos.
        # kernel_desfoque = ImageFilter.Kernel(
        #     size=(3, 3),
        #     kernel=(
        #         1, 1, 1,
        #         1, 1, 1,
        #         1, 1, 1
        #     ),
        #     scale=9, # Dividimos o resultado por 9 para calcular a "Média" das cores
        #     offset=0
        # )
   
        kernel_desfoque = ImageFilter.Kernel(
            size=(5, 5),
            kernel=(
                1, 1, 1, 1, 1,
                1, 1, 1, 1, 1,
                1, 1, 1, 1, 1,
                1, 1, 1, 1, 1,
                1, 1, 1, 1, 1
            ),
            scale=25, 
            offset=0
        )
        
        return imagem_rgb.filter(kernel_desfoque)

class FiltroContorno(FiltroBase):
    def aplicar(self, imagem: Image.Image) -> Image.Image:
        """
        Destaca as bordas da imagem usando o Operador de Laplace (Laplacian Filter)
        """
        # Para achar contornos com mais precisão, é melhor converter para tons de cinza primeiro
        imagem_rgb = imagem.convert("RGB")
        
        # Transforma a imagem em uma matriz numérica
        matriz_pixels = np.array(imagem_rgb)
        
        # Separa os canais de cor extraindo as fatias da matriz
        canal_red   = matriz_pixels[:, :, 0] # Canal 0 = Vermelho
        canal_green = matriz_pixels[:, :, 1] # Canal 1 = Verde
        canal_blue  = matriz_pixels[:, :, 2] # Canal 2 = Azul
        
        # Aplica a fórmula de luminância (pesos baseados na percepção humana)
        matriz_cinza = (canal_red * 0.299) + (canal_green * 0.587) + (canal_blue * 0.114)
        
        # Converte os números calculados de volta para inteiros de 8 bits (0 a 255)
        matriz_cinza = matriz_cinza.astype(np.uint8)
        
        # Reconstrói a imagem do Pillow a partir da nossa matriz calculada
        imagem_cinza_pil = Image.fromarray(matriz_cinza, mode="L")
        
        # Matriz de detecção de bordas. 
        # O pixel central tem peso 8, e os vizinhos puxam para o lado negativo (-1).
        # Offset de 128 mantém o fundo cinza metálico para evitar perda de bordas negativas.
        kernel_bordas = ImageFilter.Kernel(
            size=(3, 3),
            kernel=(
                -1, -1, -1,
                -1,  8, -1,
                -1, -1, -1
            ),
            scale=1,
            offset=128
        )
        
        imagem_contorno = imagem_cinza_pil.filter(kernel_bordas)
        
        return imagem_contorno
     
 
