import os
import base64
import streamlit as st
import openai
import numpy as np

from openai import OpenAI
from PIL import Image
from streamlit_drawable_canvas import st_canvas


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="El Bosque de las Hadas",
    page_icon="🧚",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "full_response" not in st.session_state:
    st.session_state.full_response = ""

if "base64_image" not in st.session_state:
    st.session_state.base64_image = ""

if "story" not in st.session_state:
    st.session_state.story = ""


# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>

    /* Fondo general */
    .stApp {
        background:
            radial-gradient(circle at 10% 10%, #E8F5E9 0%, transparent 25%),
            radial-gradient(circle at 90% 20%, #EDE7F6 0%, transparent 25%),
            radial-gradient(circle at 50% 100%, #E0F2F1 0%, transparent 30%),
            #F7FBF4;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Título */
    .titulo {
        text-align: center;
        font-size: 48px;
        font-weight: 800;
        color: #315C4A;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }

    .subtitulo {
        text-align: center;
        font-size: 18px;
        color: #6B7D70;
        margin-top: 5px;
        margin-bottom: 10px;
    }

    .hojitas {
        text-align: center;
        font-size: 25px;
        margin-bottom: 25px;
    }

    /* Tarjetas */
    .tarjeta {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 25px;
        border-radius: 25px;
        border: 2px solid #DCEBDD;
        box-shadow: 0px 8px 25px rgba(61, 92, 72, 0.08);
        margin-bottom: 20px;
    }

    .tarjeta-titulo {
        color: #315C4A;
        font-size: 21px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .texto-suave {
        color: #728276;
        font-size: 15px;
    }

    /* Botón */
    .stButton > button {
        width: 100%;
        border-radius: 15px;
        border: 2px solid #A8C9B3;
        background-color: #DDEFE1;
        color: #315C4A;
        font-weight: 700;
        padding: 10px;
        transition: 0.2s;
    }

    .stButton > button:hover {
        background-color: #C9E4CF;
        border-color: #8FB79D;
    }

    /* Inputs */
    div[data-baseweb="select"] > div {
        border-radius: 12px;
        border: 1px solid #C8DCCB;
        background-color: #FFFFFF;
    }

    /* Slider */
    div[data-baseweb="slider"] > div > div > div {
        background-color: #87A98F;
    }

    /* Color picker */
    button[data-testid="stColorPickerButton"] {
        border-radius: 10px;
        border: 1px solid #C8DCCB;
    }

    /* Resultado mágico */
    .resultado {
        background: linear-gradient(
            135deg,
            #F2EAF7,
            #E7F3EA
        );
        border: 2px solid #D6C7DF;
        border-radius: 25px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0px 8px 25px rgba(70, 60, 80, 0.08);
    }

    .resultado-titulo {
        color: #665176;
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    /* Historia */
    .historia {
        background-color: #FFF8E8;
        border: 2px solid #EADCB8;
        border-radius: 25px;
        padding: 25px;
        margin-top: 20px;
    }

    .footer {
        text-align: center;
        color: #8B9A8D;
        font-size: 13px;
        margin-top: 30px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    '<div class="titulo">🧚 El Bosque de las Hadas</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'En este bosque cada dibujo esconde una pequeña criatura mágica.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hojitas">🌿 ✨ 🍄 🌙 🍃</div>',
    unsafe_allow_html=True
)


# ============================================================
# INSTRUCCIONES
# ============================================================

st.markdown(
    '<div class="tarjeta">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="tarjeta-titulo">🌱 Crea tu propia hada</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="texto-suave">'
    'Dibuja un hada como tú quieras. Puedes hacerle alas grandes o pequeñas, '
    'ponerle un vestido, cabello, flores, estrellas o cualquier detalle que '
    'imagines. No hay una forma correcta de dibujarla.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# HERRAMIENTAS DE DIBUJO
# ============================================================

st.markdown(
    '<div class="tarjeta">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="tarjeta-titulo">🎨 Dale vida a tu hada</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:

    drawing_mode = st.selectbox(
        "🖌️ Herramienta",
        (
            "freedraw",
            "line",
            "rect",
            "circle",
            "transform",
            "polygon",
            "point"
        ),
        format_func=lambda herramienta: {
            "freedraw": "✏️ Dibujar",
            "line": "📏 Línea",
            "rect": "⬜ Rectángulo",
            "circle": "⭕ Círculo",
            "transform": "🔄 Transformar",
            "polygon": "🔷 Polígono",
            "point": "✨ Punto"
        }[herramienta]
    )

with col2:

    stroke_width = st.slider(
        "🌿 Grosor del trazo",
        min_value=1,
        max_value=30,
        value=5,
        step=1
    )

with col3:

    stroke_color = st.color_picker(
        "🎨 Color de tu hada",
        "#315C4A"
    )

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# FONDO DEL BOSQUE
# ============================================================

col1, col2 = st.columns([1, 2])

with col1:

    st.markdown(
        '<div class="tarjeta">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="tarjeta-titulo">🌳 Elige el ambiente</div>',
        unsafe_allow_html=True
    )

    bg_color = st.color_picker(
        "Color del bosque",
        "#F7FBF4"
    )

    st.markdown(
        '<div class="texto-suave">'
        'Elige el color que tendrá el fondo de tu dibujo.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# LIENZO
# ============================================================

st.markdown(
    '<div class="tarjeta">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="tarjeta-titulo">🧚 Tu rincón mágico</div>',
    unsafe_allow_html=True
)

canvas_result = st_canvas(
    fill_color="rgba(180, 220, 190, 0.25)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=450,
    width=700,
    drawing_mode=drawing_mode,
    key="canvas"
)

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# API KEY
# ============================================================

with st.expander("🔐 Configuración"):

    ke = st.text_input(
        "Ingresa tu clave de OpenAI",
        type="password"
    )

    if ke:
        os.environ["OPENAI_API_KEY"] = ke


api_key = os.environ.get("OPENAI_API_KEY", "")


# ============================================================
# FUNCIÓN PARA CODIFICAR IMAGEN
# ============================================================

def encode_image_to_base64(image_path):

    try:

        with open(image_path, "rb") as image_file:

            encoded = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

            return encoded

    except FileNotFoundError:

        return None


# ============================================================
# BOTÓN DE ANÁLISIS
# ============================================================

st.markdown(
    '<div class="tarjeta">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="tarjeta-titulo">🔮 Descubre qué hada dibujaste</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="texto-suave">'
    'Cuando termines tu dibujo, deja que el bosque descubra qué tipo de hada vive en él.'
    '</div>',
    unsafe_allow_html=True
)

analyze_button = st.button(
    "✨ Descubrir mi hada"
)

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# ANÁLISIS DE LA IMAGEN
# ============================================================

if analyze_button:

    if not api_key:

        st.warning(
            "🌱 Primero necesitas ingresar tu clave de OpenAI."
        )

    else:

        try:

            # Intentamos obtener la imagen del canvas.
            # Si todavía no hay dibujo, la librería puede lanzar RuntimeError.
            try:
                image_data = canvas_result.image_data
            except RuntimeError:
                image_data = None

            if image_data is None:

                st.warning(
                    "🧚 Tu hada todavía no ha aparecido. "
                    "Dibuja algo en el lienzo primero."
                )

            else:

                with st.spinner(
                    "✨ Las hadas están observando tu dibujo..."
                ):

                    # Convertir canvas a imagen
                    input_numpy_array = np.array(
                        image_data
                    )

                    input_image = Image.fromarray(
                        input_numpy_array.astype("uint8")
                    ).convert("RGBA")

                    input_image.save("hada.png")

                    # Convertir imagen a base64
                    base64_image = encode_image_to_base64(
                        "hada.png"
                    )

                    st.session_state.base64_image = base64_image

                    # ------------------------------------------------
                    # PROMPT PARA LA IA
                    # ------------------------------------------------

                    prompt_text = """
                    Estamos en un bosque mágico donde los niños pueden
                    crear sus propias hadas mediante dibujos.

                    Analiza la imagen que hizo el niño.

                    No juzgues la calidad artística del dibujo.
                    No digas que está mal dibujado.
                    Interpreta el dibujo de forma imaginativa y positiva.

                    Identifica características visibles como:
                    - presencia y forma de alas
                    - cantidad de detalles
                    - formas predominantes
                    - tamaño de las figuras
                    - líneas rectas o curvas
                    - colores utilizados
                    - elementos naturales como flores, hojas, estrellas,
                      lunas, árboles o plantas
                    - cualquier otro elemento reconocible

                    A partir de esos elementos, asigna al personaje UNO
                    de estos tipos de hada:

                    1. Hada del Bosque
                    2. Hada de las Flores
                    3. Hada de las Estrellas
                    4. Hada de la Luna
                    5. Hada de los Sueños
                    6. Hada de la Naturaleza

                    Si el dibujo no representa claramente un hada,
                    interpreta los elementos presentes de la manera más
                    creativa posible y conviértelo igualmente en un
                    personaje fantástico.

                    Responde en español y con un tono alegre, mágico
                    y apropiado para niños.

                    Usa exactamente esta estructura:

                    🧚 TU HADA ES:
                    [nombre del tipo de hada]

                    ✨ ¿CÓMO ES?
                    [2 o 3 frases sobre el personaje basadas en el dibujo]

                    🌿 SU PODER:
                    [un poder mágico relacionado con el dibujo]

                    💫 SU DETALLE ESPECIAL:
                    [un elemento del dibujo que la hace especial]

                    No inventes características que contradigan claramente
                    lo que aparece en la imagen.
                    """

                    # ------------------------------------------------
                    # OPENAI
                    # ------------------------------------------------

                    client = OpenAI(
                        api_key=api_key
                    )

                    response = client.chat.completions.create(

                        model="gpt-4o-mini",

                        messages=[

                            {
                                "role": "user",

                                "content": [

                                    {
                                        "type": "text",
                                        "text": prompt_text
                                    },

                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url":
                                            f"data:image/png;base64,{base64_image}"
                                        }
                                    }

                                ]
                            }

                        ],

                        max_tokens=500
                    )

                    full_response = (
                        response.choices[0]
                        .message
                        .content
                    )

                    # Guardar resultado
                    st.session_state.full_response = full_response
                    st.session_state.analysis_done = True


                    # ------------------------------------------------
                    # MOSTRAR RESULTADO
                    # ------------------------------------------------

                    st.markdown(
                        '<div class="resultado">',
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        '<div class="resultado-titulo">'
                        '🔮 El bosque ha descubierto tu hada'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        full_response
                    )

                    st.markdown("</div>", unsafe_allow_html=True)


        except Exception as e:

            st.error(
                f"🌧️ El bosque tuvo un pequeño problema: {e}"
            )


# ============================================================
# CREAR HISTORIA
# ============================================================

if st.session_state.analysis_done:

    st.markdown(
        '<div class="tarjeta">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="tarjeta-titulo">'
        '📖 ¿Quieres conocer la historia de tu hada?'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="texto-suave">'
        'Puedes convertir tu dibujo en el comienzo de una pequeña aventura.'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button("🌙 Crear historia mágica"):

        with st.spinner(
            "🍄 Las hojas están contando tu historia..."
        ):

            story_prompt = f"""
            Esta es la descripción de un hada creada por un niño:

            "{st.session_state.full_response}"

            Escribe una historia infantil breve, divertida y mágica
            protagonizada por esta hada.

            La historia debe:
            - tener aproximadamente 3 párrafos
            - ser apropiada para niños
            - tener un pequeño conflicto o aventura
            - terminar de manera positiva
            - relacionarse con el bosque
            - utilizar el poder y las características del hada
            - ser fácil de entender
            - no dar miedo

            No hables sobre inteligencia artificial ni sobre el proceso
            de análisis del dibujo.
            """

            try:

                story_response = client.chat.completions.create(

                    model="gpt-4o-mini",

                    messages=[
                        {
                            "role": "user",
                            "content": story_prompt
                        }
                    ],

                    max_tokens=500
                )

                story = (
                    story_response
                    .choices[0]
                    .message
                    .content
                )

                st.session_state.story = story

            except Exception as e:

                st.error(
                    f"🍃 No pudimos crear la historia: {e}"
                )

    # Mostrar historia si existe
    if st.session_state.story:

        st.markdown(
            '<div class="historia">',
            unsafe_allow_html=True
        )

        st.markdown(
            "### 📖 La historia de tu hada"
        )

        st.write(
            st.session_state.story
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.markdown(
    '<div class="footer">'
    '🌿 Cada dibujo es una puerta a un pequeño mundo mágico ✨'
    '</div>',
    unsafe_allow_html=True
)
