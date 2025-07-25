import streamlit as st
import fitz
from io import BytesIO
from PIL import Image
import zipfile

# --- Custom CSS for nicer style ---
st.markdown(
    """
    <style>
    /* Header */
    .header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0a66c2;
        margin-bottom: 20px;
    }
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #f5f7fa;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgb(0 0 0 / 0.1);
    }
    /* Main grid */
    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill,minmax(280px,1fr));
        grid-gap: 20px;
        padding-bottom: 50px;
    }
    /* Footer */
    .footer {
        font-size: 0.9rem;
        color: #888;
        text-align: center;
        padding: 20px;
        margin-top: 50px;
        border-top: 1px solid #ddd;
    }
    /* Download button style */
    div.stDownloadButton > button {
        background-color: #0a66c2;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 8px 16px;
        border: none;
        transition: background-color 0.3s ease;
    }
    div.stDownloadButton > button:hover {
        background-color: #004182;
    }
    </style>
    """, unsafe_allow_html=True
)

# Set wide page config
st.set_page_config(page_title="PDF to Image Converter", layout="wide")

# HEADER
st.markdown('<div class="header">📄 PDF to Image Converter</div>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="sidebar">', unsafe_allow_html=True)

    pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])

    if pdf_file is not None:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        total_pages = doc.page_count

        col1, col2 = st.columns(2)
        with col1:
            start_page = st.number_input("Start page", min_value=1, max_value=total_pages, value=1)
        with col2:
            end_page = st.number_input("End page", min_value=1, max_value=total_pages, value=total_pages)

        output_format = st.selectbox("Output image format", ["PNG", "JPEG"])

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        start_page = end_page = output_format = None

# MAIN CONTENT
if pdf_file is not None and start_page <= end_page:
    progress_bar = st.progress(0)
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:

        container = st.container()
        container.markdown('<div class="image-grid">', unsafe_allow_html=True)

        page_indices = range(start_page - 1, end_page)
        for idx, i in enumerate(page_indices):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            img_buffer = BytesIO()
            img.save(img_buffer, format=output_format)
            img_bytes = img_buffer.getvalue()

            # Add image file to ZIP
            zip_file.writestr(f"page_{i + 1}.{output_format.lower()}", img_bytes)

            # Display image and download button in grid cell
            with container.container():
                st.markdown(
                    f"""
                    <div style="border:1px solid #ddd; border-radius:10px; padding:10px; box-shadow: 0 2px 5px rgb(0 0 0 / 0.1); background: white;">
                        <img src="data:image/{output_format.lower()};base64,{img_buffer.getvalue().hex()}" alt="Page {i + 1}" style="width:100%; border-radius: 6px;">
                        <p style="text-align:center; margin: 8px 0 4px;">Page {i + 1}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Streamlit image + download button (fallback to native)
            st.image(img, caption=f"Page {i + 1}", use_container_width=True)
            st.download_button(
                label=f"Download Page {i + 1} as {output_format}",
                data=img_bytes,
                file_name=f"page_{i + 1}.{output_format.lower()}",
                mime=f"image/{output_format.lower()}",
            )

            progress_bar.progress((idx + 1) / len(page_indices))

        container.markdown("</div>", unsafe_allow_html=True)

    progress_bar.empty()
    zip_buffer.seek(0)

    st.download_button(
        label=f"📦 Download ZIP of pages {start_page} to {end_page}",
        data=zip_buffer,
        file_name=f"{pdf_file.name}_pages_{start_page}_to_{end_page}.zip",
        mime="application/zip",
    )
elif pdf_file is not None:
    st.error("❌ Start page must be less or equal to End page")

# FOOTER
st.markdown(
    """
    <div class="footer">
        Developed by YourName — © 2025
    </div>
    """,
    unsafe_allow_html=True,
)
