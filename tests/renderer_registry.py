from structivize.renderers.chemistry import RendererChemMol

# from structivize.renderers.music import RendererMusicAbc

RENDERER_REGISTRY = [
    {
        "renderer_cls": RendererChemMol,
        "domain": "chemistry",
        "renderer_name": "chem_mol",
        "sample_filename": "sample.mol"
    },
    # {
    #     "renderer_cls": RendererChemInchi,
    #     "domain": "chemistry",
    #     "renderer_name": "chem_inchi",
    #     "sample_filename": "sample.inchi"
    # },
    # {
    #     "renderer_cls": RendererMusicAbc,
    #     "domain": "music",
    #     "renderer_name": "music_abc",
    #     "sample_filename": "sample.abc"
    # },
    # Add more renderers here
]
