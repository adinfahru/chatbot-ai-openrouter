import streamlit as st
import requests
import os
import uuid
import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_APIKEY")
default_model = os.getenv("MODEL")
api_url = os.getenv("API_URL")

# Available models with descriptions
MODELS = {
    "DeepSeek Chat v3": {
        "id": "deepseek/deepseek-chat-v3-0324",
        "description": "DeepSeek's flagship chat model, good for general conversation and coding assistance.",
    },
    "DeepSeek R1 (Free)": {
        "id": "deepseek/deepseek-r1:free",
        "description": "Free version of DeepSeek's reasoning-focused model, suitable for complex problem-solving.",
    },
    "Devstral Small (Free)": {
        "id": "mistralai/devstral-small:free",
        "description": "Mistral AI's compact but capable model, good balance of performance and speed.",
    },
    "Llama 3.3 8B Instruct (Free)": {
        "id": "meta-llama/llama-3.3-8b-instruct:free",
        "description": "Meta's Llama 3.3 model optimized for following instructions with impressive capabilities.",
    },
    "Qwen3 8B (Free)": {
        "id": "qwen/qwen3-8b:free",
        "description": "Alibaba's Qwen model featuring strong multilingual capabilities.",
    },
    "Gemma 3 1B IT (Free)": {
        "id": "google/gemma-3-1b-it:free",
        "description": "Google's lightweight model, very fast responses though less capable than larger models.",
    },
}

HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "http://localhost:8501",
    "X-Title": "Chatbot",
}

# --- Initialize session state ---
if "chats" not in st.session_state:
    st.session_state.chats = {}  # Store multiple chat histories

if "current_chat_id" not in st.session_state:
    # Create a first chat
    new_chat_id = str(uuid.uuid4())
    st.session_state.chats[new_chat_id] = {
        "title": "New conversation",
        "messages": [],
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "model": list(MODELS.keys())[0],  # Default model
    }
    st.session_state.current_chat_id = new_chat_id

# --- UI STREAMLIT ---
st.set_page_config(
    page_title="AI Assistant Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)



# --- LEFT SIDEBAR FOR CHAT HISTORY ---
with st.sidebar:
    st.markdown(
        '<div class="sidebar-title"><h2>💬 Chat History</h2></div>',
        unsafe_allow_html=True,
    )

    # New chat button
    if st.button("➕ New Chat", type="primary", use_container_width=True):
        new_chat_id = str(uuid.uuid4())
        st.session_state.chats[new_chat_id] = {
            "title": "New conversation",
            "messages": [],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "model": list(MODELS.keys())[0],  # Default model
        }
        st.session_state.current_chat_id = new_chat_id
        st.rerun()

    st.markdown("---")

    # Display chat history
    for chat_id, chat_data in sorted(
        st.session_state.chats.items(), key=lambda x: x[1]["created_at"], reverse=True
    ):
        # Generate a short title from the first user message if available
        chat_title = chat_data["title"]
        if chat_data["messages"] and chat_title == "New conversation":
            first_msg = chat_data["messages"][0]["content"]
            chat_data["title"] = (
                first_msg[:25] + "..." if len(first_msg) > 25 else first_msg
            )

        # Determine if this is the active chat
        is_active = chat_id == st.session_state.current_chat_id
        active_class = "active" if is_active else ""

        # Create a clickable div for each chat
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                f"📝 {chat_data['title']}",
                key=f"chat_{chat_id}",
                use_container_width=True,
                type="secondary" if is_active else "tertiary",
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}", help="Delete this conversation"):
                del st.session_state.chats[chat_id]
                if chat_id == st.session_state.current_chat_id:
                    # If we deleted the current chat, switch to another one or create new
                    if st.session_state.chats:
                        st.session_state.current_chat_id = list(
                            st.session_state.chats.keys()
                        )[0]
                    else:
                        new_chat_id = str(uuid.uuid4())
                        st.session_state.chats[new_chat_id] = {
                            "title": "New conversation",
                            "messages": [],
                            "created_at": datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                            "model": list(MODELS.keys())[0],
                        }
                        st.session_state.current_chat_id = new_chat_id
                st.rerun()

        # Add timestamp under each chat entry
        st.caption(f"{chat_data['created_at']} | Model: {chat_data['model'][:15]}...")


# --- MAIN CONTENT AREA ---
# Get the current chat data
current_chat = st.session_state.chats[st.session_state.current_chat_id]
current_messages = current_chat["messages"]
current_model = current_chat["model"]

# Create a three-column layout: chat area and model selection
chat_col, model_col = st.columns([3, 1])

with chat_col:
    st.title("🤖 AI Assistant Chat")
    st.markdown(
        """
        Welcome to the AI Assistant Chat! Ask any question and get answers from various AI models.
        """
    )

    # Display chat history in the main area
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    if not current_messages:
        st.markdown("_Start a conversation by sending a message below!_")

    for idx, msg in enumerate(current_messages):
        with st.chat_message(
            msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"
        ):
            st.write(msg["content"])

            # Add a small label showing which model answered (for assistant messages)
            if msg["role"] == "assistant" and "model_used" in msg:
                st.caption(f"Answered by: {msg['model_used']}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Input box for user messages
    user_input = st.chat_input(
        "Ask anything...", key=f"user_input_{st.session_state.current_chat_id}"
    )

    if user_input:
        # Update chat title if this is the first message
        if not current_messages:
            current_chat["title"] = (
                user_input[:25] + "..." if len(user_input) > 25 else user_input
            )

        # Display user input
        with st.chat_message("user", avatar="🧑‍💻"):
            st.write(user_input)

        # Get the selected model
        selected_model_name = current_chat["model"]
        selected_model_id = MODELS[selected_model_name]["id"]

        # Add to messages
        current_messages.append({"role": "user", "content": user_input})

        # API call
        with st.spinner("The AI is thinking..."):
            payload = {
                "model": selected_model_id,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful, friendly assistant. Provide accurate and thoughtful responses.",
                    },
                    *[
                        {"role": m["role"], "content": m["content"]}
                        for m in current_messages
                    ],
                ],
            }

            try:
                response = requests.post(api_url, headers=HEADERS, json=payload)
                response.raise_for_status()
                answer = response.json()["choices"][0]["message"]["content"]

                # Display assistant response
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(answer)
                    st.caption(f"Answered by: {selected_model_name}")

                # Add to messages
                current_messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "model_used": selected_model_name,
                    }
                )

                # Force a rerun to update the UI
                st.rerun()

            except Exception as e:
                st.error(f"Error getting response: {str(e)}")
                st.error("Please try again or select a different model.")

# --- MODEL SELECTION COLUMN ---
with model_col:
    st.header("🧠 Model Selection")
    st.markdown("Select the AI model you want to use:")

    selected_model_name = st.selectbox(
        "Choose model:",
        options=list(MODELS.keys()),
        index=(
            list(MODELS.keys()).index(current_chat["model"])
            if current_chat["model"] in MODELS
            else 0
        ),
        key=f"model_select_{st.session_state.current_chat_id}",
    )

    # Update the current chat's model when changed
    if selected_model_name != current_chat["model"]:
        current_chat["model"] = selected_model_name

    # Display model information
    st.markdown("### Model Details")
    st.markdown(
        f"""
        <div class="model-card">
            <div class="model-name">{selected_model_name}</div>
            <div><code>{MODELS[selected_model_name]["id"]}</code></div>
            <div>{MODELS[selected_model_name]["description"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Add usage tips
    st.markdown("### Usage Tips")
    st.markdown(
        """
        - Be specific in your questions
        - For coding help, describe what you're trying to achieve
        - Try different models for different types of questions
        """
    )

    st.markdown("---")
    st.markdown("Powered by [OpenRouter](https://openrouter.ai)")
    st.markdown("v1.0.0 | Made with Streamlit")
