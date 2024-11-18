import streamlit as st
import io
import numpy as np
import PIL, PIL.Image
from PIL import ImageDraw
from streamlit_img_label import st_img_label
from streamlit_img_label.manage import ImageManager
import google.cloud.aiplatform as aip
from vertexai.preview.vision_models import Image, ImageGenerationModel

st.set_page_config(layout='wide')

LANGUAGE = ['auto', 'ko', 'en']
RATIO = ["1:1", "9:16", "16:9", "4:3", "3:4"]
UPSCALE = [2048, 4096]
MAX_IMAGE_EDIT_SIZE = 700
MODELS = ["imagen-3.0-generate-001", "imagen-3.0-fast-generate-001"]

aip.init()

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

def generate_image(model, language, prompt, negative_prompt, ratio, seed = 0):
    model = ImageGenerationModel.from_pretrained(model)
    response = model.generate_images(
        prompt=prompt,
        negative_prompt=negative_prompt,
        # Optional parameters
        number_of_images=4,
        language=language,
        # You can't use a seed value and watermark at the same time.
        add_watermark=True,
        #seed=seed,
        aspect_ratio=ratio,
        safety_filter_level="block_few",
        person_generation="allow_adult",
    )
    return response.images

def upscale_image(image, new_size = 2048):
    model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
    return model.upscale_image(image, new_size)

def edit_image_mask(
    input_image: Image,
    mask_image: Image,
    language = None,
    prompt = None,
    negative_prompt = None,
    edit_mode = None,
    mask_mode = None,
    guidance_scale = None
):
    model = ImageGenerationModel.from_pretrained("imagegeneration@006")
    response = model.edit_image(
        base_image=input_image,
        mask=mask_image,
        prompt=prompt,
        negative_prompt=negative_prompt,
        edit_mode=edit_mode,
        number_of_images=4,
        safety_filter_level="block_few",
        guidance_scale=guidance_scale,
        mask_mode=mask_mode,
        person_generation="allow_adult",
        language = language
    )
    return response.images

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
        model = cols[2].selectbox("Model", MODELS)
        if cols[3].button("Generate image\n\n(Imagen 3)", use_container_width=True):
            with st.spinner("Generating..."):
                st.session_state['generated_image'] = generate_image(model, language, generation_text, negative_text, ratio)
    #for edit
    with st.container(border=1):
        cols = st.columns([2, 2, 1])
        edit_mode = cols[0].selectbox('Edit mode', ("inpainting-insert", "inpainting-remove", "outpainting", "product-image"))
        mask_mode = cols[1].selectbox("Mask mode", ("foreground", "background", "semantic"))
        guidance_scale = cols[2].text_input("guidance_scale", 50.0)
        if edit_mode == "inpainting-remove":
            mask_mode = None
        if len(guidance_scale) == 0:
            guidance_scale = None
        cols = st.columns(2)
        prompt = cols[0].text_input("Edit Prompt", "")
        if len(prompt) == 0:
            prompt = None
        negative_prompt = cols[1].text_input("Edit Negative prompt")
        if len(negative_prompt) == 0:
            negative_prompt = None
    
        cols = st.columns(3)
        if st.session_state['selected_image'] != None:
            base_image = st.session_state['selected_image'].get_img()
            new_width = int(cols[0].text_input("Outpaint width", base_image.width))
            new_height = int(cols[1].text_input("Outpaint height", base_image.height))
            if edit_mode != "outpainting":
                new_width = base_image.width
                new_height = base_image.height
        if cols[2].button("Edit image\n\n(Imagen 2)", use_container_width=True):
            with st.spinner("Editing..."):
                #By default is mask free mode
                mask = None
                new_base_image = base_image

                #If it is masked rect based edit mode
                if len(st.session_state['origin_rects']) > 0:
                    mask_image = PIL.Image.new("RGBA", (base_image.width, base_image.height), color="black")
                    fill_color(mask_image, st.session_state['origin_rects'], "white")
                    col1, col2 = st.columns(2)
                    col1.image(base_image)
                    col2.image(mask_image)
                    mask = Image(get_image_bytes(mask_image))
                
                #If target resolution is changed
                elif (base_image.width != new_width) or (base_image.height != new_height):
                    mask_image = PIL.Image.new("RGBA", (new_width, new_height), color="white")
                    #black to main image, white to new
                    fill_color(mask_image, [{"left": int(new_width/2 - base_image.width/2), "top": int(new_height/2 - base_image.height/2), 
                                             "width": base_image.width, "height": base_image.height}], "black")
                    new_base_image = mask_image.copy()
                    new_base_image.paste(base_image, (int(new_width/2 - base_image.width/2), int(new_height/2 - base_image.height/2)))
                    col1, col2 = st.columns(2)
                    col1.image(new_base_image)
                    col2.image(mask_image)
                    mask = Image(get_image_bytes(mask_image))
                
                st.session_state['generated_image'] = edit_image_mask(Image(get_image_bytes(new_base_image)), 
                                                                     mask, language, prompt, negative_prompt, edit_mode, mask_mode, guidance_scale)

    for idx, image in enumerate(st.session_state['generated_image']):
        with st.container(border=1):
            pil_image = image._pil_image
            st.image(pil_image)
            st.caption(f"Width: {pil_image.width}, Height: {pil_image.height}")
            cols = st.columns(4)
            cols[0].download_button("Download", data=image._image_bytes, file_name="image.png", key=f"download_image_{idx}", use_container_width=True)
            if cols[1].button("Edit", key=f"edit_image_{idx}", use_container_width=True):
                st.session_state['selected_image'] = MemoryImageManager(pil_image, [])
                st.session_state['resized_image'] = st.session_state['selected_image'].resizing_img(MAX_IMAGE_EDIT_SIZE, MAX_IMAGE_EDIT_SIZE)
                st.session_state['origin_rects'] = []
                st.rerun()
            if pil_image.width == pil_image.height == 1024:
                upscale = cols[2].selectbox("Upscale", UPSCALE, key=f"upscale_ratio_{idx}", label_visibility="collapsed")
                if cols[3].button("Upscale", key=f"upscale_image_{idx}", use_container_width=True):
                    st.session_state['generated_image'][idx] = upscale_image(image, upscale)
                    st.rerun()
