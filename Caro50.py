import streamlit as st
import pandas as pd
import os
import zipfile
from datetime import datetime
import random

# Crear carpetas y archivos si no existen
if not os.path.exists("uploads"):
    os.makedirs("uploads")

if not os.path.exists("users.csv"):
    pd.DataFrame(columns=["name"]).to_csv("users.csv", index=False)

if not os.path.exists("photos.csv"):
    pd.DataFrame(columns=["filename", "uploaded_by", "tags"]).to_csv("photos.csv", index=False)

# Cargar datos
users_df = pd.read_csv("users.csv")
photos_df = pd.read_csv("photos.csv")

# Función para registrar usuario
def register_user(name):
    if name not in users_df["name"].values:
        new_user = pd.DataFrame({"name": [name]})
        new_user.to_csv("users.csv", mode="a", header=False, index=False)

# Configuración de la página
st.set_page_config(page_title="Cumple 50 Carolina", page_icon="🎉", layout="centered")

# Título principal
st.title("🎉 ¡Cumpleaños 50 de Carolina! 🎂")

# Mostrar contador de fotos
st.markdown("---")
total_photos = len(photos_df)
st.markdown(f"### 📸 Total de fotos subidas: **{total_photos}**")
st.markdown("---")

# Sesión de usuario
if "user" not in st.session_state:
    st.session_state.user = None

# Login / Registro
if not st.session_state.user:
    st.subheader("Ingresá tu nombre para participar")
    name = st.text_input("Tu nombre")

    if st.button("Entrar"):
        if name:
            register_user(name)
            st.session_state.user = name
            st.success(f"¡Bienvenido/a {name}! 🎉")
            st.rerun()  # Actualiza la página
        else:
            st.error("Por favor, ingresá tu nombre.")
else:
    st.sidebar.success(f"Conectado como {st.session_state.user}")
    menu = st.sidebar.radio("Menú", ["📸 Subir Foto", "🏆 Ver Rankings", "🕁️ Galería", "🔐 Opciones Anfitrión", "🔒 Cerrar Sesión"])

    # Rol especial para "Facu Silva" como anfitrión
    is_host = st.session_state.user.lower() == "facu silva"

    if menu == "📸 Subir Foto":
        st.subheader("📸 Subí una foto divertida")

        option = st.radio("¿Cómo querés subir la foto?", ["Desde archivo", "Sacar foto ahora"])

        if option == "Desde archivo":
            uploaded_file = st.file_uploader("Seleccioná una imagen", type=["jpg", "jpeg", "png"])
        else:
            uploaded_file = st.camera_input("Sacate una foto 📷")

        # Etiquetar usuarios
        others = users_df["name"].tolist()
        tags = st.multiselect("¿Quiénes aparecen en la foto?", others, default=[st.session_state.user])

        if uploaded_file and st.button("Subir"):
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            filepath = os.path.join("uploads", filename)
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Guardar en CSV
            new_photo = pd.DataFrame({
                "filename": [filename],
                "uploaded_by": [st.session_state.user],
                "tags": ["".join(tags)]
            })
            new_photo.to_csv("photos.csv", mode="a", header=False, index=False)

            st.balloons()
            st.success("¡Foto subida con éxito! 🎉")
            st.info(random.choice([ 
                "¡Sos una estrella! ✨", 
                "¡Otra para el álbum! 📸", 
                "¡Esto va a quedar en la historia! 🕺", 
                "¡Sonrían que estamos de fiesta! 😄", 
                "¡Qué momento épico! 🤩"
            ]))
            st.rerun()  # Actualiza la página

    elif menu == "🏆 Ver Rankings":
        st.subheader("🏆 Rankings")

        if not photos_df.empty:
            upload_counts = photos_df["uploaded_by"].value_counts().reset_index()
            upload_counts.columns = ["Usuario", "Fotos Subidas"]

            st.markdown("### 📄 Ranking de Fotos Subidas")
            for idx, row in upload_counts.iterrows():
                medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else ""
                st.write(f"{medal} {row['Usuario']} - {row['Fotos Subidas']} fotos")

            appearance_counts = {}
            for _, row in photos_df.iterrows():
                tags = []
                if not pd.isna(row["tags"]):
                    tags = row["tags"].split(",")
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        appearance_counts[tag] = appearance_counts.get(tag, 0) + 1

            if appearance_counts:
                st.markdown("### 👥 Ranking de Apariciones en Fotos")
                appearance_df = pd.DataFrame(list(appearance_counts.items()), columns=["Usuario", "Apariciones"])
                appearance_df = appearance_df.sort_values(by="Apariciones", ascending=False).reset_index(drop=True)

                for idx, row in appearance_df.iterrows():
                    medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else ""
                    st.write(f"{medal} {row['Usuario']} - {row['Apariciones']} apariciones")
            else:
                st.info("Todavía no hay personas etiquetadas.")

    elif menu == "🕁️ Galería":
        st.subheader("🕁️ Galería de Fotos")
        if not photos_df.empty:
            cols = st.columns(3)
            idx = 0
            for _, row in photos_df.iterrows():
                is_user_tagged = st.session_state.user in row["tags"]
                is_user_uploaded = row["uploaded_by"] == st.session_state.user

                with cols[idx % 3]:
                    # Resaltar si el usuario está etiquetado o subió la foto
                    highlight = "background-color: #FFFF99;" if is_user_tagged else ""
                    highlight += "border: 3px solid green;" if is_user_uploaded else ""
                    st.markdown(f"<div style='{highlight}'>", unsafe_allow_html=True)

                    # Hacer que la foto se pueda abrir en pantalla completa
                    image_url = os.path.join("uploads", row["filename"])
                    st.image(image_url, width=250, use_container_width=True)
                    st.markdown(f"[Ver en pantalla completa](file://{image_url})", unsafe_allow_html=True)
                    
                    st.caption(f"Subida por: **{row['uploaded_by']}**\n\n✨ {random.choice(['Momento único!', 'Fiesta total!', 'Sonrisas y más sonrisas!', 'Para el recuerdo'])}\n\n👥 {row['tags']}")

                    # Botón de descarga individual
                    with open(image_url, "rb") as f:
                        st.download_button(f"Descargar {row['filename']}", f, file_name=row["filename"])

                    st.markdown("</div>", unsafe_allow_html=True)

                idx += 1

            # Opción de descarga en ZIP
            st.markdown("#### 💾 Descargar todas las fotos en un ZIP")
            if st.button("Generar ZIP"):
                zip_filename = "Todas_las_fotos.zip"
                zip_path = os.path.join("uploads", zip_filename)
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file in os.listdir("uploads"):
                        zipf.write(os.path.join("uploads", file), arcname=file)
                with open(zip_path, "rb") as f:
                    st.download_button("Descargar ZIP", f, file_name=zip_filename)
        else:
            st.info("Todavía no hay fotos subidas.")

    elif menu == "🔐 Opciones Anfitrión":
        if is_host:
            st.subheader("🔐 Opciones especiales")

            st.markdown("#### ❌ Eliminar Fotos")
            if not photos_df.empty:
                for idx, row in photos_df.iterrows():
                    st.image(os.path.join("uploads", row["filename"]), width=150)
                    if st.button(f"Eliminar {row['filename']}", key=f"del_{idx}"):
                        os.remove(os.path.join("uploads", row["filename"]))
                        photos_df = photos_df.drop(idx)
                        photos_df.to_csv("photos.csv", index=False)
                        st.success(f"Foto {row['filename']} eliminada.")
                        st.rerun()  # Actualiza la página

            st.markdown("#### 📝 Ver usuarios registrados")
            if not users_df.empty:
                st.write("### Lista de usuarios registrados:")
                for user in users_df["name"]:
                    st.write(user)

                # Eliminar usuario
                user_to_remove = st.selectbox("Seleccioná un usuario para eliminar", users_df["name"].tolist())
                if st.button(f"Eliminar usuario {user_to_remove}"):
                    users_df = users_df[users_df["name"] != user_to_remove]
                    users_df.to_csv("users.csv", index=False)
                    st.success(f"Usuario {user_to_remove} eliminado.")
                    st.rerun()  # Actualiza la página

    elif menu == "🔒 Cerrar Sesión":
        st.session_state.user = None
        st.rerun()  # Actualiza la página
