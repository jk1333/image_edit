import streamlit as st
import io
import PIL
from PIL import ImageDraw
from streamlit_img_label import st_img_label
from streamlit_img_label.manage import ImageManager

st.set_page_config(layout='wide')

@st.cache_data
def get_file(filename):
    data = None
    with open(filename, "rb") as file:
        data = file.read()
    return data

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

def localize_objects(image_bytes, lookup):
    print("==========================")
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    rects = []
    match lookup:
        case "text":
            response = client.text_detection(image=image)
            print(response.full_text_annotation)
            texts = response.text_annotations
            for text in texts:
                #print(text)
                rects.append(get_rect_from_vertices(text.bounding_poly.vertices, text.description))
        case "handwriting":
            response = client.document_text_detection(image=image)
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    print(block)
        case "face":
            response = client.face_detection(image=image)
            faces = response.face_annotations
            print("Faces:")
            for face in faces:
                print(face)
        case "label":
            response = client.label_detection(image=image)
            labels = response.label_annotations
            print("Labels:")
            for label in labels:
                print(label)
        case "logo":
            response = client.logo_detection(image=image)
            logos = response.logo_annotations
            for logo in logos:
                print(logo)
        case "landmark":
            response = client.landmark_detection(image=image)
            landmarks = response.landmark_annotations
            for landmark in landmarks:
                print(landmark)
        case "object":
            response = client.object_localization(image=image)
            objects = response.localized_object_annotations
    
    return rects
    #print(f"Number of objects found: {len(objects)}")
    #for object_ in objects:
    #    print(f"\n{object_.name} (confidence: {object_.score})")
    #    print("Normalized bounding polygon vertices: ")
    #    for vertex in object_.bounding_poly.normalized_vertices:
    #        print(f" - ({vertex.x}, {vertex.y})")

class MemoryImageManager(ImageManager):
    def __init__(self, uploaded_file, rects):
        """initiate module"""
        self._filename = "memory"
        self._img = PIL.Image.open(uploaded_file)
        self._rects = rects
        self._resized_ratio_w = 1
        self._resized_ratio_h = 1

import vertexai
from vertexai.preview.vision_models import Image, ImageGenerationModel
def edit_image_mask(
    input_image: Image,
    mask_image: Image,
    prompt: str,
    negative_prompt: str,
    edit_mode: str,
    mask_mode: str,
    guidance_scale: float
) -> vertexai.preview.vision_models.ImageGenerationResponse:
    vertexai.init()
    model = ImageGenerationModel.from_pretrained("imagegeneration@006")
    images = model.edit_image(
        base_image=input_image,
        mask=mask_image,
        prompt=prompt,
        negative_prompt=negative_prompt,
        edit_mode=edit_mode,
        number_of_images=4,
        safety_filter_level="block_few",
        guidance_scale=guidance_scale,
        mask_mode=mask_mode
    )
    return images

col_left, col_right = st.columns(2)

with col_left:
    uploaded_file = st.file_uploader("Choose a image file", type=['png', 'jpg'])
    image_label = st.container()
    col_mode, col_autobutton = st.container(border=1).columns(2)
    option = col_mode.selectbox('Auto detect mode', ("text", "(TBD)handwriting", "(TBD)face", "(TBD)label", "(TBD)logo", "(TBD)landmark", "(TBD)object"))
    if uploaded_file is not None:
        if col_autobutton.button("Auto detect"):
            st.session_state['origin_rects'] = localize_objects(uploaded_file.getvalue(), option)        
        image = MemoryImageManager(uploaded_file, st.session_state['origin_rects'])
        #resized_image = image.resizing_img(max_height=1024, max_width=1024)
        resized_image = image.resizing_img()
        resized_rects = image.get_resized_rects()
        with image_label:
            resized_rects = st_img_label(resized_image, box_color="red", rects=resized_rects)
    else:
        st.session_state['origin_rects'] = []
    st.download_button("Download sample", data=get_file('images.zip'), file_name="images.zip")

def fill_white(org_image, rects):
    draw = ImageDraw.Draw(org_image)
    for rect in rects:
        crop = [rect['left'], rect['top'], rect['left'] + rect['width'], rect['top'] + rect['height']]
        draw.rectangle(crop, fill="white")

#https://github.com/GoogleCloudPlatform/generative-ai/blob/main/vision/getting-started/image_editing_maskmode.ipynb
with col_right:
    cols = st.columns([2, 2, 1])
    edit_mode = cols[0].selectbox('Edit mode', ("inpainting-insert", "inpainting-remove", "outpainting", "product-image"))
    mask_mode = cols[1].selectbox("Mask mode", ("foreground", "background", "semantic"))
    guidance_scale = cols[2].text_input("guidance_scale", 50.0)
    cols = st.columns(2)
    prompt = cols[0].text_input("Prompt", "")
    negative_prompt = cols[1].text_input("Negative prompt")
    if st.button("Generate"):
        with st.spinner("Generating..."):
            if len(resized_rects) > 0:
                mask_image = PIL.Image.new("RGBA", (resized_image.width, resized_image.height), color="black")
                fill_white(mask_image, resized_rects)
                col1, col2 = st.columns(2)
                col1.image(resized_image)
                col2.image(mask_image)
                res = edit_image_mask(Image(get_image_bytes(resized_image)), Image(get_image_bytes(mask_image)), 
                                    prompt, negative_prompt, edit_mode, mask_mode, guidance_scale)
            else:
                res = edit_image_mask(Image(get_image_bytes(resized_image)), None, 
                                    prompt, negative_prompt, edit_mode, mask_mode, guidance_scale)
        #match option:
        #    case "inpainting-insert":
        #        fill_white(resized_image, rects)
        #    case "outpainting":
        #        fill_white(resized_image, rects)
        #    case "inpainting-remove":
        #        fill_white(resized_image, resized_rects)
        #print(f"{resized_image.width}, {resized_image.height}")        
        
        for image in res:
            st.image(image._pil_image)