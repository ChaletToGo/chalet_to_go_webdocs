# Chalé Básico · Atelier 3D

Página local `/experiencia-3d`, com `noindex, nofollow` e fora do sitemap.

## Conteúdo

O catálogo explícito está em `routes.py`, na pasta `app/3d/chalé_basico`:

- `basico_exterior_modelagem.glb`: modelo inicial do exterior.
- `basico_estrutura_modelagem.glb`: modelo estrutural, carregado somente quando selecionado.
- `planta_chale_basico.jpg`: planta do térreo e mezanino.
- `interior_basico.jpg`, `interior_basico2.jpg`, `interior_basico3.jpg`, `interior_basico4.jpg`: galeria de interiores.

A pasta fornecida não contém fotografias externas separadas. O exterior é apresentado pelo GLB. URLs com acentos são codificadas e relativas à origem, compatíveis com proxy HTTPS.

## Visualizador

Escala, centro e enquadramento calculados por modelo. Trocas descartam geometrias, materiais e texturas do modelo anterior; respostas atrasadas não substituem a escolha mais recente. O corte e a malha são reiniciados em cada troca; a atmosfera escolhida é preservada. Em falhas, é possível selecionar outro modelo. Ambos os GLBs têm uma única malha: não há desmontagem por peças nem medidas reais. O corte é apenas visual, sem fechamento da seção.

Giro, zoom, quatro vistas, tour, três atmosferas, corte, malha, tela cheia e PNG. Galeria e planta usam diálogo com fechamento por Escape, botão ou fundo. Galeria funciona independentemente de WebGL. Imagens abaixo da dobra usam carregamento tardio.

Three.js 0.180.0 via jsDelivr requer internet. GLBs e imagens são servidos pelo próprio app em `/models`. Modelos Draco/KTX2 exigem configurar seus decodificadores antes de usar.

## Executar

```powershell
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8083
```

Abra http://127.0.0.1:8083/experiencia-3d.
