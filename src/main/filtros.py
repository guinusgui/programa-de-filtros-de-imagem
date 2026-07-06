import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
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
     
    


     
 
