import streamlit as st
from pdf2image import convert_from_bytes
from io import BytesIO

# Đường dẫn poppler trên máy bạn (đổi cho đúng)
POPPLER_PATH = r"C:\Users\FTC-User\Desktop\Training\Phase 01\Software\Release-24.08.0-0\poppler-24.08.0\Library\bin"

st.title("PDF to Image Converter")

pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if pdf_file is not None:
    with st.spinner('Processing PDF, please wait...'):
        # Chuyển PDF sang ảnh với DPI cao
        pages = convert_from_bytes(pdf_file.read(), dpi=300, poppler_path=POPPLER_PATH)

    total_pages = len(pages)
    st.write(f"Total pages: {total_pages}")

    output_format = st.selectbox("Select output image format", ["PNG", "JPEG"])

    progress_bar = st.progress(0)

    for page_number, page_image in enumerate(pages, start=1):
        st.image(page_image, caption=f"Page {page_number}", use_container_width=True)

        img_buffer = BytesIO()
        page_image.save(img_buffer, format=output_format)
        img_bytes = img_buffer.getvalue()

        st.download_button(
            label=f"Download Page {page_number} as {output_format}",
            data=img_bytes,
            file_name=f"page_{page_number}.{output_format.lower()}",
            mime=f"image/{output_format.lower()}",
        )

        progress_bar.progress(page_number / total_pages)

    progress_bar.empty()
