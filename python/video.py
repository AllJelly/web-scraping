# import cv2

# def get_video_metadata(video_url):
#     # Abra o vídeo usando OpenCV
#     cap = cv2.VideoCapture(video_url)
    
#     # Verifique se o vídeo foi aberto corretamente
#     if not cap.isOpened():
#         raise ValueError("Não foi possível abrir o vídeo.")

#     # Obtenha metadados
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

#     # Libere o objeto de captura
#     cap.release()

#     return {
#         "Largura": width,
#         "Altura": height,
#         "FPS": fps,
#         "Contagem de Quadros": frame_count
#     }

# video_url = 'http://trutrend.net:80/movie/746163457/5008672/525714.mp4'
 
# metadata = get_video_metadata(video_url)
# print(metadata)

from moviepy.editor import VideoFileClip

def get_video_metadata_moviepy(video_url):
    try:
        # Abra o vídeo usando moviepy
        clip = VideoFileClip(video_url)
        
        # Obtenha metadados
        width, height = clip.size
        fps = clip.fps
        duration = clip.duration
        frame_count = int(fps * duration)
        
        # Feche o vídeo
        clip.close()
        
        return {
            "Largura": width,
            "Altura": height,
            "FPS": fps,
            "Contagem de Quadros": frame_count
        }
    except Exception as e:
        print("Erro ao obter metadados:", e)
        return None

video_url = 'http://wateronplay.com:80/series/Veron23/Veron2023/110233.mp4'
metadata = get_video_metadata_moviepy(video_url)
print(metadata)
# import requests

# def check_stream(url):
#     try:
#         # Enviar uma requisição GET para a URL
#         response = requests.get(url, timeout=5)  # O timeout é de 5 segundos
        
#         # Verificar se a resposta foi bem-sucedida
#         if response.status_code == 200:
#             print(f"O link {url} está funcionando.")
#             return True
#         else:
#             print(f"O link {url} não está funcionando. Código de status: {response.status_code}")
#             return False
#     except requests.exceptions.RequestException as e:
#         print(f"Ocorreu um erro ao acessar o link {url}: {e}")
#         return False

# # Exemplo de uso
# url = "http://wateronplay.com:80/Veron23/Veron2023/365234"
# check_stream(url)
