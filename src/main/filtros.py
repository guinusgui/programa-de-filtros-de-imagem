import os
import tkinter as tk
import numpy as np
import cv2
import requests
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps, ImageFilter
from abc import ABC, abstractmethod
from urllib.parse import urlparse

class Download:

    @staticmethod
    def baixar_imagem(url: str, diretorio_destino: str = "."):
        """
        Faz o download da imagem a partir de uma URL e a salva localmente.
        Retorna o caminho do arquivo salvo.
        """
        print("Iniciando o download da imagem...")
        try:
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            resposta = requests.get(url, headers=headers, timeout=15)
            resposta.raise_for_status() 
            
            # descobrir o nome original do arquivo pela URL
            caminho_url = urlparse(url).path
            nome_arquivo = os.path.basename(caminho_url)
            
            # lê o cabeçalho do arquivo caso pela URL não dê certo
            tipo_conteudo = resposta.headers.get('Content-Type', '').lower()
            
            if not (nome_arquivo.lower().endswith('.jpg') or nome_arquivo.lower().endswith('.png') or nome_arquivo.lower().endswith('.jpeg')):
                if 'jpeg' in tipo_conteudo or 'jpg' in tipo_conteudo:
                    nome_arquivo = "imagem_baixada.jpg"
                elif 'png' in tipo_conteudo:
                    nome_arquivo = "imagem_baixada.png"
                else:
                    raise ValueError("A URL fornecida não aponta para uma imagem .jpg ou .png válida.")
            
            caminho_completo = os.path.join(diretorio_destino, nome_arquivo)
            

            with open(caminho_completo, 'wb') as arquivo:
                arquivo.write(resposta.content)
                
            print(f" Download concluído! Arquivo salvo em: {caminho_completo}")
            return caminho_completo
            
        except requests.exceptions.MissingSchema:
            raise ValueError("URL inválida. Certifique-se de incluir 'http://' ou 'https://'.")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Erro de conexão. Verifique sua internet ou se a URL está no ar.")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"O servidor recusou o acesso (Erro HTTP {resposta.status_code}).")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Erro inesperado ao acessar a URL: {e}")


class Imagem:
    """
    Representa o arquivo de imagem que será processado pelo programa.
    Garante que o arquivo seja local e tenha a extensão correta.
    """
    def __init__(self, caminho_ou_url: str):
        self._entrada_usuario = caminho_ou_url
        self.caminho_local = None
        self._preparar_imagem()

    def _preparar_imagem(self):
        entrada = self._entrada_usuario.strip()
        
        if entrada.startswith("http://") or entrada.startswith("https://"):
            self.caminho_local = Download.baixar_imagem(entrada)
        else:
            self.caminho_local = entrada
            
        self._validar_arquivo()

    def _validar_arquivo(self):
        if not os.path.exists(self.caminho_local):
            raise FileNotFoundError(f"O arquivo '{self.caminho_local}' não foi encontrado no diretório local.")
            
        _, extensao = os.path.splitext(self.caminho_local.lower())
        
        if extensao not in ['.jpg', '.jpeg', '.png']:
            raise ValueError(f"Formato '{extensao}' inválido. O programa aceita apenas imagens .jpg, .jpeg ou .png.")
            
    def get_caminho(self) -> str:
        return self.caminho_local


class FiltroBase(ABC):
    #CLasse Abstrata para indicar o método "aplicar", presente em todas as classes filtro.
    @abstractmethod
    def aplicar(self, imagem: Image.Image) -> Image.Image:
        raise NotImplementedError
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
    
class FiltroCartoon():
    """
        Uma imagem catoonizada é, sobretudo, uma imagem com menos detalhes.
        
        Uma características são cores chapadas. Para isso, a imagem será suavizada para reduzir seus detalhes. Então,
        será aplicado uma quantização - clusterização k-means - para reduzir a diversidade de cor e atingir o efeito desejado.

        Outro caractere são as bordas bem definidas. Para isso, serão identificadas as bordas da imagem
        Essas serão binarizadas visando o efeito chapado e aplicadas sobre a imagem quantizada.
    """

    def __init__(self,
                 gaussianKernel=3,
                 k=16,
                 maxIt=10
                 ):
        self.gaussianKernel = gaussianKernel
        self.k = k
        self.maxIt = maxIt

        self.kMeansCriteria = ( cv2.TERM_CRITERIA_MAX_ITER, self.maxIt, None) 

    def aplicar(self, imagem: Image.Image) -> Image.Image:
        img = np.array(imagem.convert("RGB"))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Suavização ---
        img_blur = cv2.GaussianBlur(img, (self.gaussianKernel, self.gaussianKernel), 0)

        # Cores Chapadas por K-Means ---
        flatten = np.float32(img.reshape(-1, 3))
        
        _, classificacoes, centroides = cv2.kmeans(flatten, self.k, None, self.kMeansCriteria, 10, cv2.KMEANS_RANDOM_CENTERS) 
        centroides = np.uint8(centroides) 
        segmented_data = centroides[classificacoes.flatten()] 
        coresQuantizadas = segmented_data.reshape((img.shape))

        # Bordas bem definidas ---
        bordas = cv2.Canny(img_blur, 100, 65)

        _, bordas = cv2.threshold(
            bordas,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        # Unindo cores chapadas com bordas ---
        bordas = cv2.cvtColor(bordas, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(coresQuantizadas, bordas)

        # Convertendo para PIL ---
        cartoon = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cartoon)
