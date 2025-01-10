import subprocess
import json

def obter_codec_e_bit_depth(video_url):
    try:
        # Executa o comando ffprobe e captura a saída em JSON
        comando = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            video_url
        ]
        resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Analisa o JSON retornado
        info_video = json.loads(resultado.stdout)
        codec = None
        bit_depth = None

        for stream in info_video.get("streams", []):
            if stream.get("codec_type") == "video":
                codec = stream.get("codec_name")
                bit_depth = stream.get("bits_per_raw_sample") or stream.get("pix_fmt")
                break

        return codec, bit_depth
    except Exception as e:
        return None, f"Erro ao obter codec: {e}"

# URL do vídeo
video_url = "http://wateronplay.com:80/movie/Veron23/Veron2023/241905.mp4"
codec, bit_depth = obter_codec_e_bit_depth(video_url)

if codec:
    print(f"Codec do vídeo: {codec}")
    if bit_depth:
        print(f"Bit Depth (ou Pixel Format): {bit_depth}")
    else:
        print("Bit Depth não disponível.")
else:
    print(bit_depth)
