# Vora Agency — vídeo motion

Vídeo vertical (1080x1920, 30 fps, ~49 s) em estilo motion graphics, montado a partir da locução
`motion/assets/voz.mp3`, com a identidade da Vora Agency.

**Resultados:**
- `output/vora-motion.mp4` — vídeo 1 (locução `voz.mp3`, ~49 s)
- `output/depoimento-maria.mp4` — depoimento da Maria (estilo claro; `motion/v3.html`, sons em `motion/sfx3.py`, foto `assets/maria.jpg`)
- `output/depoimento-maria-estatico.mp4` — versão calma do depoimento (fundo branco, foto da Dra. Paulla Samara, player com o áudio da paciente Maria; `motion/v4.html`, `motion/sfx4.py`)
- `output/visita-dra-paulla.mp4` — edição do vídeo da visita (frames melhorados em `motion/frames5/`, gerados com ffmpeg; `motion/v5.html`, `motion/sfx5.py`)
- `output/conversa-placa-dra-paulla.mp4` — conversa Dra. x paciente sobre a placa (frames desespelhados e melhorados em `motion/frames6/`; `motion/v6.html`, `motion/sfx6.py`)
- `output/vora-motion-2.mp4` — vídeo 2 (locução `voz2.mp3`, ~53 s; animação em `motion/v2.html`, sons em `motion/sfx2.py`)

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

Vídeo 2:

```bash
cd motion
PAGE=v2.html DURATION=53.4 node render.js video ../output/silent2.mp4 4
python3 sfx2.py assets/voz2.mp3 ../output/mix2.wav
ffmpeg -i ../output/silent2.mp4 -i ../output/mix2.wav -c:v libx264 -crf 23 -tune grain -c:a aac -b:a 192k -shortest ../output/vora-motion-2.mp4
```
