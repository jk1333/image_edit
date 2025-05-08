import streamlit as st
import io
import PIL, PIL.Image
from PIL import ImageDraw
from streamlit_img_label import st_img_label
from streamlit_img_label.manage import ImageManager
from google.cloud import aiplatform
from google import genai
from google.genai import types

st.set_page_config(layout='wide')

LANGUAGE = ['en']
RATIO = ["1:1", "9:16", "16:9", "4:3", "3:4"]
UPSCALE = ["x2", "x4"]
MAX_IMAGE_EDIT_SIZE = 700
GENERATION_MODELS = ["imagen-3.0-generate-002", "imagen-3.0-fast-generate-001"]
EDIT_MODEL = "imagen-3.0-capability-001"
UPSCALE_MODEL = "imagen-3.0-generate-002"
GUIDANCE_SCALE = [10.0, 5.0, 20.0]
BASE_STEPS = 75
DILATION = 0.03

@st.cache_resource
def get_client():
    return genai.Client(vertexai=True,
        project=aiplatform.initializer.global_config.project,
        location=aiplatform.initializer.global_config.location)

client = genai.Client(vertexai=True,
        project=aiplatform.initializer.global_config.project,
        location=aiplatform.initializer.global_config.location)

if 'generated_image' not in st.session_state:
    st.session_state['generated_image'] = []

if 'selected_image' not in st.session_state:
    st.session_state['selected_image'] = None

if 'resized_image' not in st.session_state:
    st.session_state['resized_image'] = None

if 'origin_rects' not in st.session_state:
    st.session_state['origin_rects'] = []

def get_image_bytes(roi_img):
    img_byte_arr = io.BytesIO()
    roi_img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def get_rect_from_vertices(vertices, label):
    min_x = 9999
    min_y = 9999
    max_x = -1
    max_y = -1
    for vertex in vertices:
        if vertex.x < min_x:
            min_x = vertex.x
        if vertex.y < min_y:
            min_y = vertex.y
        if vertex.x > max_x:
            max_x = vertex.x
        if vertex.y > max_y:
            max_y = vertex.y
    return {'left': min_x, 'top': min_y, 
            'width': max_x - min_x, 'height': max_y - min_y,
            'label': label}

class MemoryImageManager(ImageManager):
    def __init__(self, image, rects):
        """initiate module"""
        self._filename = "memory"
        self._img = image
        self._rects = rects
        self._resized_ratio_w = 1
        self._resized_ratio_h = 1

    def revoke_resized_rect(self, rects):
        return_rects = []
        for rect in rects:
            revoked_rect = {}
            revoked_rect["left"] = int(rect["left"] * self._resized_ratio_w)
            revoked_rect["width"] = int(rect["width"] * self._resized_ratio_w)
            revoked_rect["top"] = int(rect["top"] * self._resized_ratio_h)
            revoked_rect["height"] = int(rect["height"] * self._resized_ratio_h)
            if "label" in rect:
                revoked_rect["label"] = rect["label"]
            return_rects.append(revoked_rect)
        return return_rects
    
def rects_to_bbox(rects):
    return_rects = []
    for rect in rects:
        return_rects.append([rect["left"], rect["top"], rect["left"] + rect["width"], rect["top"] + rect["height"]])
    return return_rects

def generate_image(model, language, prompt, negative_prompt, ratio, seed = 0, enhance_prompt = True):
    response = get_client().models.generate_images(
        model = model,
        prompt = prompt,
        config = types.GenerateImagesConfig(
            negative_prompt = negative_prompt,
            number_of_images = 4,
            aspect_ratio = ratio,
            include_rai_reason = True,
            language = language,
            add_watermark = True,
            #seed = seed,
            enhance_prompt = enhance_prompt,
            safety_filter_level = types.SafetyFilterLevel.BLOCK_ONLY_HIGH,
            person_generation = types.PersonGeneration.ALLOW_ADULT,
            output_mime_type = "image/png"
        )
    )
    return response.generated_images

def upscale_image(model, image, upscale_factor = 'x2'):
    response = get_client().models.upscale_image(
        model = model,
        image = image,
        upscale_factor = upscale_factor,
        config = types.UpscaleImageConfig(
            include_rai_reason = True,
            output_mime_type = "image/png"
        )
    )
    return response.generated_images[0]

def edit_image_mask(model,
    input_image: types.Image,
    mask_image: types.Image,
    language = None,
    prompt = None,
    negative_prompt = None,
    edit_mode = None,
    mask_mode = None,
    guidance_scale = None,
    base_steps = None,
    dilation = None
):
    response = client.models.edit_image(
        model = model,
        prompt = prompt,
        reference_images = [
            types.RawReferenceImage(
                reference_id = 1,
                reference_image = input_image,
            ),
            types.MaskReferenceImage(
                reference_id = 2,
                reference_image = mask_image,
                config = types.MaskReferenceConfig(
                    mask_mode = mask_mode,
                    mask_dilation = dilation
                )
            )
        ],
        config = types.EditImageConfig(
            negative_prompt = negative_prompt,
            number_of_images = 4,
            guidance_scale = guidance_scale,
            safety_filter_level = types.SafetyFilterLevel.BLOCK_ONLY_HIGH,
            person_generation = types.PersonGeneration.ALLOW_ADULT,
            include_rai_reason = True,
            output_mime_type = "image/png",
            language = language,
            edit_mode = edit_mode,
            base_steps = base_steps
        )
    )
    return response.generated_images

col_left, col_right = st.columns(2)

with col_left:
    cols = st.columns([3, 1])
    generation_text = cols[0].text_area("Prompt to generate images")
    negative_text = cols[1].text_area("Negative prompt")
    uploaded_file = st.file_uploader("Choose a image file to edit", type=['png', 'jpg'])
    image_label = st.container()

    if uploaded_file is not None:
        st.session_state['selected_image'] = MemoryImageManager(PIL.Image.open(uploaded_file), [])
        st.session_state['resized_image'] = st.session_state['selected_image'].resizing_img(MAX_IMAGE_EDIT_SIZE, MAX_IMAGE_EDIT_SIZE)
        
    if st.session_state['resized_image'] != None:
        #    st.session_state['origin_rects'] = localize_objects(uploaded_file.getvalue(), option)
        with image_label:
            resized_rects = st_img_label(st.session_state['resized_image'], box_color="red", rects=st.session_state['selected_image'].get_resized_rects())
            st.session_state['origin_rects'] = st.session_state['selected_image'].revoke_resized_rect(resized_rects)
            #if len(resized_rects) > 0:
            #    st.session_state['origin_rects'] = st.session_state['selected_image'].revoke_resized_rect(resized_rects)
    else:
        st.session_state['origin_rects'] = []

def fill_color(org_image, rects, color):
    draw = ImageDraw.Draw(org_image)
    for rect in rects:
        crop = [rect['left'], rect['top'], rect['left'] + rect['width'], rect['top'] + rect['height']]
        draw.rectangle(crop, fill=color)

#https://github.com/GoogleCloudPlatform/generative-ai/blob/main/vision/getting-started/image_editing_maskmode.ipynb
with col_right:
    #for generation
    with st.container(border=1):
        cols = st.columns(4)
        language = cols[0].selectbox("Language", LANGUAGE)
        ratio = cols[1].selectbox("Generation Ratio", RATIO)
        model = cols[2].selectbox("Model", GENERATION_MODELS)
        if cols[3].button("Generate image", use_container_width=True):
            with st.spinner("Generating..."):
                st.session_state['generated_image'] = generate_image(model, language, generation_text, negative_text, ratio)
    #for edit
    with st.container(border=1):
        cols = st.columns([2, 2, 1])
        edit_mode = cols[0].selectbox('Edit mode', ("EDIT_MODE_INPAINT_INSERTION", "EDIT_MODE_INPAINT_REMOVAL", "EDIT_MODE_OUTPAINT", "EDIT_MODE_PRODUCT_IMAGE"))
        mask_mode = cols[1].selectbox("Mask mode", ("MASK_MODE_USER_PROVIDED", "MASK_MODE_FOREGROUND", "MASK_MODE_BACKGROUND", "MASK_MODE_SEMANTIC"))
        guidance_scale = cols[2].selectbox("guidance_scale", GUIDANCE_SCALE)
        #if edit_mode == "inpainting-remove":
        #    mask_mode = None
        #if len(guidance_scale) == 0:
        #    guidance_scale = None
        cols = st.columns(2)
        prompt = cols[0].text_input("Edit Prompt", "")
        if len(prompt) == 0:
            prompt = None
        negative_prompt = cols[1].text_input("Edit Negative prompt")
        if len(negative_prompt) == 0:
            negative_prompt = None
    
        cols = st.columns(3)
        base_steps = int(cols[0].text_input("Base steps", BASE_STEPS))
        dilation = float(cols[1].text_input("Dilation", DILATION))
        if st.session_state['selected_image'] != None:
            base_image = st.session_state['selected_image'].get_img()
            if edit_mode == "EDIT_MODE_OUTPAINT":
                outpaint_cols = st.columns(2)
                new_width = int(outpaint_cols[0].text_input("Outpaint width", base_image.width))
                new_height = int(outpaint_cols[1].text_input("Outpaint height", base_image.height))
        if cols[2].button("Edit image", use_container_width=True):
            with st.spinner("Editing..."):
                #By default is mask free mode
                new_base_image = base_image

                #If it is masked rect based edit mode
                if len(st.session_state['origin_rects']) > 0:
                    mask_image = PIL.Image.new("RGBA", (base_image.width, base_image.height), color="black")
                    fill_color(mask_image, st.session_state['origin_rects'], "white")
                    col1, col2 = st.columns(2)
                    col1.image(base_image)
                    col2.image(mask_image)
                
                #If EDIT_MODE_OUTPAINT
                elif edit_mode == "EDIT_MODE_OUTPAINT":
                    mask_image = PIL.Image.new("RGBA", (new_width, new_height), color="white")
                    #black to main image, white to new
                    fill_color(mask_image, [{"left": int(new_width/2 - base_image.width/2), "top": int(new_height/2 - base_image.height/2), 
                                             "width": base_image.width, "height": base_image.height}], "black")
                    new_base_image = mask_image.copy()
                    new_base_image.paste(base_image, (int(new_width/2 - base_image.width/2), int(new_height/2 - base_image.height/2)))
                    col1, col2 = st.columns(2)
                    col1.image(new_base_image)
                    col2.image(mask_image)
                
                st.session_state['generated_image'] = edit_image_mask(EDIT_MODEL, types.Image(image_bytes = get_image_bytes(new_base_image)), 
                                                                     types.Image(image_bytes = get_image_bytes(mask_image)), 
                                                                     language, prompt, negative_prompt, edit_mode, mask_mode, guidance_scale, base_steps, dilation)

    for idx, image in enumerate(st.session_state['generated_image']):
        with st.container(border=1):
            pil_image = image.image._pil_image
            st.image(pil_image)
            st.caption(f"Width: {pil_image.width}, Height: {pil_image.height}")
            cols = st.columns(4)
            cols[0].download_button("Download", data=image.image.image_bytes, file_name="image.png", key=f"download_image_{idx}", use_container_width=True)
            if cols[1].button("Edit", key=f"edit_image_{idx}", use_container_width=True):
                st.session_state['selected_image'] = MemoryImageManager(pil_image, [])
                st.session_state['resized_image'] = st.session_state['selected_image'].resizing_img(MAX_IMAGE_EDIT_SIZE, MAX_IMAGE_EDIT_SIZE)
                st.session_state['origin_rects'] = []
                st.rerun()
            if pil_image.width == pil_image.height == 1024:
                upscale = cols[2].selectbox("Upscale", UPSCALE, key=f"upscale_ratio_{idx}", label_visibility="collapsed")
                if cols[3].button("Upscale", key=f"upscale_image_{idx}", use_container_width=True):
                    st.session_state['generated_image'][idx] = upscale_image(UPSCALE_MODEL, image.image, upscale)
                    st.rerun()