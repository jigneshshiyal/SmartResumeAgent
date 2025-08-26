import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Login System", page_icon="🔐")

st.title("🔐 FastAPI + Streamlit Login Demo")

menu = ["Home", "Register", "Login", "Upload Resume", "Customize Resume", "View Custom Resumes", "Logout"]
choice = st.sidebar.selectbox("Menu", menu)


if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if choice == "Home":
    if st.session_state.logged_in_user:
        st.success(f"Welcome, {st.session_state.logged_in_user}!")
        if st.button("Logout"):
            st.session_state.logged_in_user = None
            st.info("Logged out successfully")
    else:
        st.warning("Please login or register")

elif choice == "Register":
    st.subheader("Create a New Account")
    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")
    if submit:
        res = requests.post(f"{API_URL}/register", data={"username": username, "password": password})
        if res.status_code == 200:
            st.success("User registered successfully! Please login.")
        else:
            st.error(res.json().get("detail", "Error"))

elif choice == "Login":
    st.subheader("Login to Your Account")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    if submit:
        res = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
        if res.status_code == 200:
            st.session_state.logged_in_user = res.json()["username"]
            st.success(f"Logged in as {st.session_state.logged_in_user}")
            # Redirect to Upload Resume page
            # st.session_state["redirect_page"] = "Upload Resume"
            # st.rerun()
        else:
            st.error(res.json().get("detail", "Login failed"))


# ---- Upload Resume ----
elif choice == "Upload Resume":
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader("Choose a resume (PDF/DOCX)", type=["pdf", "docx"])
    if uploaded_file is not None:
        if st.button("Upload"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            data = {"username": st.session_state.logged_in_user}
            res = requests.post(f"{API_URL}/upload_resume", files=files, data=data)
            if res.status_code == 200:
                st.success("Resume uploaded and processed!")
                st.json(res.json()["extracted_data"])
            else:
                st.error(res.json().get("detail", "Upload failed"))

elif choice == "Customize Resume":
    st.subheader("Customize Resume with Job Post")

    job_post_text = st.text_area("Paste LinkedIn Job Post Text", height=200)

    if st.button("Generate & Save Customized Resume"):
        if not st.session_state.logged_in_user:
            st.error("Please login first.")
        elif not job_post_text:
            st.error("Please provide a job post text.")
        else:
            res = requests.post(
                f"{API_URL}/customize_resume",
                data={"username": st.session_state.logged_in_user, "job_post": job_post_text}
            )

            if res.status_code == 200:
                data = res.json()
                st.success("Customized Resume saved successfully!")
                st.json(data["customized_resume"])
            else:
                st.error(res.json().get("detail", "Error while customizing resume"))


elif choice == "View Custom Resumes":
    st.subheader("Your Customized Resumes")

    if not st.session_state.logged_in_user:
        st.error("Please login first.")
    else:
        res = requests.get(f"{API_URL}/get_customized_resumes", params={"username": st.session_state.logged_in_user})

        if res.status_code == 200:
            customizations = res.json().get("customizations", [])
            if not customizations:
                st.info("No customized resumes found.")
            else:
                for idx, c in enumerate(customizations, start=1):
                    with st.expander(f"Customization #{idx} (ID: {c['id']})"):
                        st.write("**Job Post Used:**")
                        st.text_area("Job Post", c["job_post_text"], height=150)
                        st.write("**Customized Resume JSON:**")
                        st.json(c["customized_data"])
        else:
            st.error(res.json().get("detail", "Error while fetching custom resumes"))


# ---- Logout ----
elif choice == "Logout":
    st.session_state.logged_in_user = None
    st.info("Logged out successfully")