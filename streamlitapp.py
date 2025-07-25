import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
from PIL import Image
import zipfile

st.set_page_config(page_title="PDF to Image Converter", layout="wide")
st.title("📄 PDF to Image Converter (No Poppler Needed)")

pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if pdf_file is not None:
    pdf_name = pdf_file.name
    st.write(f"**File name:** {pdf_name}")

    with st.spinner("Processing PDF, please wait..."):
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        total_pages = doc.page_count
        st.success(f"✅ Total pages detected: {total_pages}")

    # Chọn trang bắt đầu và kết thúc (1-based)
    start_page = st.number_input("Start page", min_value=1, max_value=total_pages, value=1)
    end_page = st.number_input("End page", min_value=1, max_value=total_pages, value=total_pages)

    if start_page > end_page:
        st.error("Start page must be less or equal to End page")
    else:
        output_format = st.selectbox("Select output image format", ["PNG", "JPEG"])
        progress_bar = st.progress(0)

        # Nút download ZIP
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:

            for i in range(start_page - 1, end_page):
                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                st.image(img, caption=f"📄 Page {i + 1}", use_container_width=True)

                img_buffer = BytesIO()
                img.save(img_buffer, format=output_format)
                img_bytes = img_buffer.getvalue()

                # Thêm file vào zip
                zip_file.writestr(f"page_{i + 1}.{output_format.lower()}", img_bytes)

                # Tạo nút download cho từng trang
                st.download_button(
                    label=f"⬇️ Download Page {i + 1} as {output_format}",
                    data=img_bytes,
                    file_name=f"page_{i + 1}.{output_format.lower()}",
                    mime=f"image/{output_format.lower()}",
                )

                progress_bar.progress((i - (start_page - 1) + 1) / (end_page - start_page + 1))

        progress_bar.empty()

        # Hiển thị nút download ZIP
        zip_buffer.seek(0)
        st.download_button(
            label=f"📦 Download ZIP of pages {start_page} to {end_page}",
            data=zip_buffer,
            file_name=f"{pdf_name}_pages_{start_page}_to_{end_page}.zip",
            mime="application/zip",
        )
