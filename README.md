# Vora Agency — vídeo motion

Vídeo vertical (1080x1920, 30 fps, ~49 s) em estilo motion graphics, montado a partir da locução
`motion/assets/voz.mp3`, com a identidade da Vora Agency.

**Resultado:** `output/vora-motion.mp4`

## Como foi feito

| Arquivo | Função |
| --- | --- |
| `motion/index.html` | Toda a animação (cenas, câmera, cursor, legendas palavra a palavra, logo). É determinística: `render(t)` desenha o quadro do instante `t`. |
| `motion/words.json` | Transcrição da locução com tempo de cada palavra (gerada com Whisper). Sincroniza legendas e animações. |
| `motion/render.js` | Abre a página no Chromium (Playwright), captura quadro a quadro e codifica em H.264 com ffmpeg. |
| `motion/sfx.py` | Sintetiza efeitos sonoros (whooshes, cliques, digitação, pops, riser, impacto, brilho) e trilha ambiente, e mixa com a voz (com ducking). |

## Gerar de novo

```bash
cd motion
npm i playwright            # ou use um Playwright já instalado
pip install numpy scipy
node render.js video ../output/silent.mp4 4
python3 sfx.py assets/voz.mp3 ../output/mix.wav
ffmpeg -i ../output/silent.mp4 -i ../output/mix.wav -c:v copy -c:a aac -b:a 192k -shortest ../output/vora-motion.mp4
```

Pré-visualizar quadros: `node render.js stills 2.5 12.9 43.8` (salva PNGs em `motion/stills/`).
